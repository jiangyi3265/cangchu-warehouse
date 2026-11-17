#!/usr/bin/python3
from pathlib import Path
import json,subprocess,urllib.request,os,datetime,sys
base=Path('/opt/cangchu-ruoyi');cfg=Path('/etc/cangchu-ruoyi');result={}
for service in ('cangchu-ruoyi','cangchu-ruoyi-mysql','cangchu-ruoyi-redis'):
 result[service]=subprocess.run(['systemctl','is-active','--quiet',service]).returncode==0
try:
 with urllib.request.urlopen('http://127.0.0.1:19474/captchaImage',timeout=10) as response:
  data=json.loads(response.read());result['javaRedisReady']=response.status==200 and data.get('code')==200 and data.get('captchaEnabled') is True
except Exception:result['javaRedisReady']=False
q=subprocess.run(['/www/server/mysql/bin/mysql','--defaults-extra-file='+str(cfg/'mysql-root.cnf'),'-NBe','SELECT 1;','cangchu_ruoyi'],capture_output=True,text=True)
result['mysqlReady']=q.returncode==0 and q.stdout.strip()=='1'
latest=base/'backups/latest-ruoyi.json'
result['recentBackup']=latest.exists() and datetime.datetime.now().timestamp()-latest.stat().st_mtime<36*3600
ok=all(result.values());report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':ok,'checks':result}
out=base/'shared/health.json';temp=out.with_suffix('.tmp');temp.write_text(json.dumps(report,indent=2));os.chmod(temp,0o640);os.replace(temp,out)
print(json.dumps(report));sys.exit(0 if ok else 1)
