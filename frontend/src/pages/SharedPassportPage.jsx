import {useParams} from 'react-router-dom';
import useAsync from '../hooks/useAsync.js';
import {request,requestBlob} from '../services/apiClient.js';
import {Card,Button,Async} from '../components/ui.jsx';

export default function SharedPassport(){
  const {token}=useParams();
  const state=useAsync(()=>request(`/passport/shared/${token}`),[token]);
  async function download(){const blob=await requestBlob(`/passport/shared/${token}/pdf`);const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='health-passport.pdf';a.click();URL.revokeObjectURL(url);}
  return <main className="stack" style={{maxWidth:760,margin:'2rem auto',padding:'1rem'}}><Async state={state}>{({passport})=><><Card title="DiagnoSure Health Passport"><p>Read-only passport for <b>{passport.name}</b>. Verify the patient’s identity before using this information.</p><Button onClick={download}>Download PDF</Button></Card><Card title="Patient details"><dl className="dl"><dt>Age</dt><dd>{passport.age||'Not provided'}</dd><dt>Sex</dt><dd>{passport.sex||'Not provided'}</dd><dt>Allergies</dt><dd>{passport.allergies.join(', ')||'None recorded'}</dd><dt>Conditions</dt><dd>{passport.conditions.join(', ')||'None recorded'}</dd><dt>Medications</dt><dd>{passport.medications.join(', ')||'None recorded'}</dd><dt>Medical history</dt><dd>{passport.medical_history||'None recorded'}</dd></dl></Card></>}</Async></main>;
}
