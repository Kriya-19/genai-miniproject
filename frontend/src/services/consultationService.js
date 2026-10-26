import {pick,request} from './apiClient.js';import {consultations,doctors,wait,uid} from '../mocks/data.js';
const mock={
  async listConsultations(){await wait();return {items:[...consultations],doctors};},
  async getConsultation(id){await wait();const c=consultations.find(x=>x.id===id);if(!c)throw new Error('Consultation not found');return c;},
  async createConsultation(p){await wait();const d=doctors.find(x=>x.id===p.doctorId);
    const c={id:uid('con'),doctor:d.name,specialty:d.specialty,scheduledAt:p.slot,type:p.type,status:'scheduled',reason:p.reason||'',caseId:p.shareCaseId||null};consultations.unshift(c);return c;},
  async getJoinDetails(id){await wait();return {consultation_id:id,room:'demo-room',demo:true,ice_servers:[]};},
  async cancelConsultation(id){await wait();const c=consultations.find(x=>x.id===id);if(c)c.status='cancelled';return c;}};
const normalize=c=>({...c,doctor:c.doctor_name||'Assigned clinician',specialty:'Healthcare consultation',scheduledAt:c.scheduled_at,status:c.status==='requested'?'scheduled':c.status,type:c.video_provider?'video':'audio',reason:c.notes||'',caseId:null});
const real={
  listConsultations:async()=>{const [items,available]=await Promise.all([request('/consultations'),request('/doctors')]);const byId=Object.fromEntries(available.map(d=>[d.id,d]));return {items:items.map(c=>normalize({...c,doctor_name:byId[c.doctor_id]?.name})),doctors:available};},
  getConsultation:id=>request(`/consultations/${id}`).then(normalize),
  createConsultation:p=>request('/consultations',{method:'POST',body:{scheduled_at:p.slot,doctor_id:p.doctorId||null,notes:p.reason||''}}).then(normalize),
  getJoinDetails:id=>request(`/consultations/${id}/join`),
  updateStatus:(id,status,notes='')=>request(`/consultations/${id}/status`,{method:'PATCH',body:{status,notes}}),
  cancelConsultation:id=>request(`/consultations/${id}`,{method:'DELETE'})};
export default pick(mock,real);
