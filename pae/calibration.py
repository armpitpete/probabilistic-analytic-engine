"""Balanced resolved-case calibration and external-review controls."""
from __future__ import annotations
import argparse, json, math, sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from .acquisition import AcquisitionError

VERSION="0.1"
CLASSES=("positive","negative","disputed","insufficient")
UNIFORM_P=1/4
UNIFORM_BRIER=.75
UNIFORM_LOG=math.log(4)
FIXED_THRESHOLDS={
 "minimum_brier_improvement":.10,
 "minimum_log_improvement":.15,
 "minimum_top_one_accuracy":.50,
 "maximum_expected_calibration_error":.20,
 "minimum_correct_per_outcome_class":1,
 "minimum_external_reviewers":2,
}

def _s(d,k,c):
 v=d.get(k)
 if not isinstance(v,str) or not v.strip(): raise AcquisitionError(f"{c}: {k} must be a non-empty string")
 return v.strip()

def _sl(d,k,c):
 v=d.get(k)
 if not isinstance(v,list) or not v or any(not isinstance(x,str) or not x.strip() for x in v):
  raise AcquisitionError(f"{c}: {k} must be a non-empty list of strings")
 return [x.strip() for x in v]

def _d(v,c):
 try:return date.fromisoformat(v)
 except ValueError as e: raise AcquisitionError(f"{c}: must be an ISO date") from e

def _dt(v,c):
 try:r=datetime.fromisoformat(v.replace("Z","+00:00"))
 except ValueError as e: raise AcquisitionError(f"{c}: must be an ISO-8601 datetime") from e
 if r.tzinfo is None: raise AcquisitionError(f"{c}: timezone is required")
 return r

def _p(v,c):
 if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)) or not 0<=float(v)<=1:
  raise AcquisitionError(f"{c}: must be a number from 0 to 1")
 return float(v)

def validate_manifest(m:Any)->dict[str,Any]:
 if not isinstance(m,dict): raise AcquisitionError("calibration manifest must be an object")
 if _s(m,"calibration_version","manifest")!=VERSION: raise AcquisitionError("manifest: unsupported calibration_version")
 _s(m,"programme_id","manifest"); _s(m,"authority_base_sha","manifest"); _dt(_s(m,"frozen_at","manifest"),"manifest frozen_at")
 if m.get("outcome_classes")!=list(CLASSES): raise AcquisitionError("manifest: outcome_classes must exactly match the fixed four-class order")
 t=m.get("thresholds")
 if not isinstance(t,dict): raise AcquisitionError("manifest: thresholds must be an object")
 for k,v in FIXED_THRESHOLDS.items():
  if t.get(k)!=v: raise AcquisitionError(f"manifest thresholds.{k} must remain predeclared as {v}")
 cases=m.get("cases")
 if not isinstance(cases,list) or len(cases)!=8: raise AcquisitionError("manifest: cases must contain exactly eight records")
 ids=set(); counts=Counter(); urls=set()
 for i,case in enumerate(cases,1):
  c=f"manifest cases[{i}]"
  if not isinstance(case,dict): raise AcquisitionError(f"{c}: must be an object")
  cid=_s(case,"id",c)
  if cid in ids: raise AcquisitionError(f"{c}: duplicate id {cid!r}")
  ids.add(cid); _s(case,"title",c)
  oc=_s(case,"outcome_class",c)
  if oc not in CLASSES: raise AcquisitionError(f"{c}: unsupported outcome_class")
  counts[oc]+=1; cutoff=_d(_s(case,"evidence_cutoff",c),f"{c} cutoff")
  if "?" not in _s(case,"question",c): raise AcquisitionError(f"{c}: question must be explicit")
  _s(case,"resolution_standard",c); _s(case,"outcome_rationale",c)
  if _s(case,"packet_status",c) not in {"predeclared","packet_ready","externally_reviewed"}: raise AcquisitionError(f"{c}: unsupported packet_status")
  ev=case.get("evidence_source_registry"); out=case.get("withheld_outcome_sources")
  if not isinstance(ev,list) or not ev: raise AcquisitionError(f"{c}: evidence_source_registry is required")
  if not isinstance(out,list) or not out: raise AcquisitionError(f"{c}: withheld_outcome_sources is required")
  for j,src in enumerate(ev,1):
   sc=f"{c} evidence_source_registry[{j}]"
   if not isinstance(src,dict): raise AcquisitionError(f"{sc}: must be an object")
   if _d(_s(src,"date",sc),sc)>cutoff: raise AcquisitionError(f"{sc}: evidence source is after the cutoff")
   u=_s(src,"url",sc); _s(src,"institution",sc); _s(src,"title",sc)
   if u in urls and src.get("cross_case_reuse_declared") is not True: raise AcquisitionError(f"{sc}: reused URL requires cross_case_reuse_declared")
   urls.add(u)
  for j,src in enumerate(out,1):
   sc=f"{c} withheld_outcome_sources[{j}]"
   if not isinstance(src,dict): raise AcquisitionError(f"{sc}: must be an object")
   if _d(_s(src,"date",sc),sc)<=cutoff: raise AcquisitionError(f"{sc}: outcome source must be after the cutoff")
   _s(src,"url",sc); _s(src,"institution",sc); _s(src,"title",sc)
 if counts!=Counter({x:2 for x in CLASSES}): raise AcquisitionError("manifest: corpus must contain exactly two cases in each outcome class")
 er=m.get("external_review")
 if not isinstance(er,dict): raise AcquisitionError("manifest: external_review must be an object")
 if er.get("self_certification_prohibited") is not True: raise AcquisitionError("manifest: external review self-certification must be prohibited")
 if er.get("minimum_reviewers")!=2: raise AcquisitionError("manifest: minimum_reviewers must equal 2")
 _sl(er,"required_declarations","manifest external_review"); _sl(er,"critical_finding_types","manifest external_review")
 return {"case_ids":ids,"class_counts":dict(counts),"thresholds":t}

