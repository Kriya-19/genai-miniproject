import {pick,request,setToken} from './apiClient.js';import {user,wait} from '../mocks/data.js';
let signedIn=true;
const mock={async getCurrentUser(){await wait(100);return signedIn?{...user}:null;},async signIn(){await wait(150);signedIn=true;return {...user};},async signOut(){await wait(100);signedIn=false;setToken(null);return {ok:true};}};
const real={
  getCurrentUser:()=>request('/auth/me').then(u=>({...u,name:u.full_name})),
  signIn:p=>request('/auth/login',{method:'POST',body:p}).then(r=>{setToken(r.access_token);return {...r.user,name:r.user.full_name};}),
  register:p=>request('/auth/register',{method:'POST',body:p}).then(r=>{setToken(r.access_token);return {...r.user,name:r.user.full_name};}),
  signOut:()=>request('/auth/logout',{method:'POST'}).finally(()=>setToken(null))
};
export default pick(mock,real);
