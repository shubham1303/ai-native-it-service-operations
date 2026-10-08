"""Persist explicit model-assisted qualitative judgments after reading the packets.

This is a review register, not a keyword classifier or ground-truth labeling pipeline.
Re-running copies these judgments; changed source packets require a new review.
"""
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/milestone4'
REVIEWED_HASHES={
    'review-packets.json':'5a23de7d745db915ac772f659f3924f31feb1add1b47fcd47ac139cad06ce606',
    'expanded-review-packets.json':'55d07af36647b236399e62b984d062fc2c04c48f46cf39909ee40b9a2cd58f65',
    'validation-review-packets.json':'95fa5f5d0bfaecae769883231a541a30aa375c48b4db8977f35d0659729e09e3',
}
# issue, mechanisms, evidence comments, potentially addressable lead, limits/counterevidence
REVIEWS=[
('1008598','technical dependency; coordination','1095304 1096613 1098062','Clarify application/database responsibility', 'UAT/production schema and access questions remain; no established ready-to-act time or complete meeting record.'),
('1008678','missing artifact; testing confirmation','1097203 1098553 1102953','Artifact collection and confirmation', 'Production JAR requested and later collected; reminders already occur. Collection after exit corroborates context, not a pre-entry predictor.'),
('1005715','customer testing; production approval; administrative closure','1063624 1063924 1065379 1065592','Testing-to-confirmation communication', 'Post-exit report says UAT completed and production approval pending; completion timestamp and approval need unknown.'),
('1010058','access dependency; coordination; customer testing; administrative closure','1108190 1110389 1112403 1114184 1121152','Dependency readiness and test confirmation', 'Expanded full episode: access becomes available and UAT report can be reached, then business testing remains pending. One Waiting interval spans changing blockers; no evidence all 65 days were unnecessary.'),
('1004368','intermittent recurrence; missing logs; technical investigation','1060323 1060351 1063595 1070520','Diagnostic artifact availability', 'Cannot reproduce and must await recurrence; later log receipt does not establish earlier ability to provide them.'),
('1007739','incorrect diagnostic artifact; transfer constraint; coordination; internal technical work','1095949 1096016 1096543 1096545 1097399 1099917','Diagnostic collection readiness and cross-team coordination', 'Expanded full episode: wrong log directory/dates, file-size objection, narrowed request already supplied, then extraction/infrastructure problems and internal investigation. No proven feasible faster collection route or available staff.'),
('1009661','specification clarification; internal dependency','1102436 1102483 1102620','API specification completeness', 'Masked required specification prevents checking completeness; elapsed time alone cannot identify responsible delay.'),
('1007611','coordination; access credentials; technical work','1081124 1085282 1085557','Connection and access readiness', 'Some wallet work applied while still Waiting; template saying resolved is not reliable restoration evidence.'),
('1004446','coordination; technical investigation; customer confirmation','1047170 1050570 1055964','Dependency ownership', 'Session and ongoing investigation appear; reporter eventually permits closure. Masking prevents specific root cause and readiness determination.'),
('1005454','scheduled activity; coordination','1061533 1065126 1073872','Scheduling visibility', 'Explicit rescheduling could be legitimate. Sparse later context and unknown activity completion time preclude classifying the long tail.'),
('1004519','diagnostic information; coordination; administrative closure','1049176 1049644 1070154','Diagnostic capture readiness', 'Request/response capture required; nonresponse closure is not verified technical restoration or proof of avoidable delay.'),
('1007580','customer testing; confirmation','1082042 1084454','Confirmation timing', 'No during-episode comments; post-exit phone reference reports resolution. Unrecorded call timing and customer work unknown.'),
('1009250','workaround implementation; confirmation','1098504 1099113 1099900','Implementation confirmation', 'Reminder asks whether workaround applied; no completion evidence or verified response standard. Template is not validated policy.'),
('1006856','network dependency; migration testing; coordination; technical work','1073229 1075779 1079797','Environment and connectivity readiness', 'Connectivity eventually works but customer-message work remains. Scope-specific resolution does not establish total service restoration.'),
('1004298','incomplete report; certificate dependency; technical work; administrative closure','1045412 1052693 1070939','Diagnostic scope and prerequisite clarity', 'Mixed vulnerability/configuration work and certificate dependency; 46 during-episode comments, only four sampled. No blanket idleness claim.'),
('1010303','DBA action; requested output; administrative closure','1111953 1114980','Cross-team evidence delivery', 'DBA script/output requested after app work; no proof of DBA availability, approval or actual script completion.'),
('1007567','customer testing; state-recording ambiguity','1087009 1087457','State/outcome meaning requires validation', 'Four-second Waiting then Resolved although feedback still requested later. Not a substantive four-second operational queue.'),
('1008671','solution acceptance; internal development','1095610 1095938 1096371','Agreed acceptance criteria', 'Reporter rejects workaround, assignee identifies fix. Could be valid product requirement; no evidence it was feasible earlier.'),
('1007010','monitoring; technical investigation; developer dependency','1076285 1076618 1076941 1076963','Investigation ownership and diagnostic sufficiency', 'Explicit uncertainty about root cause and request to monitor; developer work occurs while Waiting. Planned observation may be necessary.'),
('1006065','fix deployment; customer testing; monitoring','1101631 1101964','Deployment confirmation timing', 'Long pre-entry deployment instructions truncated in packet; only deployment/testing context inferred, not technical adequacy. Post-exit production change reported.'),
('1008607','testing feedback; development rework; third-party dependency','1094185 1095272 1095291 1095394','Test failure and subsequent fix investigation', 'Concrete error after UAT fix with requested redevelopment, but exact defect/ownership masked. Waiting-to-Validation, not necessarily the defined Validation-to-In-progress return.'),
('1009327','change authorization; release coordination','1107904 1108648','Change scope and release confirmation', 'Broad redeployment consequences require confirmation; later release request corroborates dependency, not avoidability.'),
('1004444','session coordination; access dependency','1047952 1047956 1048059','Test environment access readiness', 'Dump available before entry, but post-exit message reports connection failure and deferred test access. Available information alone does not make action feasible.'),
('1005845','incomplete diagnostic evidence; clarification','1062480 1062498 1062566','Diagnostic input completeness', 'Corrupted images/scope clarified quickly, then internal checking begins. A necessary clarification loop, not demonstrated avoidable delay.'),
('1004857','active technical investigation; planned monitoring','1052039 1052107 1052201','State/work distinction', 'Session investigation and planned configuration work occur around Waiting; ownership time is not labor time.'),
('1006717','third-party session dependency','1071598 1071622','Dependency readiness', 'Session opened by another team and case closed within an hour; no evidence of a preventable breach.'),
('1007957','diagnostic information; technical investigation; expected behavior','1084725 1085276 1085342','Problem definition and input completeness', 'Support concludes behavior matches approved requirements; reporter requests closure. This is not necessarily an incident or defective service.'),
('1005127','customer action; restoration confirmation; administrative tail','1054796 1055109','Confirmation-to-status timing', 'Reporter confirms cache clearing works during Waiting; delay to status update exists, but service already works and no handling standard or available actor established.'),
('1007323','configuration confirmation; remote support; off-platform communication','1078033 1078753 1078905','Confirmation visibility', 'WhatsApp confirmation is referenced but exact restoration and communication times absent; apparent silence is not absence of work.'),
('1009230','session coordination; technical action','1098025 1098039 1098599','Connection readiness', 'Session nonattendance and later account reset observed. Availability and authorized response standard unknown.'),
('1005913','network checks; confirmation','1063201 1063204 1063348','Diagnostic confirmation', 'Connectivity checks requested and closure contemplated; no explicit customer result in packet. Mechanism and elapsed-time necessity remain provisional.'),
('1010562','UAT testing; production deployment; confirmation','1111442 1111478 1111502 1111582','Test/deployment boundary visibility', 'Successful UAT confirmation followed by production deployment during Waiting. Illustrates necessary stages rather than idle queue time.'),
]

