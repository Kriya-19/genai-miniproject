import {Routes,Route,Navigate} from 'react-router-dom';import {useEffect,useState} from 'react';import Layout from '../components/Layout.jsx';
import Dashboard from '../pages/DashboardPage.jsx';import Diagnosis from '../pages/DiagnosisPage.jsx';import Results from '../pages/DiagnosisResultsPage.jsx';
import Consultations from '../pages/ConsultationsPage.jsx';import Room from '../pages/ConsultationRoomPage.jsx';
import DoctorConsultations from '../pages/DoctorConsultationsPage.jsx';
import Passport from '../pages/HealthPassportPage.jsx';import Record from '../pages/MedicalRecordPage.jsx';
import Clinics from '../pages/ClinicsPage.jsx';import Reminders from '../pages/RemindersPage.jsx';import Settings from '../pages/SettingsPage.jsx';
import {Empty} from '../components/ui.jsx';import {Link} from 'react-router-dom';
import Login from '../pages/LoginPage.jsx';import auth from '../services/authService.js';
import SharedPassport from '../pages/SharedPassportPage.jsx';
const NotFound=()=><Empty title="Page not found" text="That page does not exist."><Link className="btn primary" to="/">Back to overview</Link></Empty>;
function Protected(){const [state,setState]=useState('loading');useEffect(()=>{auth.getCurrentUser().then(()=>setState('ready')).catch(()=>setState('login'));},[]);if(state==='loading')return <p>Loading…</p>;return state==='login'?<Navigate to="/login" replace/>:<Layout/>;}
export default function App(){return <Routes><Route path="/login" element={<Login/>}/><Route path="/passport/shared/:token" element={<SharedPassport/>}/><Route element={<Protected/>}>
  <Route path="/" element={<Dashboard/>}/><Route path="/diagnosis" element={<Diagnosis/>}/><Route path="/diagnosis/results/:caseId" element={<Results/>}/>
  <Route path="/consultations" element={<Consultations/>}/><Route path="/consultations/:consultationId" element={<Room/>}/>
  <Route path="/doctor/consultations" element={<DoctorConsultations/>}/>
  <Route path="/health-passport" element={<Passport/>}/><Route path="/health-passport/records/:recordId" element={<Record/>}/>
  <Route path="/clinics" element={<Clinics/>}/><Route path="/reminders" element={<Reminders/>}/><Route path="/settings" element={<Settings/>}/>
  <Route path="*" element={<NotFound/>}/></Route></Routes>;}
