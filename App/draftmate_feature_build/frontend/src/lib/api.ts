export const api = async <T,>(path:string, init:RequestInit={}):Promise<T> => {
  let response: Response;
  const url = `/api${path}`;
  try {
    response = await fetch(url, init);
  } catch (error) {
    const reason = error instanceof Error ? error.message : 'network error';
    throw new Error(`Cannot reach the local DraftMate API (${url}). ${reason}. Close duplicate DraftMate windows and restart RUN_DRAFTMATE.bat from the latest project folder. Your typed case details have not been cleared.`);
  }
  const type=response.headers.get('content-type')||'';
  if(!response.ok){let message=`Request failed (${response.status})`;try{const body=await response.json();message=body.detail||message}catch{}throw new Error(message)}
  if(type.includes('application/json')) return response.json();
  return response as unknown as T;
};
export const json = (data:unknown):RequestInit => ({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
