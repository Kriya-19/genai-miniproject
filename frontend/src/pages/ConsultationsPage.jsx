import {useState} from 'react';import {Link} from 'react-router-dom';import {Video,Phone} from 'lucide-react';
import useAsync from '../hooks/useAsync.js';import svc from '../services/consultationService.js';import diagnosis from '../services/diagnosisService.js';
import {Card,Button,Field,Badge,tone,Modal,Async,Empty,Confirm,useToast,fmt} from '../components/ui.jsx';
function Schedule({data,onClose,onDone}){
  const [f,setF]=useState({doctorId:'',slot:'',type:'video',reason:'',shareReport:false,consent:false});const [err,setErr]=useState({});const [busy,setBusy]=useState(false);const toast=useToast();
  const doc=data.doctors.find(d=>d.id===f.doctorId);
  async function go(e){e.preventDefault();const er={};if(!f.slot)er.slot='Choose a slot.';if(!f.consent)er.consent='Consent is required.';setErr(er);if(Object.keys(er).length)return;
    setBusy(true);try{await svc.createConsultation({...f,shareCaseId:null});toast('Consultation scheduled');onDone();}catch(x){toast(x.message,'bad');setBusy(false);}}
  return <Modal title="Schedule consultation" onClose={onClose}><form onSubmit={go} noValidate className="stack">
    <Field label="Doctor or specialty" error={err.doctor}><select value={f.doctorId} onChange={e=>setF({...f,doctorId:e.target.value,slot:''})}><option value="">Any available clinician</option>{data.doctors.map(d=><option key={d.id} value={d.id}>{d.name}, {d.specialty}</option>)}</select></Field>
    <Field label="Appointment time" error={err.slot}><input type="datetime-local" value={f.slot} onChange={e=>setF({...f,slot:e.target.value})}/></Field>
    <Field label="Consultation type"><select value={f.type} onChange={e=>setF({...f,type:e.target.value})}><option value="video">Video</option><option value="audio">Audio only</option></select></Field>
    <Field label="Reason (optional)"><textarea rows="2" value={f.reason} onChange={e=>setF({...f,reason:e.target.value})}/></Field>
    <label className="check"><input type="checkbox" checked={f.shareReport} onChange={e=>setF({...f,shareReport:e.target.checked})}/>Share my latest diagnosis report with the doctor</label>
    <label className="check"><input type="checkbox" checked={f.consent} onChange={e=>setF({...f,consent:e.target.checked})}/>I consent to this consultation and to sharing the selected information.</label>{err.consent&&<em className="err-t" role="alert">{err.consent}</em>}
    <div className="row end"><Button variant="secondary" type="button" onClick={onClose}>Cancel</Button><Button type="submit" disabled={busy}>{busy?'Scheduling…':'Schedule'}</Button></div></form></Modal>;
}
export default function Consultations(){
  const st=useAsync(()=>svc.listConsultations());const [q,setQ]=useState('');const [status,setStatus]=useState('all');const [show,setShow]=useState(false);const [cancel,setCancel]=useState(null);const toast=useToast();
  return <Async state={st}>{d=>{
    const items=d.items.filter(c=>(status==='all'||c.status===status)&&(c.doctor+c.specialty).toLowerCase().includes(q.toLowerCase()));
    const row=c=><Card key={c.id} className="rowcard"><div><b>{c.doctor}</b><small>{c.specialty} · {fmt(c.scheduledAt)}</small>{c.reason&&<small>Reason: {c.reason}</small>}</div>
      <Badge>{c.type==='video'?'Video':'Audio'}</Badge><Badge tone={tone(c.status)}>{c.status}</Badge>
      {['scheduled','accepted'].includes(c.status)&&<><Link className="btn primary" to={`/consultations/${c.id}`}>{c.type==='video'?<Video size={16}/>:<Phone size={16}/>}Join Consultation</Link><Button variant="ghost" onClick={()=>setCancel(c)}>Cancel</Button></>}</Card>;
    const up=items.filter(c=>c.status==='scheduled'),past=items.filter(c=>c.status!=='scheduled');
    return <div className="stack"><div className="row wrap"><input aria-label="Search consultations" placeholder="Search doctor or specialty" value={q} onChange={e=>setQ(e.target.value)}/>
      <select aria-label="Filter by status" value={status} onChange={e=>setStatus(e.target.value)}><option value="all">All statuses</option><option value="scheduled">Scheduled</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select>
      <div className="spacer"/><Button onClick={()=>setShow(true)}>Schedule Consultation</Button></div>
      <h2>Upcoming</h2>{up.length?up.map(row):<Empty title="No upcoming consultations"/>}
      <h2>Past</h2>{past.length?past.map(row):<Empty title="No past consultations"/>}
      {show&&<Schedule data={d} onClose={()=>setShow(false)} onDone={()=>{setShow(false);st.reload();}}/>}
      {cancel&&<Confirm title="Cancel consultation?" text={`Cancel your consultation with ${cancel.doctor}?`} yes="Cancel consultation" onNo={()=>setCancel(null)} onYes={async()=>{await svc.cancelConsultation(cancel.id);setCancel(null);toast('Consultation cancelled');st.reload();}}/>}</div>;}}</Async>;
}