def build_blinded_review_packet(m:Any)->dict[str,Any]:
 validate_manifest(m)
 return {"calibration_version":VERSION,"programme_id":m["programme_id"],"review_mode":"external_outcome_blinded",
  "cases":[{k:c[k] for k in ("id","title","question","evidence_cutoff","resolution_standard","packet_status","evidence_source_registry")} for c in m["cases"]],
  "required_reviewer_declarations":m["external_review"]["required_declarations"],
  "prohibited_material":["resolved outcome class","withheld outcome sources","outcome rationale","aggregate scores from other reviewers"],
  "warning":"Reviewers must not seek outcome material until their signed blinded review is frozen."}

def _reviews(rows,case_ids,minimum):
 if not isinstance(rows,list): raise AcquisitionError("aggregate: external_reviews must be a list")
 by=defaultdict(list); seen=set()
 for i,r in enumerate(rows,1):
  c=f"external_reviews[{i}]"
  if not isinstance(r,dict): raise AcquisitionError(f"{c}: must be an object")
  cid=_s(r,"case_id",c); rid=_s(r,"reviewer_id",c)
  if cid not in case_ids: raise AcquisitionError(f"{c}: unknown case_id")
  if (cid,rid) in seen: raise AcquisitionError(f"{c}: duplicate reviewer for case")
  seen.add((cid,rid))
  if r.get("independent") is not True: raise AcquisitionError(f"{c}: reviewer must declare independence")
  if r.get("conflict_of_interest") is not False: raise AcquisitionError(f"{c}: conflict_of_interest must be false")
  if r.get("outcome_blinded_during_review") is not True: raise AcquisitionError(f"{c}: outcome blinding must be confirmed")
  if r.get("not_involved_in_case_preparation") is not True: raise AcquisitionError(f"{c}: reviewer must not have prepared the case or calculation")
  _s(r,"affiliation",c); _s(r,"expertise",c); _s(r,"reviewer_signature",c)
  if _s(r,"decision",c) not in {"accept","accept_with_minor_comments","reject"}: raise AcquisitionError(f"{c}: unsupported decision")
  fs=r.get("findings")
  if not isinstance(fs,list): raise AcquisitionError(f"{c}: findings must be a list")
  for j,f in enumerate(fs,1):
   fc=f"{c} findings[{j}]"
   if not isinstance(f,dict) or _s(f,"severity",fc) not in {"minor","major","critical"}: raise AcquisitionError(f"{fc}: unsupported severity")
   _s(f,"finding",fc)
  _dt(_s(r,"reviewed_at",c),f"{c} reviewed_at"); by[cid].append(r)
 for cid in case_ids:
  if len(by[cid])<minimum: raise AcquisitionError(f"external_reviews: case {cid!r} has fewer than {minimum} reviewers")
 return by

