export const api = async <T,>(path:string, init:RequestInit={}):Promise<T> => {
  const response = await fetch(`/api${path}`, init);
  const type=response.headers.get('content-type')||'';
  if(!response.ok){let message=`Request failed (${response.status})`;try{const body=await response.json();message=body.detail||message}catch{}throw new Error(message)}
  if(type.includes('application/json')) return response.json();
  return response as unknown as T;
};
export const json = (data:unknown):RequestInit => ({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
