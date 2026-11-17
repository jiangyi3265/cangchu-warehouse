#!/usr/bin/python3
from pathlib import Path
import subprocess,json,sys,os,datetime,urllib.request
base=Path('/opt/cangchu-ruoyi');backup=base/'backups/before-ruoyi-20261117T012436Z'
nginx=Path('/www/server/panel/vhost/nginx/cangchu.oksja.cn.conf')
assert (backup/'nginx.conf').is_file() and (backup/'warehouse.sqlite').is_file()
assert Path('/opt/cangchu/current/server.mjs').is_file()
if sys.argv[1:]!=['--execute']:
 print('Rollback prerequisites are present. To switch back, run this script as root with --execute. New RuoYi data will be backed up and preserved, not merged into the old application.');sys.exit(0)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
current=nginx.read_bytes();(base/'backups'/('nginx-before-rollback-'+stamp+'.conf')).write_bytes(current)
subprocess.run(['systemctl','stop','cangchu-ruoyi-health.timer','cangchu-ruoyi-backup.timer','cangchu-ruoyi'],check=True)
try:
 subprocess.run(['/usr/bin/python3',str(base/'bin/backup.py')],check=True)
 subprocess.run(['systemctl','start','cangchu'],check=True)
 import time
 for _ in range(30):
  try:
   with urllib.request.urlopen('http://127.0.0.1:19473/api/health',timeout=3) as r:
    if r.status==200:break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Legacy service did not become healthy')
 temp=nginx.with_suffix('.rollback');temp.write_bytes((backup/'nginx.conf').read_bytes());os.chmod(temp,0o644);os.replace(temp,nginx)
 subprocess.run(['/usr/bin/nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'],check=True)
 subprocess.run(['systemctl','disable','cangchu-ruoyi','cangchu-ruoyi-health.timer','cangchu-ruoyi-backup.timer'],check=True)
 subprocess.run(['systemctl','enable','--now','cangchu','cangchu-health.timer','cangchu-backup.timer'],check=True)
 print('Rolled back website to preserved Node release. RuoYi database and backups retained. No new RuoYi business data has been replayed to legacy.')
except Exception:
 nginx.write_bytes(current)
 subprocess.run(['/usr/bin/nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
 subprocess.run(['systemctl','start','cangchu-ruoyi','cangchu-ruoyi-health.timer','cangchu-ruoyi-backup.timer'])
 raise
