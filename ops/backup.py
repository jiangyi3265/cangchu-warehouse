#!/usr/bin/python3
from pathlib import Path
import datetime,subprocess,gzip,os,json,hashlib,tarfile
base=Path('/opt/cangchu-ruoyi');cfg=Path('/etc/cangchu-ruoyi')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
target=base/'backups'/('ruoyi-'+stamp);target.mkdir(mode=0o700)
raw=target/'database.sql'
with raw.open('xb') as out:
 os.chmod(raw,0o600)
 result=subprocess.run(['/www/server/mysql/bin/mysqldump','--defaults-extra-file='+str(cfg/'mysql-root.cnf'),'--single-transaction','--no-tablespaces','--set-gtid-purged=OFF','--routines','--triggers','--events','--hex-blob','cangchu_ruoyi'],stdout=out,stderr=subprocess.PIPE)
if result.returncode:raise RuntimeError('MySQL backup failed')
archive=target/'database.sql.gz'
with raw.open('rb') as src,gzip.open(archive,'wb') as dst:
 while chunk:=src.read(1024*1024):dst.write(chunk)
os.chmod(archive,0o600)
sqlHash=hashlib.sha256(raw.read_bytes()).hexdigest()
assert hashlib.sha256(gzip.decompress(archive.read_bytes())).hexdigest()==sqlHash
raw.unlink()
with tarfile.open(target/'private-config.tar.gz','w:gz') as tar:
 tar.add(cfg,arcname='etc/cangchu-ruoyi')
 tar.add('/www/server/panel/vhost/nginx/cangchu.oksja.cn.conf',arcname='nginx/cangchu.oksja.cn.conf')
 for p in Path('/etc/systemd/system').glob('cangchu-ruoyi*'):tar.add(p,arcname='systemd/'+p.name)
os.chmod(target/'private-config.tar.gz',0o600)
uploads=base/'shared/uploads'
with tarfile.open(target/'uploads.tar.gz','w:gz') as tar:tar.add(uploads,arcname='uploads')
os.chmod(target/'uploads.tar.gz',0o600)
proof={'createdAt':stamp,'release':str((base/'current').resolve()),'database':'cangchu_ruoyi','uncompressedSqlSha256':sqlHash,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}}
(target/'manifest.json').write_text(json.dumps(proof,indent=2));os.chmod(target/'manifest.json',0o600)
latest=base/'backups/latest-ruoyi.json';temp=latest.with_suffix('.tmp');temp.write_text(json.dumps({'directory':str(target),**proof},indent=2));os.chmod(temp,0o600);os.replace(temp,latest)
print(json.dumps({'backup':str(target),'compressedIntegrity':'ok','sqlSha256':sqlHash}))
