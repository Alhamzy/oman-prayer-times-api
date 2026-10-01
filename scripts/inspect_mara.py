import requests
u="https://www.mara.gov.om/calendar_page2.asp"
r=requests.get(u,headers={"User-Agent":"Mozilla/5.0"},timeout=30,verify=False)
print("STATUS",r.status_code,"URL",r.url)
print(r.text[:30000])
