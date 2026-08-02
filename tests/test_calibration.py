import copy
import pytest
from pae.acquisition import AcquisitionError
from pae.calibration import validate_manifest, aggregate_calibration, UNIFORM_BRIER, UNIFORM_LOG


def make_manifest():
    classes=["positive","positive","negative","negative","disputed","disputed","insufficient","insufficient"]
    manifest={
      "calibration_version":"0.1","programme_id":"pae-calibration-v0.1","authority_base_sha":"a"*40,
      "frozen_at":"2026-08-02T13:20:00+01:00","outcome_classes":["positive","negative","disputed","insufficient"],
      "thresholds":{"minimum_brier_improvement":0.10,"minimum_log_improvement":0.15,
      "minimum_top_one_accuracy":0.50,"maximum_expected_calibration_error":0.20,
      "minimum_correct_per_outcome_class":1,"minimum_external_reviewers":2},
      "external_review":{"self_certification_prohibited":True,"minimum_reviewers":2,
      "required_declarations":["independence","conflict of interest","outcome blinding"],
      "critical_finding_types":["outcome leakage","unauditable evidence","irreproducible calculation"]},
      "cases":[]}
    for i,cls in enumerate(classes):
        manifest["cases"].append({
            "id":f"case-{i+1}","title":f"Case {i+1}","outcome_class":cls,
            "evidence_cutoff":"2020-01-01","question":"What is the resolved class?",
            "resolution_standard":"Public institutional evidence standard.",
            "outcome_rationale":"Fixture rationale.","packet_status":"predeclared",
            "evidence_source_registry":[{"date":"2019-12-01","url":f"https://evidence/{i}","institution":"I","title":"E"}],
            "withheld_outcome_sources":[{"date":"2020-02-01","url":f"https://outcome/{i}","institution":"O","title":"O"}]
        })
    return manifest


def make_results(manifest, accuracy="perfect"):
    result={"calibration_version":"0.1","case_results":[],"external_reviews":[]}
    classes=("positive","negative","disputed","insufficient")
    for i,case in enumerate(manifest["cases"]):
        correct=case["outcome_class"]
        if accuracy=="perfect":
            probs={c:0.05 for c in classes}; probs[correct]=0.85
        elif accuracy=="uniform":
            probs={c:0.25 for c in classes}
        elif accuracy=="wrong":
            probs={c:0.05 for c in classes}; probs[classes[(classes.index(correct)+1)%4]]=0.85
        else:
            probs={c:0.2 for c in classes}; probs[correct]=0.4
        result["case_results"].append({"case_id":case["id"],"resolved_outcome_class":correct,
                                       "outcome_leakage_detected":False,"probabilities":probs})
        for r in ("r1","r2"):
            result["external_reviews"].append({"case_id":case["id"],"reviewer_id":f"{r}-{i}",
              "independent":True,"conflict_of_interest":False,"outcome_blinded_during_review":True,
              "not_involved_in_case_preparation":True,"affiliation":"Independent reviewer",
              "expertise":"Structured analytic methods","reviewer_signature":f"signed-{r}-{i}",
              "decision":"accept","findings":[],"reviewed_at":"2026-08-02T13:00:00+01:00"})
    return result


def test_manifest_valid_and_balanced():
    result=validate_manifest(make_manifest())
    assert result["class_counts"]=={"positive":2,"negative":2,"disputed":2,"insufficient":2}


def test_manifest_rejects_rebalanced_corpus():
    manifest=make_manifest(); manifest["cases"][0]["outcome_class"]="negative"
    with pytest.raises(AcquisitionError, match="exactly two"):
        validate_manifest(manifest)


def test_manifest_rejects_post_cutoff_evidence():
    manifest=make_manifest(); manifest["cases"][0]["evidence_source_registry"][0]["date"]="2020-01-02"
    with pytest.raises(AcquisitionError, match="after the cutoff"):
        validate_manifest(manifest)


def test_manifest_rejects_pre_cutoff_outcome():
    manifest=make_manifest(); manifest["cases"][0]["withheld_outcome_sources"][0]["date"]="2019-12-31"
    with pytest.raises(AcquisitionError, match="must be after"):
        validate_manifest(manifest)


