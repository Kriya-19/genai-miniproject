import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import auth from '../services/authService.js';
import {Button,Card,Field,useToast} from '../components/ui.jsx';

export default function LoginPage(){
  const [mode,setMode]=useState('login');const [form,setForm]=useState({email:'',password:'',full_name:'',role:'patient'});const [error,setError]=useState('');const nav=useNavigate();const toast=useToast();
  async function submit(e){e.preventDefault();setError('');try{await (mode==='login'?auth.signIn({email:form.email,password:form.password}):auth.register(form));toast('Signed in');nav('/');}catch(x){setError(x.message);}}
  return <main className="stack" style={{maxWidth:480,margin:'4rem auto',padding:'1rem'}}>
    <Card title="DiagnoSure">
      <form className="stack" onSubmit={submit}>
        {mode==='register'&&<><Field label="Full name"><input required value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></Field>
        {mode==='register'&&<Field label="Account type"><select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="patient">Patient</option><option value="doctor">Doctor</option></select></Field>}
        {form.role==='patient'&&<><Field label="Age"><input type="number" min="0" max="130" required value={form.age||''} onChange={e=>setForm({...form,age:e.target.value?Number(e.target.value):null})}/></Field><Field label="Sex"><select required value={form.sex||''} onChange={e=>setForm({...form,sex:e.target.value})}><option value="">Select…</option><option>Female</option><option>Male</option><option>Other</option><option>Prefer not to say</option></select></Field><Field label="Known allergies" hint="Comma separated, or write None"><input required value={form.allergies||''} onChange={e=>setForm({...form,allergies:e.target.value.split(',').map(x=>x.trim()).filter(Boolean)})}/></Field><Field label="Existing conditions" hint="Comma separated, or write None"><input required value={form.conditions||''} onChange={e=>setForm({...form,conditions:e.target.value.split(',').map(x=>x.trim()).filter(Boolean)})}/></Field><Field label="Current medications" hint="Comma separated, or write None"><input required value={form.medications||''} onChange={e=>setForm({...form,medications:e.target.value.split(',').map(x=>x.trim()).filter(Boolean)})}/></Field><Field label="Medical history"><textarea rows="3" value={form.medical_history||''} onChange={e=>setForm({...form,medical_history:e.target.value})}/></Field></>}</>}
        <Field label="Email"><input type="email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></Field>
        <Field label="Password"><input type="password" minLength="8" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></Field>
        {error&&<em className="err-t" role="alert">{error}</em>}
        <Button type="submit">{mode==='login'?'Sign in':'Create account'}</Button>
        <Button type="button" variant="ghost" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'Create a patient account':'Use existing account'}</Button>
      </form>
    </Card>
  </main>;
}