# Each observed Validation -> In-progress event in the available primary text cases.
VALIDATION_REVIEWS=[
('1004667',1643018862,'New change request / workflow handling','211718366 1049988 1050007','Logo change, assignment and deployment scheduling; no demonstrated failed validation.'),
('1006065',1668339225,'Fix delivery / possible rework','1103785 1104159','Permanent password-reset fix and rollback instructions; not enough context to attribute a specific prior failed test.'),
('1006849',1670408826,'Successful testing to production deployment','1109299 1109303 1109412 1109645','Test success and explicit approval precede deployment. Direct counterexample to equating every return with failed validation.'),
('1007244',1657084031,'Continuing defect investigation','1078756 1079038 1079472','Unresolved data mismatch, tracing and log-level changes; does not identify a preventable earlier test failure.'),
('1007244',1659848940,'Fix delivery with subsequent reported issue','1084372 1084832','Fix instructions precede return; later missing fields reported. Later failure is outcome context, not established cause of the earlier return.'),
('1007291',1667307168,'Development investigation; sparse context','1101441','Only development update near return; failure reason unknown.'),
('1007291',1669797416,'Continuing defect investigation and fix delivery','1107333 1107384 1107847','Recurring issue and risky manual workaround reported; trigger supplied. Specific avoidable process failure and independent harm not established.'),
('1007420',1665978156,'Unknown','','No comments in the specified window; retain unknown.'),
('1007420',1666251831,'Fix delivery; testing requested','1098872 1099176','Work and UAT fix instructions; failed prior acceptance test not observed in window.'),
('1009151',1665901100,'Deployment scheduling','1098000 1098579 1098589','Download, test deployment and remote-session coordination; no proven validation failure.'),
('1009327',1672596139,'Fix delivery; testing requested','1113854','Only post-return fix and test instructions; return cause unknown.'),
('1010327',1670495395,'Known defect; mitigation followed by new release','1109152 1109176 1109734','Reporter says symptom mitigated before return while root cause remains under development; testing before rollout is legitimate.'),
]

