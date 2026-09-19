// Carry a shared collection selection back from a standalone evidence dossier.
// Only a query is accepted; the destination is always the local catalogue.
const selection=new URLSearchParams(location.search).get('from');
if(selection?.startsWith('?') && selection.length<2000) {
  const query=new URLSearchParams(selection).toString();
  const back=document.querySelector('.back-link');
  if(back) {back.href=`../catalogue.html?${query}#explore`;back.textContent='← Back to your collection view';}
}