def _auc(rows):
 pos=sum(y for _,y in rows); neg=len(rows)-pos
 if not pos or not neg:return None
 rows=sorted(rows); rank_sum=0.; i=0
 while i<len(rows):
  j=i+1
  while j<len(rows) and rows[j][0]==rows[i][0]:j+=1
  rank_sum+=((i+1+j)/2)*sum(y for _,y in rows[i:j]); i=j
 return (rank_sum-pos*(pos+1)/2)/(pos*neg)

def _ece(rows):
 total=len(rows); value=0.
 for lo,hi in ((0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.0000001)):
  b=[r for r in rows if lo<=r["confidence"]<hi]
  if b:value+=len(b)/total*abs(sum(r["correct"] for r in b)/len(b)-sum(r["confidence"] for r in b)/len(b))
 return value

def aggregate_calibration(m:Any,b:Any)->dict[str,Any]:
 info=validate_manifest(m)
 if not isinstance(b,dict) or b.get("calibration_version")!=VERSION: raise AcquisitionError("aggregate: unsupported calibration_version")
 results=b.get("case_results")
 if not isinstance(results,list) or len(results)!=8: raise AcquisitionError("aggregate: case_results must contain exactly eight records")
 cases={c["id"]:c for c in m["cases"]}; seen=set(); per=[]; bins=[]; correct=Counter(); validated=[]
 for i,r in enumerate(results,1):
  c=f"case_results[{i}]"
  if not isinstance(r,dict): raise AcquisitionError(f"{c}: must be an object")
  cid=_s(r,"case_id",c)
  if cid not in cases or cid in seen: raise AcquisitionError(f"{c}: unknown or duplicate case_id")
  seen.add(cid); expected=cases[cid]["outcome_class"]
  if _s(r,"resolved_outcome_class",c)!=expected: raise AcquisitionError(f"{c}: outcome class differs from frozen manifest")
  if r.get("outcome_leakage_detected") is not False: raise AcquisitionError(f"{c}: outcome leakage detected or not cleared")
  ps=r.get("probabilities")
  if not isinstance(ps,dict) or set(ps)!=set(CLASSES): raise AcquisitionError(f"{c}: probabilities must exactly match outcome classes")
  p={x:_p(ps[x],f"{c} probabilities.{x}") for x in CLASSES}
  if not math.isclose(sum(p.values()),1,abs_tol=1e-9): raise AcquisitionError(f"{c}: probabilities must total 1")
  if p[expected]<=0: raise AcquisitionError(f"{c}: resolved probability must be positive")
  lead=max(CLASSES,key=p.get); hit=lead==expected; correct[expected]+=int(hit)
  br=sum((v-(1 if x==expected else 0))**2 for x,v in p.items()); lg=-math.log(p[expected])
  per.append({"case_id":cid,"outcome_class":expected,"leading_class":lead,"correct":hit,"resolved_probability":p[expected],"brier_score":br,"logarithmic_score":lg})
  bins.append({"confidence":max(p.values()),"correct":int(hit)}); validated.append((cid,p))
 if seen!=info["case_ids"]: raise AcquisitionError("aggregate: case_results do not match frozen corpus")
 reviews=_reviews(b.get("external_reviews"),info["case_ids"],m["external_review"]["minimum_reviewers"])
 critical=[]; major=[]; rejected=[]
 for cid,rs in reviews.items():
  for r in rs:
   if r["decision"]=="reject": rejected.append({"case_id":cid,"reviewer_id":r["reviewer_id"]})
   for f in r["findings"]:
    row={"case_id":cid,"reviewer_id":r["reviewer_id"],"finding":f["finding"]}
    if f["severity"]=="critical":critical.append(row)
    elif f["severity"]=="major":major.append(row)
 mb=sum(x["brier_score"] for x in per)/8; ml=sum(x["logarithmic_score"] for x in per)/8; top=sum(x["correct"] for x in per)/8; ece=_ece(bins)
 aucs={x:_auc([(p[x],1 if cases[cid]["outcome_class"]==x else 0) for cid,p in validated]) for x in CLASSES}; macro=sum(aucs.values())/4
 stop=[]; correction=[]
 if mb>=UNIFORM_BRIER or ml>=UNIFORM_LOG:stop.append("aggregate performance is not better than the uniform baseline")
 if critical:stop.append("external review contains a critical finding")
 if rejected:stop.append("one or more external reviewers rejected a case packet")
 t=info["thresholds"]
 if UNIFORM_BRIER-mb<t["minimum_brier_improvement"]:correction.append("Brier improvement misses the predeclared threshold")
 if UNIFORM_LOG-ml<t["minimum_log_improvement"]:correction.append("log-score improvement misses the predeclared threshold")
 if top<t["minimum_top_one_accuracy"]:correction.append("top-one accuracy misses the predeclared threshold")
 if ece>t["maximum_expected_calibration_error"]:correction.append("expected calibration error exceeds the threshold")
 missing=[x for x in CLASSES if correct[x]<t["minimum_correct_per_outcome_class"]]
 if missing:correction.append("no correct leading classification in: "+", ".join(missing))
 if major:correction.append("external review contains one or more major findings")
 decision="stop" if stop else "correction_required" if correction else "pass_candidate"
 loo=[]
 for omitted in per:
  rem=[x for x in per if x["case_id"]!=omitted["case_id"]]
  loo.append({"omitted_case_id":omitted["case_id"],"mean_brier_score":sum(x["brier_score"] for x in rem)/7,"mean_logarithmic_score":sum(x["logarithmic_score"] for x in rem)/7,"top_one_accuracy":sum(x["correct"] for x in rem)/7})
 return {"calibration_version":VERSION,"programme_id":m["programme_id"],"case_count":8,"class_counts":info["class_counts"],
  "uniform_baseline":{"brier_score":UNIFORM_BRIER,"logarithmic_score":UNIFORM_LOG,"top_one_accuracy":UNIFORM_P},
  "aggregate":{"mean_brier_score":mb,"brier_improvement_over_uniform":UNIFORM_BRIER-mb,"mean_logarithmic_score":ml,"log_improvement_over_uniform":UNIFORM_LOG-ml,"top_one_accuracy":top,"expected_calibration_error":ece,"one_vs_rest_auc":aucs,"macro_auc":macro,"correct_by_outcome_class":dict(correct)},
  "per_case":sorted(per,key=lambda x:x["case_id"]),"leave_one_case_out":sorted(loo,key=lambda x:x["omitted_case_id"]),
  "external_review":{"review_count":sum(map(len,reviews.values())),"critical_findings":critical,"major_findings":major,"rejected_reviews":rejected,"independent_external_review_completed":True},
  "decision":decision,"stop_reasons":stop,"correction_reasons":correction,"live_use_authorised":False,
  "warning":"A pass candidate still requires explicit human acceptance and never automatically authorises live use."}

def _load(p):return json.loads(p.read_text(encoding="utf-8"))
def parser():
 p=argparse.ArgumentParser(description="Validate or score a PAE calibration corpus."); sub=p.add_subparsers(dest="command",required=True)
 for name in ("validate-manifest","prepare-review"):
  q=sub.add_parser(name); q.add_argument("manifest",type=Path); q.add_argument("--output",type=Path)
 q=sub.add_parser("aggregate"); q.add_argument("manifest",type=Path); q.add_argument("results",type=Path); q.add_argument("--output",type=Path)
 return p
def main(argv=None):
 a=parser().parse_args(argv)
 try:
  r=validate_manifest(_load(a.manifest)) if a.command=="validate-manifest" else build_blinded_review_packet(_load(a.manifest)) if a.command=="prepare-review" else aggregate_calibration(_load(a.manifest),_load(a.results))
  text=json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
  if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding="utf-8")
  else:print(text,end="")
 except (OSError,json.JSONDecodeError,AcquisitionError) as e:print(f"PAE calibration failed: {e}",file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
