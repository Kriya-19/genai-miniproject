// Fictional demo data only. Nothing here is a real patient, clinic result or clinical output.
export const wait=(ms=300)=>new Promise(r=>setTimeout(r,ms));
export const uid=p=>`${p}-${Math.random().toString(36).slice(2,7)}`;
const day=(n,h=10)=>{const d=new Date();d.setDate(d.getDate()+n);d.setHours(h,0,0,0);return d.toISOString();};
export const user={id:'demo-user',name:'Asha Verma',role:'Patient',email:'demo@diagnosure.example',language:'en',timezone:'Asia/Kolkata'};
export const profile={...user,age:34,sex:'Female',lastUpdated:day(-7)};
export const healthSummary={
  conditions:['Seasonal allergic rhinitis','Mild iron deficiency'],allergies:['Penicillin (patient-reported)'],
  medications:['Iron supplement, per prescription RX-DEMO-1'],
  vaccinations:[{name:'Influenza',date:'2025-11-02'},{name:'Tetanus booster',date:'2023-05-14'}],
  aiSummary:{generated:true,verified:false,text:'Sample AI-generated summary: history of seasonal allergic rhinitis and mild iron deficiency; reports a penicillin allergy; takes one prescribed iron supplement.',sources:['rec-1','rec-2','rec-3']},
  lastUpdated:day(-7)};
export const records=[
 {id:'rec-1',title:'Complete blood count (sample)',category:'lab',date:'2026-09-20',origin:'clinician',fileType:'application/pdf',size:182000,notes:'Fictional lab report.'},
 {id:'rec-2',title:'Iron supplement prescription (sample)',category:'prescription',date:'2026-09-22',origin:'clinician',fileType:'application/pdf',size:94000,notes:'Dose as written by the prescribing clinician.'},
 {id:'rec-3',title:'General consultation note (sample)',category:'consultation',date:'2026-08-30',origin:'clinician',fileType:'application/pdf',size:120000,notes:'Follow-up in 3 months.'},
 {id:'rec-4',title:'Influenza vaccination',category:'vaccination',date:'2025-11-02',origin:'patient',fileType:'image/jpeg',size:640000,notes:'Patient-uploaded photo; text not verified.'}];
export const shares=[{id:'share-1',recipient:'Dr. Demo Rao',recordIds:['rec-1'],createdAt:day(-3),expiresAt:day(4),status:'active'}];
export const doctors=[
 {id:'doc-1',name:'Dr. Demo Rao',specialty:'General Medicine',slots:[day(1,10),day(1,15),day(2,11)]},
 {id:'doc-2',name:'Dr. Demo Iyer',specialty:'Internal Medicine',slots:[day(1,12),day(3,9)]},
 {id:'doc-3',name:'Dr. Demo Khan',specialty:'ENT',slots:[day(2,16),day(4,10)]}];
export const consultations=[
 {id:'con-1',doctor:'Dr. Demo Rao',specialty:'General Medicine',scheduledAt:day(1,10),type:'video',status:'scheduled',reason:'Follow-up',caseId:'demo-case-001'},
 {id:'con-2',doctor:'Dr. Demo Iyer',specialty:'Internal Medicine',scheduledAt:day(-14,11),type:'audio',status:'completed',reason:'Review of lab results',caseId:null}];
const sample=(symptoms)=>({
  case_id:'demo-case-001',status:'completed',is_demo:true,created_at:day(-1),
  symptoms,history_used:['Seasonal allergic rhinitis','Penicillin allergy (patient-reported)'],
  differential_diagnoses:[
   {condition:'Viral upper respiratory infection',rank:1,ranking_score:0.78,score_type:'ranking_score',evidence_quality:'Sample',
    supporting_evidence:['Symptom pattern matches typical presentation'],contradictory_evidence:['No fever reported'],
    sources:[{title:'Placeholder source A (not a real citation)',details:'Demo data',url:null,summary:'Illustrative summary only.',relation:'supports'}],
    explanation:'Ranked first because most reported symptoms overlap with the sample profile.',uncertainty:'Overlaps with several other conditions.'},
   {condition:'Allergic rhinitis flare',rank:2,ranking_score:0.64,score_type:'ranking_score',evidence_quality:'Sample',
    supporting_evidence:['Existing allergy history'],contradictory_evidence:['Symptoms are new this week'],
    sources:[{title:'Placeholder source B (not a real citation)',details:'Demo data',url:null,summary:'Illustrative summary only.',relation:'partially supports'}],
    explanation:'History of allergic rhinitis raises relevance.',uncertainty:'Duration does not clearly fit.'},
   {condition:'Bacterial sinusitis',rank:3,ranking_score:0.41,score_type:'ranking_score',evidence_quality:'Sample',
    supporting_evidence:['Facial pressure may be present'],contradictory_evidence:['Short duration'],
    sources:[{title:'Placeholder source C (not a real citation)',details:'Demo data',url:null,summary:'Illustrative summary only.',relation:'weakly supports'}],
    explanation:'Included for completeness; duration is short.',uncertainty:'Cannot be assessed without examination.'}],
  case_comparisons:[{label:'Sample similar case 1 (fictional)',note:'Illustrative comparison only.'}],
  safety_warnings:['Seek urgent care for breathing difficulty, chest pain, confusion, or symptoms that rapidly worsen.'],
  missing_information:['Temperature readings','Vaccination status for respiratory illnesses'],
  limitations:['Demo output is NOT generated from your input and is not clinically valid.','Ranking scores are not calibrated probabilities.']});
