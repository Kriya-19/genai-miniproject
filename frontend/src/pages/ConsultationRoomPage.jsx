import {useParams} from 'react-router-dom';
import useAsync from '../hooks/useAsync.js';
import svc from '../services/consultationService.js';
import hp from '../services/healthPassportService.js';
import diagnosis from '../services/diagnosisService.js';
import auth from '../services/authService.js';
import {Card,Badge,Async} from '../components/ui.jsx';

export default function Room(){
  const {consultationId}=useParams();
  const st=useAsync(async()=>{
    const c=await svc.getConsultation(consultationId);
    const j=await svc.getJoinDetails(consultationId);
    const user=await auth.getCurrentUser();
    const sum=await hp.getHealthSummary();
    const cs=c.caseId?await diagnosis.getCase(c.caseId):null;
    return {c,j,sum,cs,user};
  },[consultationId]);
  return <Async state={st}>{({c,j,sum,cs,user})=><div className="room">
    <div className="stack">
      <div className="note">{user.role==='doctor'?'You are the doctor. Open Jitsi in a new tab and sign in once in that browser session before the patient joins. Public meet.jit.si does not make anonymous guests moderators.':'The doctor must first sign in to Jitsi and become the moderator. Then join this same room.'}</div>
      <div className="row wrap"><a className="btn primary" href={j.video_url} target="_blank" rel="noreferrer">{user.role==='doctor'?'Start as Jitsi moderator':'Open Jitsi room'}</a>{user.role==='doctor'&&<small>Use the same room URL shown here; do not create a new room.</small>}</div>
      <div className="stage">{j.video_url&&<iframe title="Jitsi consultation" src={j.video_url} allow="camera; microphone; fullscreen; display-capture" style={{width:'100%',height:'620px',border:0}} />}</div>
    </div>
    <aside className="stack">
      <Card title="Patient-authorized summary"><dl className="dl"><dt>Allergies</dt><dd>{sum.allergies.join(', ')||'None recorded'}</dd><dt>Medications</dt><dd>{sum.medications.join(', ')||'None recorded'}</dd><dt>Conditions</dt><dd>{sum.conditions.join(', ')||'None recorded'}</dd></dl></Card>
      <Card title="AI case summary">{cs?<><Badge tone="amber">AI-generated, not clinician-verified</Badge><ol>{cs.differential_diagnoses.map(d=><li key={d.rank}>{d.condition} <small>(ranking score {d.ranking_score})</small></li>)}</ol></>:<p className="muted">No diagnosis report shared for this consultation.</p>}</Card>
    </aside>
  </div>}</Async>;
}
