import {useState} from 'react';import {Link} from 'react-router-dom';
import useAsync from '../hooks/useAsync.js';import svc from '../services/reminderService.js';import {Card,Button,Field,Badge,tone,Modal,Confirm,Async,Empty,useToast,fmt} from '../components/ui.jsx';
const tz=Intl.DateTimeFormat().resolvedOptions().timeZone;
const blank={kind:'medication',title:'',instructions:'',times:'08:00',startDate:new Date().toISOString().slice(0,10),endDate:'',frequency:'daily',timezone:tz,reference:''};
function Form({initial,onClose,onDone}){
  const [f,setF]=useState(initial?{...initial,times:initial.times.join(', ')}:blank);const [err,setErr]=useState({});const toast=useToast();
  async function go(e){e.preventDefault();const er={};if(!f.title.trim())er.title='Required.';if(f.kind==='medication'&&!f.instructions.trim())er.instructions='Enter instructions from your clinician-approved prescription.';
    const times=f.times.split(',').map(x=>x.trim()).filter(Boolean);if(!times.length||times.some(t=>!/^\d{2}:\d{2}$/.test(t)))er.times='Use HH:MM, comma separated.';
    if(f.endDate&&f.endDate<f.startDate)er.endDate='End date must be after start.';setErr(er);if(Object.keys(er).length)return;
    const p={...f,times};initial?await svc.updateReminder(initial.id,p):await svc.createReminder(p);toast(initial?'Reminder updated':'Reminder created');onDone();}
  return <Modal title={initial?'Edit reminder':'New reminder'} onClose={onClose}><form onSubmit={go} className="stack" noValidate>
    <Field label="Type"><select value={f.kind} onChange={e=>setF({...f,kind:e.target.value})}><option value="medication">Medication</option><option value="followup">Follow-up / other</option></select></Field>
    <Field label={f.kind==='medication'?'Medication name':'Title'} error={err.title}><input value={f.title} onChange={e=>setF({...f,title:e.target.value})}/></Field>
    <Field label={f.kind==='medication'?'Instructions from clinician-approved prescription':'Notes'} error={err.instructions} hint={f.kind==='medication'?'DiagnoSure does not suggest doses. Copy them from your prescription.':''}><textarea rows="2" value={f.instructions} onChange={e=>setF({...f,instructions:e.target.value})}/></Field>
    <div className="grid2"><Field label="Times" error={err.times}><input value={f.times} onChange={e=>setF({...f,times:e.target.value})}/></Field>
      <Field label="Frequency"><select value={f.frequency} onChange={e=>setF({...f,frequency:e.target.value})}><option value="once">Once</option><option value="daily">Daily</option><option value="weekly">Weekly</option></select></Field>
      <Field label="Start date"><input type="date" value={f.startDate} onChange={e=>setF({...f,startDate:e.target.value})}/></Field>
      <Field label="End date (optional)" error={err.endDate}><input type="date" value={f.endDate} onChange={e=>setF({...f,endDate:e.target.value})}/></Field></div>
    <Field label="Time zone"><input value={f.timezone} onChange={e=>setF({...f,timezone:e.target.value})}/></Field>
    <Field label="Prescription / clinician reference (optional)"><input value={f.reference} onChange={e=>setF({...f,reference:e.target.value})}/></Field>
    <div className="row end"><Button type="button" variant="secondary" onClick={onClose}>Cancel</Button><Button type="submit">Save</Button></div></form></Modal>;
}
export default function Reminders(){
  const [status,setStatus]=useState('all');const st=useAsync(()=>svc.listReminders({status}),[status]);const [form,setForm]=useState(null);const [cancel,setCancel]=useState(null);const [hist,setHist]=useState(null);const toast=useToast();
  const act=async(fn,msg)=>{try{await fn();toast(msg);st.reload();}catch(e){toast(e.message,'bad');}};
  return <div className="stack"><div className="row wrap"><select aria-label="Filter by status" value={status} onChange={e=>setStatus(e.target.value)}>{['all','scheduled','completed','missed','skipped','snoozed','cancelled'].map(s=><option key={s}>{s}</option>)}</select>
    <Link to="/settings" className="btn ghost">Notification preferences</Link><div className="spacer"/><Button onClick={()=>setForm({})}>Add reminder</Button></div>
    <div className="note">Reminders are saved to the backend and processed by the development scheduler. Local browser alerts are optional; delivery after the browser closes depends on the configured notification provider.</div>
    <Async state={st}>{list=>!list.length?<Empty title="No reminders match" text="Create a reminder or change the filter."/>:<div className="stack">{list.map(r=><Card key={r.id} className="rowcard"><div><b>{r.title}</b><small>{r.kind==='medication'?'Medication':'Follow-up'} · {r.times.join(', ')} · {r.frequency}</small><small>{r.instructions}</small></div><Badge tone={tone(r.status)}>{r.status}</Badge>
      <div className="row wrap">{['scheduled','snoozed','missed'].includes(r.status)&&<><Button variant="secondary" onClick={()=>act(()=>svc.completeReminder(r.id),'Marked completed')}>Complete</Button>
        {r.status==='scheduled'&&<><Button variant="ghost" onClick={()=>act(()=>svc.updateReminder(r.id,{action:'snoozed'}),'Snoozed 10 minutes')}>Snooze</Button><Button variant="ghost" onClick={()=>act(()=>svc.updateReminder(r.id,{action:'skipped'}),'Skipped')}>Skip</Button></>}
        <Button variant="ghost" onClick={()=>setForm(r)}>Edit</Button><Button variant="ghost" onClick={()=>setCancel(r)}>Cancel</Button></>}<Button variant="ghost" onClick={()=>setHist(r)}>History</Button></div></Card>)}</div>}</Async>
    {form&&<Form initial={form.id?form:null} onClose={()=>setForm(null)} onDone={()=>{setForm(null);st.reload();}}/>}
    {cancel&&<Confirm title="Cancel reminder?" text={`Cancel "${cancel.title}"?`} yes="Cancel reminder" onNo={()=>setCancel(null)} onYes={()=>{act(()=>svc.cancelReminder(cancel.id),'Reminder cancelled');setCancel(null);}}/>}
    {hist&&<Modal title={`History: ${hist.title}`} onClose={()=>setHist(null)}>{hist.history.length?<ul className="list">{hist.history.map((h,i)=><li key={i}>{h.event}<small>{fmt(h.at)}</small></li>)}</ul>:<Empty title="No history yet"/>}</Modal>}</div>;
}