export const cases={'demo-case-001':sample([{name:'Sore throat',duration:'3 days',severity:'mild'},{name:'Nasal congestion',duration:'4 days',severity:'moderate'}])};
export const makeCase=(payload)=>{const id=uid('demo-case');const c=sample(payload.symptoms);c.case_id=id;c.created_at=new Date().toISOString();cases[id]=c;return c;};
export const researchData={
  summary:[{metric:'Top-1 accuracy',baseline:0.42,multi:0.55},{metric:'Top-5 recall',baseline:0.71,multi:0.82},{metric:'Mean reciprocal rank',baseline:0.55,multi:0.66},
   {metric:'Symptom extraction F1',baseline:0.74,multi:0.81},{metric:'Evidence relevance',baseline:0.5,multi:0.68},{metric:'End-to-end latency (s)',baseline:4,multi:19}],
  ablations:[{config:'Full multi-agent',top1:0.55,top5:0.82},{config:'No literature retrieval',top1:0.48,top5:0.76},{config:'No case retrieval',top1:0.5,top5:0.78},{config:'No evidence synthesis',top1:0.47,top5:0.74}]};
export const clinics=[
 {id:'cl-1',name:'Sample Community Clinic',type:'clinic',address:'Fictional address 1',lat:19.076,lng:72.877,phone:'+910000000001',specialties:['General Medicine']},
 {id:'cl-2',name:'Sample District Hospital',type:'hospital',address:'Fictional address 2',lat:19.12,lng:72.9,phone:'+910000000002',specialties:['Emergency','Internal Medicine']},
 {id:'cl-3',name:'Sample Primary Health Centre',type:'primary care',address:'Fictional address 3',lat:19.03,lng:72.85,phone:null,specialties:['General Medicine']},
 {id:'cl-4',name:'Sample Emergency Unit',type:'emergency',address:'Fictional address 4',lat:19.2,lng:72.95,phone:'+910000000004',specialties:['Emergency']}];
export const reminders=[
 {id:'rem-1',kind:'medication',title:'Iron supplement',instructions:'As written on prescription RX-DEMO-1',times:['08:00'],startDate:'2026-10-01',endDate:'',frequency:'daily',timezone:'Asia/Kolkata',reference:'RX-DEMO-1',status:'scheduled',history:[]},
 {id:'rem-2',kind:'medication',title:'Morning dose (sample)',instructions:'As on prescription',times:['07:00'],startDate:'2026-10-01',endDate:'',frequency:'daily',timezone:'Asia/Kolkata',reference:'',status:'completed',history:[{at:day(0,7),event:'completed'}]},
 {id:'rem-3',kind:'followup',title:'Follow-up with Dr. Demo Rao',instructions:'Bring lab report',times:['10:00'],startDate:'2026-10-26',endDate:'',frequency:'once',timezone:'Asia/Kolkata',reference:'',status:'scheduled',history:[]},
 {id:'rem-4',kind:'medication',title:'Evening dose (sample)',instructions:'As on prescription',times:['21:00'],startDate:'2026-10-01',endDate:'',frequency:'daily',timezone:'Asia/Kolkata',reference:'',status:'missed',history:[{at:day(-1,21),event:'missed'}]}];
export const notifPrefs={browser:false,reminders:true,appointments:true,followups:true,quietStart:'22:00',quietEnd:'07:00'};
