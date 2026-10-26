import {pick,request,requestBlob} from './apiClient.js';import {profile,healthSummary,records,shares,wait,uid} from '../mocks/data.js';
const mock={
  async getPatientProfile(){await wait();return {...profile};},
  async getHealthSummary(){await wait();return healthSummary;},
  async listMedicalRecords(f={}){await wait(200);const q=(f.q||'').toLowerCase();
    return records.filter(r=>(!f.category||f.category==='all'||r.category===f.category)&&(!q||r.title.toLowerCase().includes(q))).map(r=>({...r}));},
  async getMedicalRecord(id){await wait(200);const r=records.find(x=>x.id===id);if(!r)throw new Error('Record not found');return {...r};},
  async uploadMedicalRecord(file,meta,{onProgress}={}){for(let i=1;i<=5;i++){await wait(200);onProgress?.(i*20);}
    const r={id:uid('rec'),title:meta.title||file.name,category:meta.category,date:meta.date,origin:'patient',fileType:file.type,size:file.size,notes:'Held in browser memory only (demo).'};records.unshift(r);return r;},
  async updateMedicalRecord(id,p){await wait(200);const r=records.find(x=>x.id===id);Object.assign(r,p);return {...r};},
  async deleteMedicalRecord(id){await wait(200);const i=records.findIndex(x=>x.id===id);if(i>=0)records.splice(i,1);return {ok:true};},
  async listShares(){await wait(150);return shares.map(s=>({...s}));},
  async createShareRequest(p){await wait(300);const s={id:uid('share'),recipient:p.recipient,recordIds:p.recordIds,createdAt:new Date().toISOString(),expiresAt:p.expiresAt,status:'active'};shares.unshift(s);return s;},
  async revokeShare(id){await wait(200);const s=shares.find(x=>x.id===id);if(s)s.status='revoked';return {...s};}};
const real={
  getPassport:()=>request('/patients/me/passport'),
  downloadPassport:()=>requestBlob('/patients/me/passport.pdf'),
  getPatientProfile:()=>request('/patients/me').then(p=>({...p,name:p.full_name,age:'',sex:'',lastUpdated:null})),
  getHealthSummary:()=>request('/patients/me/health-summary').then(s=>({...s,conditions:[...new Set(s.conditions||[])],allergies:[...new Set(s.allergies||[])],medications:[...new Set(s.medications||[])],vaccinations:s.vaccinations||[],aiSummary:s.aiSummary||{text:'No generated summary is available.',sources:[]}})),
  listMedicalRecords:f=>request('/patients/me/records',{query:f}).then(rows=>rows.map(r=>({...r,date:r.created_at,origin:'patient',fileType:r.file_path?'document':'metadata',size:0,notes:r.details||''}))),getMedicalRecord:id=>request(`/patients/me/records/${id}`).then(r=>({...r,date:r.created_at,origin:'patient',fileType:r.file_path?'document':'metadata',size:0,notes:r.details||''})),
  uploadMedicalRecord:(file,meta)=>{const fd=new FormData();fd.append('file',file);fd.append('category',meta.category);fd.append('title',meta.title||file.name);return request('/patients/me/records/upload',{method:'POST',form:fd,timeout:60000});},
  updateMedicalRecord:(id,p)=>request(`/patients/me/records/${id}`,{method:'PATCH',body:{category:p.category||'other',title:p.title,details:p.notes||p.details||''}}),deleteMedicalRecord:id=>request(`/patients/me/records/${id}`,{method:'DELETE'}),
  listShares:()=>request('/patients/me/shares').then(rows=>rows.map(s=>({...s,recordIds:[s.record_id],recipient:s.doctor_id,status:s.revoked?'revoked':'active',expiresAt:s.expires_at}))),
  createShareRequest:p=>request('/patients/me/shares',{method:'POST',query:{record_id:p.recordIds[0],doctor_id:p.doctorId||p.recipient,expires_at:p.expiresAt}}),revokeShare:id=>request(`/patients/me/shares/${id}`,{method:'DELETE'})};
export default pick(mock,real);
