# 运维文件快照

这里保存 `20261117T012436Z` 若依发布实际使用的非敏感文件，便于接手者查看、审查和维护。运行位置与步骤见 [部署文档](../docs/DEPLOYMENT.md)，项目入口见 [交接文件](../docs/HANDOFF.md)。

| 文件 | 服务器用途 |
| --- | --- |
| `backup.py` | `/opt/cangchu-ruoyi/bin/backup.py`，创建 SQL、私有配置和上传目录备份 |
| `health.py` | `/opt/cangchu-ruoyi/bin/health.py`，健康检查并写入报告 |
| `rollback.py` | `/opt/cangchu-ruoyi/bin/rollback.py`，核对或按明确参数回退此次部署 |
| `systemd/` | `/etc/systemd/system/` 中本项目的服务与定时器 |
| `nginx/cangchu.oksja.cn.conf` | 本站 HTTPS、静态文件和 Java API 反向代理 |

脚本包含本次服务器路径，需要相应 Linux 环境和私有配置才能运行。**不要在新电脑或 CI 中把这些脚本当测试直接执行，也不要无检查地覆盖正在运行的服务器配置。**

仓库没有保存 `/etc/cangchu-ruoyi/app.env`、`credentials.json`、带密码的 MySQL/Redis 配置、TLS 私钥或备份内容。备份脚本会归档这些私有材料，因此它产生的文件也不能提交 Git。

这里只提交脚本源文件和服务结构，没有提交 Node 旧代码、依赖目录、JAR、前端构建目录、日志、业务 SQL 导出或测试账号。旧版回退目标仍保存在服务器和项目所有者的私有备份中。
