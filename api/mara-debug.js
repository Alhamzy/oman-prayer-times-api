module.exports = async function handler(req,res){
  try{
    const r = await fetch('https://www.mara.gov.om/calendar_page2.asp',{headers:{'user-agent':'Mozilla/5.0'}});
    const html = await r.text();
    const forms = [...html.matchAll(/<form[\s\S]*?<\/form>/gi)].map(m=>m[0]).join('\n\n');
    res.setHeader('content-type','text/plain; charset=utf-8');
    res.status(200).send(forms || html.slice(0,20000));
  }catch(e){
    res.status(500).json({error:String(e&&e.message||e)});
  }
};