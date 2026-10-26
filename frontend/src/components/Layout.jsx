import {useState,useEffect} from 'react';import {NavLink,Outlet,Link,useLocation} from 'react-router-dom';
import {LayoutDashboard,Stethoscope,Video,FolderHeart,MapPin,Pill,Settings,Bell,Menu,X,User} from 'lucide-react';
import auth from '../services/authService.js';
const nav=[['/','Overview',LayoutDashboard],['/diagnosis','Multi-Agent Diagnosis',Stethoscope],['/consultations','Video Consultation',Video],['/health-passport','Health Passport',FolderHeart],['/clinics','Find Clinics',MapPin],['/reminders','Medicine Reminders',Pill],['/settings','Settings',Settings]];
const titleFor=p=>(nav.find(([to])=>to!=='/'&&p.startsWith(to))||nav[0])[1];
export default function Layout(){
  const [open,setOpen]=useState(false);const {pathname}=useLocation();const [menu,setMenu]=useState(false);const [role,setRole]=useState('patient');
  useEffect(()=>{auth.getCurrentUser().then(u=>setRole(u.role)).catch(()=>{});},[]);
  return <div className="shell">
    <aside className={`sidebar ${open?'open':''}`} aria-label="Primary">
      <div className="brand"><Stethoscope size={22}/><b>DiagnoSure</b><button className="icon-btn mobile-only" aria-label="Close menu" onClick={()=>setOpen(false)}><X size={18}/></button></div>
      <nav>{nav.map(([to,l,I])=><NavLink key={to} to={to} end={to==='/'} onClick={()=>setOpen(false)}><I size={18}/>{l}</NavLink>)}{role==='doctor'&&<NavLink to="/doctor/consultations" onClick={()=>setOpen(false)}><Video size={18}/>Doctor consultations</NavLink>}</nav>
      <Link to="/settings" className="profile" onClick={()=>setOpen(false)}><User size={28}/><div><b>My account</b><small>Patient profile</small></div></Link>
    </aside>
    {open&&<div className="scrim" onClick={()=>setOpen(false)}/>}
    <div className="main">
      <header className="topbar">
        <button className="icon-btn mobile-only" aria-label="Open menu" onClick={()=>setOpen(true)}><Menu size={20}/></button>
        <div><small className="crumb">DiagnoSure / {titleFor(pathname)}</small><h1>{titleFor(pathname)}</h1></div>
        <div className="spacer"/>
        <Link className="icon-btn" to="/reminders" aria-label="Notifications and reminders"><Bell size={18}/></Link>
        <div className="menu-wrap"><button className="icon-btn" aria-label="Profile menu" aria-expanded={menu} onClick={()=>setMenu(!menu)}><User size={18}/></button>
          {menu&&<div className="menu" onClick={()=>setMenu(false)}><Link to="/settings">Profile & settings</Link><Link to="/health-passport">Health Passport</Link></div>}</div>
      </header>
      <main><Outlet/></main>
      <footer className="foot">DiagnoSure is clinical decision support, not a diagnosis or a substitute for professional care. In an emergency contact local emergency services.</footer>
    </div>
  </div>;
}
