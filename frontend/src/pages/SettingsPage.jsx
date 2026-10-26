import {useState,useEffect} from 'react';
import useAsync from '../hooks/useAsync.js';import rem from '../services/reminderService.js';import auth from '../services/authService.js';import {USE_MOCKS} from '../services/apiClient.js';
import {Card,Button,Field,Badge,Async,useToast} from '../components/ui.jsx';
export default function Settings(){
  const toast=useToast();const u=useAsync(()=>auth.getCurrentUser());const p=useAsync(()=>rem.getNotificationPreferences());
  const [prefs,setPrefs]=useState(null);const [lang,setLang]=useState('en');const [big,setBig]=useState(false);const [out,setOut]=useState(false);
  useEffect(()=>{if(p.data)setPrefs(p.data);},[p.data]);useEffect(()=>{document.documentElement.classList.toggle('large-text',big);},[big]);
  const save=async n=>{setPrefs(n);try{await rem.updateNotificationPreferences(n);toast('Preferences saved');}catch(e){toast(e.message,'bad');}};
  async function browser(on){if(!on)return save({...prefs,browser:false});
    if(!('Notification' in window))return toast('Browser notifications are not supported','bad');
    const r=await Notification.requestPermission();if(r==='granted')save({...prefs,browser:true});else toast('Permission not granted','bad');}
  if(out)return <Card title="Signed out"><p>You are signed out of this account.</p><Button onClick={()=>window.location.reload()}>Sign in again</Button></Card>;
  return <div className="stack">
    <Card title="Connected backend"><p>{USE_MOCKS?'Mock mode is enabled. Set VITE_USE_MOCKS=false to use the backend.':'This application is connected to the configured DiagnoSure backend.'}</p></Card>
    <Async state={u}>{x=><Card title="Profile"><dl className="dl"><dt>Name</dt><dd>{x.name}</dd><dt>Email</dt><dd>{x.email}</dd><dt>Role</dt><dd>{x.role}</dd></dl>
      <div className="grid2"><Field label="Preferred language"><select value={lang} onChange={e=>{setLang(e.target.value);toast('Language preference selected; translation support is not enabled yet.');}}><option value="en">English</option><option value="hi">Hindi</option><option value="mr">Marathi</option></select></Field>
        <Field label="Time zone"><input readOnly value={x.timezone}/></Field></div></Card>}</Async>
    <Card title="Notification preferences"><Async state={p}>{()=>prefs&&<div className="stack">
      <label className="check"><input type="checkbox" checked={prefs.browser} onChange={e=>browser(e.target.checked)}/>Browser notifications (permission requested when enabled)</label>
      {[['reminders','Reminder alerts'],['appointments','Appointment reminders'],['followups','Follow-up notifications']].map(([k,l])=><label className="check" key={k}><input type="checkbox" checked={prefs[k]} onChange={e=>save({...prefs,[k]:e.target.checked})}/>{l}</label>)}
      <div className="grid2"><Field label="Quiet hours start"><input type="time" value={prefs.quietStart} onChange={e=>save({...prefs,quietStart:e.target.value})}/></Field><Field label="Quiet hours end"><input type="time" value={prefs.quietEnd} onChange={e=>save({...prefs,quietEnd:e.target.value})}/></Field></div>
      <small>Alerts cannot fire after the browser closes without a backend scheduler.</small></div>}</Async></Card>
    <Card title="Accessibility"><label className="check"><input type="checkbox" checked={big} onChange={e=>setBig(e.target.checked)}/>Larger text</label></Card>
    <Card title="Privacy and consent"><p>Health records are stored by the backend and protected by authentication. Sharing requires explicit consent and an expiry.</p></Card>
    <Card title="Connected services"><ul className="list">{['Diagnosis engine','Jitsi consultations','OpenStreetMap clinics','APScheduler reminders','Private record storage'].map(s=><li key={s}>{s}<Badge tone="green">Backend</Badge></li>)}</ul></Card>
    <div><Button variant="danger" onClick={async()=>{await auth.signOut();setOut(true);}}>Sign out</Button></div></div>;
}