def run():
    for name,digest in REVIEWED_HASHES.items():
        if hashlib.sha256((OUT/name).read_bytes()).hexdigest()!=digest:
            raise ValueError(f'{name} changed. Review the evidence again before updating judgments and pinned hashes.')
    packets=json.loads((OUT/'review-packets.json').read_text())
    expanded=json.loads((OUT/'expanded-review-packets.json').read_text())
    by_issue={p['issueid']:p for p in packets}
    assert set(by_issue)=={r[0] for r in REVIEWS} and len(REVIEWS)==32
    results=[]
    for issue,mechanisms,ids,lead,limits in REVIEWS:
        p=by_issue[issue]
        comments={r['comment_id']:r for r in p['comments']}
        for x in expanded:
            if x['issueid']!=issue:continue
            sample=pd.read_csv(OUT/'review-sample.csv',dtype={'issueid':str})
            e=sample[sample.issueid.eq(issue)].iloc[0]
            for r in x['comments']:
                comments[r['id']]=dict(comment_id=r['id'],source_rows=r['source_rows'],
                    period='before' if r['created_ts']<e.created_ts else 'during' if r['created_ts']<e.end_ts else 'after')
        evidence=[{k:comments[i][k] for k in ['comment_id','source_rows','period']} for i in ids.split()]
        results.append(dict(issueid=issue,episode_id=p['episode_id'],stratum=p['stratum'],days=p['days'],
            mechanisms=mechanisms,necessary_dependency='plausible; full duration unclassified',
            investigation_lead=lead,verified_avoidable=False,limits_and_counterevidence=limits,evidence=evidence))
    (OUT/'waiting-review-register.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    flat=[{**{k:v for k,v in r.items() if k!='evidence'},'evidence_comment_ids':' '.join(e['comment_id'] for e in r['evidence'])} for r in results]
    pd.DataFrame(flat).to_csv(OUT/'waiting-review-register.csv',index=False)
    vp=json.loads((OUT/'validation-review-packets.json').read_text())
    assert {(p['issueid'],p['return_ts']) for p in vp}=={(r[0],r[1]) for r in VALIDATION_REVIEWS}
    results=[]
    for issue,ts,label,ids,limits in VALIDATION_REVIEWS:
        packet=next(p for p in vp if p['issueid']==issue and p['return_ts']==ts)
        comments={c['id']:c for c in packet['comments']}
        evidence=[{k:comments[i][k] for k in ['id','period','source_rows']} for i in ids.split()]
        results.append(dict(issueid=issue,return_ts=ts,interpretation=label,evidence=evidence,
            limits_and_counterevidence=limits,verified_avoidable=False))
    (OUT/'validation-review-register.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    meta=dict(reviewer='Codex model-assisted qualitative review; no independent human validation',
        scope='32 purposive Waiting episodes plus all 12 observed validation-return events in 9 text-covered cases; cases overlap',
        packet_sha256={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in
            ['review-packets.json','expanded-review-packets.json','validation-review-packets.json']},
        warning='Labels are illustrative mechanisms, not population rates or verified avoidability; re-review if packets change.')
    (OUT/'review-metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    print('Saved 32 episode reviews and 12 validation-transition reviews with evidence lineage.')

if __name__=='__main__':run()
