// Map rendering lives in the page/components, separate from search. Swap the mock for a real places provider via the backend.
import {pick,request} from './apiClient.js';import {clinics,wait} from '../mocks/data.js';
export const distanceKm=(a,b)=>{const t=x=>x*Math.PI/180,dLa=t(b.lat-a.lat),dLo=t(b.lng-a.lng);
  const h=Math.sin(dLa/2)**2+Math.cos(t(a.lat))*Math.cos(t(b.lat))*Math.sin(dLo/2)**2;return +(12742*Math.asin(Math.sqrt(h))).toFixed(1);};
export const getLocation=()=>new Promise((res,rej)=>{if(!navigator.geolocation)return rej(new Error('Geolocation is not supported'));
  navigator.geolocation.getCurrentPosition(p=>res({lat:p.coords.latitude,lng:p.coords.longitude}),e=>rej(new Error(e.code===1?'Location permission denied':'Could not determine location')),{timeout:10000});});
const directions=c=>`https://www.google.com/maps/dir/?api=1&destination=${c.lat},${c.lng}`;
const mock={
  async searchClinics(f={}){await wait(400);const q=(f.q||'').toLowerCase();
    let list=clinics.filter(c=>(!f.type||f.type==='all'||c.type===f.type)&&(!f.specialty||f.specialty==='all'||c.specialties.includes(f.specialty))&&(!q||(c.name+c.address).toLowerCase().includes(q)));
    list=list.map(c=>({...c,distanceKm:f.lat!=null?distanceKm({lat:f.lat,lng:f.lng},c):null}));
    if(f.lat!=null)list=list.filter(c=>c.distanceKm<=(f.radiusKm||50)).sort((a,b)=>a.distanceKm-b.distanceKm);return list;},
  async getClinic(id){await wait(200);const c=clinics.find(x=>x.id===id);if(!c)throw new Error('Facility not found');return c;},
  getDirectionsUrl:directions};
const real={
  searchClinics:async f=>{
    if(f.lat==null||f.lng==null)return [];
    const response=await request('/clinics',{query:{latitude:f.lat,longitude:f.lng,radius_km:f.radiusKm},timeout:60000});
    return {items:(response.clinics||[]).map(c=>({...c,id:c.id,type:c.amenity||c.healthcare||'clinic',lat:Number(c.latitude),lng:Number(c.longitude),distanceKm:distanceKm({lat:f.lat,lng:f.lng},{lat:Number(c.latitude),lng:Number(c.longitude)}),specialties:[],phone:c.phone||''})),message:response.message||'',provider:response.provider};
  },
  getClinic:id=>request(`/clinics/${id}`),getDirectionsUrl:directions
};
export default pick(mock,real);
