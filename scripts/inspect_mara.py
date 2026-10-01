import requests,re
u="https://www.mara.gov.om/calendar_page2.asp"
r=requests.get(u,headers={"User-Agent":"Mozilla/5.0"},timeout=30,verify=False)
print("STATUS",r.status_code,"URL",r.url)
html=r.text
for i,m in enumerate(re.finditer(r"<form\\b[\\s\\S]*?</form>",html,re.I)):
    form=m.group(0)
    print("FORM",i)
    tag=re.search(r"<form\\b[^>]*>",form,re.I)
    print(tag.group(0) if tag else "")
    for sm in re.finditer(r"<select\\b[^>]*>[\\s\\S]*?</select>",form,re.I):
        print("SELECT",sm.group(0)[:12000])
    for im in re.finditer(r"<input\\b[^>]*>",form,re.I):
        print("INPUT",im.group(0))
