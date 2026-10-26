import {pick,request} from './apiClient.js';import {reminders,notifPrefs,wait,uid} from '../mocks/data.js';
const find=id=>reminders.find(r=>r.id===id);const log=(r,event)=>r.history.unshift({at:new Date().toISOString(),event});
const mock={
  async listReminders(f={}){await wait(200);return reminders.filter(r=>!f.status||f.status==='all'||r.status===f.status).map(r=>({...r}));},
  async createReminder(p){await wait(250);const r={...p,id:uid('rem'),status:'scheduled',history:[]};reminders.unshift(r);return r;},
  async updateReminder(id,p){await wait(250);const r=find(id);const {action,...rest}=p;Object.assign(r,rest);if(action){r.status=action;log(r,action);}return {...r};},
  async completeReminder(id){await wait(200);const r=find(id);r.status='completed';log(r,'completed');return {...r};},
  async cancelReminder(id){await wait(200);const r=find(id);r.status='cancelled';log(r,'cancelled');return {...r};},
  async getNotificationPreferences(){await wait(100);return {...notifPrefs};},
  async updateNotificationPreferences(p){await wait(150);Object.assign(notifPrefs,p);return {...notifPrefs};}};
const real={listReminders:async f=>{const rows=await request('/reminders',{query:f});return rows.map(r=>({...r,kind:r.reminder_type,times:[new Date(r.scheduled_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})],frequency:r.recurrence||'once',status:r.active?'scheduled':r.completed_at?'completed':'cancelled',history:[]}));},createReminder:p=>request('/reminders',{method:'POST',body:{title:p.title,reminder_type:p.kind==='followup'?'follow_up':'medication',scheduled_at:`${p.startDate}T${p.times[0]}:00`,recurrence:p.frequency==='once'?null:p.frequency}}),
  updateReminder:(id,p)=>request(`/reminders/${id}`,{method:'PATCH',body:p.action?{active:p.action!=='cancelled'}:p}),completeReminder:id=>request(`/reminders/${id}/complete`,{method:'POST'}),
  cancelReminder:id=>request(`/reminders/${id}`,{method:'DELETE'}),getNotificationPreferences:()=>request('/reminders/preferences'),
  updateNotificationPreferences:p=>request('/reminders/preferences',{method:'PATCH',body:p})};
export default pick(mock,real);
