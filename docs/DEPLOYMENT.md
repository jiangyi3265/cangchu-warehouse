# 当前线上部署与运维

记录的是 2026-11-16 20:37（America/New_York）的若依上线，UTC 发布标识为 `20261117T012436Z`。本页不包含密码、密钥或业务数据。开发与私密资料交接入口见 [HANDOFF.md](HANDOFF.md)。

## 运行位置

| 项目 | 地址 / 路径 |
| --- | --- |
| 站点 | `https://cangchu.oksja.cn` |
| 主机 | `124.222.244.144`，OpenCloudOS 9.6 |
| 当前版本链接 | `/opt/cangchu-ruoyi/current` |
| 此次发布目录 | `/opt/cangchu-ruoyi/releases/20261117T012436Z` |
| Java 包 / 前端 | 发布目录中的 `backend.jar` / `web/` |
| Java | `127.0.0.1:19474`，通过 Nginx `/dev-api/` 转发并移除前缀 |
| MySQL | `127.0.0.1:13373`，独立数据库 `cangchu_ruoyi` |
| Redis | `127.0.0.1:16373`，独立实例，不与其他站点共用键空间 |
| 配置 | `/etc/cangchu-ruoyi/`，私有运行环境、密码及加密密钥 |
| 业务持久目录 | `/opt/cangchu-ruoyi/shared/` 下的 `mysql/`、`redis/`、`uploads/`、`logs/` |
| Nginx | `/www/server/panel/vhost/nginx/cangchu.oksja.cn.conf` |
| TLS 证书 | `/etc/letsencrypt/live/cangchu.oksja.cn/`；私钥不得提交 Git |
| 运维脚本 | `/opt/cangchu-ruoyi/bin/backup.py`、`health.py`、`rollback.py` |

线上 Java、MySQL、Redis 只监听回环地址，应用由 `cangchu` 系统用户运行。前端 `/static/` 文件使用版本哈希缓存，HTML 禁止持久缓存，Vue 路由回退至 `index.html`。旧 `/api/` 返回升级提示，避免旧页面继续调用 Node 接口。

本站采用 `prod` profile。新库执行若依、Quartz 及 `warehouse_001`–`warehouse_039` 共 41 份 SQL，初始化时共 90 张表，示例 `ry` 用户停用。应用启动不自动建表或升级。

## 服务与日常核对

| 单元 | 用途 |
| --- | --- |
| `cangchu-ruoyi.service` | Java 业务服务 |
| `cangchu-ruoyi-mysql.service` | 独立 MySQL |
| `cangchu-ruoyi-redis.service` | 独立 Redis |
| `cangchu-ruoyi-backup.timer` / `.service` | 每日数据库、配置与上传目录备份 |
| `cangchu-ruoyi-health.timer` / `.service` | 每 5 分钟检查服务、Java/Redis、MySQL 和最近备份 |

上述服务和定时器已设置开机启动。仅查看状态可执行：

```bash
readlink -f /opt/cangchu-ruoyi/current
systemctl status cangchu-ruoyi cangchu-ruoyi-mysql cangchu-ruoyi-redis --no-pager
systemctl list-timers --all --no-pager
journalctl -u cangchu-ruoyi -n 50 --no-pager
```

不要把日志、进程环境或配置原文贴进公开 issue。Java 日志在 `shared/logs`，健康结果在 `/opt/cangchu-ruoyi/shared/health.json`。没有配置外部故障消息接收者。

Java 初始配置使用最大堆 320 MiB、systemd 内存上限 768 MiB；MySQL 上限 512 MiB，Redis 上限 96 MiB。这些是该次部署的资源约束，不是业务容量承诺。共享服务器上有其他站点，调试不能停止或修改其他应用。

## 备份

`cangchu-ruoyi-backup.timer` 使用服务器本地时区，计划时间为每日 04:30，随机延迟最多 5 分钟。部署时服务器时区为 Asia/Shanghai；换算到文档所用 America/New_York 的标准时间是前一日 15:30–15:35，夏令时或服务器时区变化后需重新核对。

