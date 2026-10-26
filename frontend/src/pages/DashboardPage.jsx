import {Link} from 'react-router-dom';import {Stethoscope,Video,FolderHeart,MapPin,Pill} from 'lucide-react';
import useAsync from '../hooks/useAsync.js';import {Card,Badge,tone,Async,fmt,Empty} from '../components/ui.jsx';
import diagnosis from '../services/diagnosisService.js';import consultations from '../services/consultationService.js';
import reminders from '../services/reminderService.js';import hp from '../services/healthPassportService.js';import auth from '../services/authService.js';
const quick=[['/diagnosis','New Diagnosis',Stethoscope],['/consultations','Book Consultation',Video],['/health-passport','View Health Passport',FolderHeart],['/clinics','Find Nearby Clinics',MapPin],['/reminders','Medicine Reminders',Pill]];
export default function Dashboard(){
  const st=useAsync(async()=>{const [user,cases,c,r,rec,sum]=await Promise.all([auth.getCurrentUser(),diagnosis.listCases(),consultations.listConsultations(),reminders.listReminders(),hp.listMedicalRecords(),hp.getHealthSummary()]);return {user,cases,cons:c.items,r,rec,sum};});
  return <Async state={st}>{d=>{
    const up=d.cons.filter(c=>['scheduled','accepted'].includes(c.status));
    return <>
    <Card className="hero"><h2>Hello, {d.user?.name.split(' ')[0]}</h2><p>DiagnoSure supports clinical decision-making with structured case assessment, consultations, your Health Passport, nearby care and reminders.</p>
      <div className="row"><Link className="btn primary" to="/diagnosis">Start New Assessment</Link><Link className="btn secondary" to="/health-passport">View Health Passport</Link></div></Card>
    <div className="grid5">{quick.map(([to,l,I])=><Link key={to} to={to} className="quick"><I size={20}/>{l}</Link>)}</div>
    <div className="grid4">{[['Recent assessments',d.cases.length],['Upcoming consultations',up.length],["Today's reminders",d.r.filter(x=>x.status==='scheduled').length],['Health records',d.rec.length]].map(([l,n])=><Card key={l} className="stat"><b>{n}</b><span>{l}</span></Card>)}</div>
    <div className="grid2">
      <Card title="Recent activity"><ul className="list">
        {d.cases.map(c=><li key={c.case_id}><Link to={`/diagnosis/results/${c.case_id}`}>Assessment {c.case_id}</Link><small>{fmt(c.created_at)}</small></li>)}
        {up.map(c=><li key={c.id}><Link to={`/consultations/${c.id}`}>Upcoming: {c.doctor}</Link><small>{fmt(c.scheduledAt)}</small></li>)}
        {d.rec.slice(0,2).map(r=><li key={r.id}><Link to={`/health-passport/records/${r.id}`}>Record: {r.title}</Link><small>{r.date}</small></li>)}
        {d.r.filter(x=>x.status==='completed').map(x=><li key={x.id}><Link to="/reminders">Completed: {x.title}</Link><small>Reminder</small></li>)}
        {!d.cases.length&&<Empty title="No activity yet"/>}</ul></Card>
      <Card title="Health overview"><dl className="dl"><dt>Existing conditions</dt><dd>{d.sum.conditions.join(', ')||'None recorded'}</dd><dt>Allergies</dt><dd>{d.sum.allergies.join(', ')||'None recorded'}</dd><dt>Current medications</dt><dd>{d.sum.medications.join(', ')||'None recorded'}</dd></dl>
        <Badge tone="green">Stored backend data</Badge></Card></div></>;}}</Async>;
}