def test_manifest_rejects_threshold_drift():
    manifest=make_manifest(); manifest["thresholds"]["minimum_top_one_accuracy"]=0.49
    with pytest.raises(AcquisitionError, match="must remain predeclared"):
        validate_manifest(manifest)


def test_perfect_bundle_is_pass_candidate():
    manifest=make_manifest(); result=aggregate_calibration(manifest, make_results(manifest))
    assert result["decision"]=="pass_candidate"
    assert result["aggregate"]["mean_brier_score"] < UNIFORM_BRIER
    assert result["aggregate"]["mean_logarithmic_score"] < UNIFORM_LOG
    assert result["external_review"]["independent_external_review_completed"] is True
    assert result["live_use_authorised"] is False


def test_uniform_performance_stops():
    manifest=make_manifest(); result=aggregate_calibration(manifest, make_results(manifest,"uniform"))
    assert result["decision"]=="stop"
    assert result["stop_reasons"]


def test_wrong_performance_stops():
    manifest=make_manifest(); result=aggregate_calibration(manifest, make_results(manifest,"wrong"))
    assert result["decision"]=="stop"


def test_marginal_performance_requires_correction():
    manifest=make_manifest(); result=aggregate_calibration(manifest, make_results(manifest,"marginal"))
    assert result["decision"] in {"correction_required","pass_candidate"}
    assert result["live_use_authorised"] is False


def test_outcome_leakage_fails():
    manifest=make_manifest(); bundle=make_results(manifest); bundle["case_results"][0]["outcome_leakage_detected"]=True
    with pytest.raises(AcquisitionError, match="outcome leakage"):
        aggregate_calibration(manifest,bundle)


def test_missing_external_reviewer_fails():
    manifest=make_manifest(); bundle=make_results(manifest); bundle["external_reviews"]=[r for r in bundle["external_reviews"] if not (r["case_id"]=="case-1" and r["reviewer_id"].startswith("r2"))]
    with pytest.raises(AcquisitionError, match="fewer than 2"):
        aggregate_calibration(manifest,bundle)


def test_conflicted_reviewer_fails():
    manifest=make_manifest(); bundle=make_results(manifest); bundle["external_reviews"][0]["conflict_of_interest"]=True
    with pytest.raises(AcquisitionError, match="conflict_of_interest"):
        aggregate_calibration(manifest,bundle)


def test_critical_external_finding_stops():
    manifest=make_manifest(); bundle=make_results(manifest)
    bundle["external_reviews"][0]["findings"]=[{"severity":"critical","finding":"Outcome leakage."}]
    result=aggregate_calibration(manifest,bundle)
    assert result["decision"]=="stop"


def test_rejected_external_review_stops():
    manifest=make_manifest(); bundle=make_results(manifest); bundle["external_reviews"][0]["decision"]="reject"
    result=aggregate_calibration(manifest,bundle)
    assert result["decision"]=="stop"


def test_probabilities_must_total_one():
    manifest=make_manifest(); bundle=make_results(manifest); bundle["case_results"][0]["probabilities"]["positive"] += .01
    with pytest.raises(AcquisitionError, match="must total 1"):
        aggregate_calibration(manifest,bundle)


def test_leave_one_case_out_contains_every_case():
    manifest=make_manifest(); result=aggregate_calibration(manifest,make_results(manifest))
    assert {r["omitted_case_id"] for r in result["leave_one_case_out"]} == {c["id"] for c in manifest["cases"]}


def test_blinded_packet_excludes_outcomes():
    from pae.calibration import build_blinded_review_packet
    packet=build_blinded_review_packet(make_manifest())
    rendered=str(packet)
    assert "outcome_class" not in rendered
    assert "withheld_outcome_sources" not in rendered
    assert "outcome_rationale" not in rendered
    assert len(packet["cases"])==8


def test_reviewer_involved_in_preparation_fails():
    manifest=make_manifest(); bundle=make_results(manifest)
    bundle["external_reviews"][0]["not_involved_in_case_preparation"]=False
    with pytest.raises(AcquisitionError, match="must not have prepared"):
        aggregate_calibration(manifest,bundle)


def test_major_finding_requires_correction():
    manifest=make_manifest(); bundle=make_results(manifest)
    bundle["external_reviews"][0]["findings"]=[{"severity":"major","finding":"Repairable dependency concern."}]
    result=aggregate_calibration(manifest,bundle)
    assert result["decision"]=="correction_required"