备份位置为 `/opt/cangchu-ruoyi/backups/ruoyi-时间戳/`，最近一次索引是 `latest-ruoyi.json`。每份包含：

- `database.sql.gz`：独立库的一致性 SQL 备份。
- `private-config.tar.gz`：私有配置、systemd 和 Nginx，包含密码/加密密钥，必须保持私密。
- `uploads.tar.gz`：上传文件。
- `manifest.json`：版本标识及文件哈希。

数据库使用一致性快照；配置与上传目录随后归档，整个组合不是跨文件的全局原子快照。业务繁忙、迁移或正式回退前应先停止相关写入再备份和核对。

有运维授权时，可执行 `sudo systemctl start cangchu-ruoyi-backup.service` 生成新备份。此动作会创建备份文件，并非只读检查。该脚本目前不自动清理历史备份，需要监控磁盘和制定留存策略。

这次 SQL 在独立临时库恢复验证通过，90 张表与管理员密码哈希核对一致。验证库随后移除。当前备份保存在同一台服务器，还没有异地目标；不能将其描述为已具备异地灾备。

## 旧版保留与回退

旧站服务 `cangchu`、`cangchu-health.timer`、`cangchu-backup.timer` 已停止并取消自启。保留：

- `/opt/cangchu/current` 及原发布目录。
- `/opt/cangchu/shared/warehouse.sqlite`。
- `/etc/cangchu/` 原配置和旧网站登录资料。
- `/opt/cangchu-ruoyi/backups/before-ruoyi-20261117T012436Z/` 中的最终 SQLite 快照、原 Nginx、原服务与配置。

检查回退文件是否存在：

```bash
sudo python3 /opt/cangchu-ruoyi/bin/rollback.py
```

这只是前置文件检查，不会切换网站，也不是完整回退演练。确实决定回退时才使用：

```bash
sudo python3 /opt/cangchu-ruoyi/bin/rollback.py --execute
```

执行会停止新版应用与定时器、备份若依数据、启动旧服务、恢复旧 Nginx 配置并重载，再恢复旧站定时器。新版 MySQL/Redis 及其数据保留；新增的若依业务不会自动合并回旧 SQLite。已经录入真实业务后，应先明确两边数据处理方案，不能把恢复旧页面当成业务无损回退。

脚本针对本次发布和原 Node 版本。未来数据库或目录变化后需重新核对，不能当成通用回退器。源码快照见 [ops/rollback.py](../ops/rollback.py)。

## 后续发布

开发者先完成本地构建和与修改相符的检查，记录后端/前端提交、JAR 哈希及 SQL 版本。发布前核对当前服务与备份，使用新发布目录和私有运行配置，不覆盖旧版证据，不重复执行空库初始化。

前端可用 `npm ci`、`npm run test:warehouse`、`npm run build:prod`；后端使用 `mvn -B -ntp verify`。构建时不得把密码写进 `VITE_*` 变量，前端变量会进入浏览器代码。应用环境变量契约见 [BACKEND-CONTRACT.md](https://github.com/jiangyi3265/cangchu-backend/blob/main/BACKEND-CONTRACT.md)。

此次可公开的服务单元、Nginx 与脚本副本在 [ops](../ops/README.md)。私有数据库/Redis配置和服务器凭据需另外取得，仓库没有一键重建生产数据库的入口。更改生产或连接真实平台，按用户当次授权范围执行并记录。

## 本次验证与边界

真实线上验证码登录、18 个只读 API、18 个仓储菜单、中英文和手机布局检查通过；没有写入测试业务。新业务库初始为空，旧库 62 张表与最终备份一致。未修改客户 Mintsoft，也未连接真实店铺或快递。

这次完成本站若依版本发布，完整替换条件仍见 [REPLACEMENT_ACCEPTANCE.md](REPLACEMENT_ACCEPTANCE.md)。运行和业务范围的后续变化应同步更新本页、交接入口和发布标识。
