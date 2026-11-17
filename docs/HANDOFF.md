# 海外仓储项目开发与部署交接

更新时间：2026-11-16（America/New_York）。本文件是接手项目的入口，可以直接发给下一位开发者或开发助手。线上发布的机器标识使用 UTC，因此发布目录中的日期为 `20261117`。

## 先了解现在的情况

目标是用若依 Vue 3 + Java Spring Boot 逐步接替 Mintsoft 的海外仓业务，包括入库、库存、订单、计费，以及电商和快递连接。当前已完成本站版本切换，完整业务替换仍在推进。

| 项目 | 当前情况 |
| --- | --- |
| 网站及域名 | [https://cangchu.oksja.cn](https://cangchu.oksja.cn) |
| 服务器 | `124.222.244.144`，OpenCloudOS 9.6；SSH 端口 `22` |
| 线上架构 | Nginx HTTPS + Vue 3 静态文件 + Java 17 / Spring Boot + MySQL 8.0.45 + 独立 Redis |
| 上线时间 | 2026-11-16 20:37:06，America/New_York；UTC 为 2026-11-17 01:37:06 |
| 业务数据 | 上线时按用户要求初始化为空白业务库，没有导入旧演示数据或本地测试数据；接手时需重新核对当前数据状态 |
| 旧版 | Node / SQLite 服务已停止且取消自启，程序和数据库完整保留用于回退 |
| 网站账号 | 管理员用户名 `admin`；密码已单独初始化，不是若依默认密码，也不是旧站密码 |
| 第三方连接 | 上线时店铺连接为空、快递外部调用关闭，没有进行真实店铺/快递联调 |
| 参考系统 | [Mintsoft 登录入口](https://om.mintsoft.co.uk/UserAccount/LogOn?signInOptions=false)；客户生产系统，账号通过私密渠道提供 |

## 代码在哪里

| 项目 | 用途 | GitHub |
| --- | --- | --- |
| cangchu-warehouse | 本交接文档、迁移记录、验收范围与运维资料 | [cangchu-warehouse](https://github.com/jiangyi3265/cangchu-warehouse) |
| cangchu-backend | 若依 Java 后端、仓储业务、SQL 迁移与测试 | [cangchu-backend](https://github.com/jiangyi3265/cangchu-backend) |
| cangchu-admin | 若依 Vue 3 管理后台、双语界面与前端测试 | [cangchu-admin](https://github.com/jiangyi3265/cangchu-admin) |

三个仓库公开、默认分支均为 `main`，在同一个工作目录下并列放置。没有第三套独立 App 或小程序。旧工作区的 `mintsoft-local` 和 `版本备份` 属于历史资料，后续开发以这三个仓库为准。

```bash
git clone https://github.com/jiangyi3265/cangchu-warehouse.git
git clone https://github.com/jiangyi3265/cangchu-backend.git
git clone https://github.com/jiangyi3265/cangchu-admin.git
```

实际已上线版本固定在 [deployed-release.json](deployed-release.json)，不要把将来 `main` 的最新提交自动视为已部署。

| 代码 | 此次上线提交 |
| --- | --- |
| 后端 | `06de9ba3b42fc35a7d4f35aef7826e576d89860e` |
| 前端 | `9c305985c275b83f011717117f87e127052411a6` |
| 发布目录 | `/opt/cangchu-ruoyi/releases/20261117T012436Z` |

## 新电脑怎么启动

准备 Git、Java 17、Maven、Python 3.10+、MySQL 8、Redis、Node.js / npm。已验证的前端工具链为 Node.js 24。Node 只负责 Vue 开发和构建，后端无需旧 Node 服务。MySQL 需要支持实际执行的 CHECK 约束，至少 8.0.16。

1. 在新电脑建立独立 MySQL 实例 `127.0.0.1:13306`，创建空数据库 `warehouse_local`，以及仅对该库有权限的非 root 开发账号。首次初始化需要建表和迁移权限；不要使用线上库。另准备本地 Redis `127.0.0.1:16379`。
2. 把 MySQL `[client]` 配置放在三个仓库的共同父目录以外。配置需包含 `host=127.0.0.1`、`port=13306`、本地用户名和密码。文件不得提交 Git。
3. 在后端目录构建；构建成功会生成初始化工具需要的 JAR。

```bash
cd cangchu-backend
mvn -B -ntp verify
```

4. 在当前终端环境设置自己生成的 `LOCAL_ADMIN_PASSWORD`（16–20 个字符），然后仅对空本地库初始化。命令里的路径需要换成私有 MySQL 配置的绝对路径。

```bash
python tools/initialize-local.py --mysql-config /absolute/private/mysql-client.cnf
```

工具仅允许 `127.0.0.1:13306/warehouse_local`，拒绝非空库。若要沿用原开发数据，应通过私密备份恢复，并核对迁移状态，不能再次运行空库初始化。

5. 在启动 Java 的终端中设置以下环境变量，然后启动后端。它不会自动读取 `.env`。

| 变量 | 设置方式 |
| --- | --- |
| `SPRING_PROFILES_ACTIVE` | `local` |
| `LOCAL_DB_USERNAME`、`LOCAL_DB_PASSWORD` | 上面独立本地 MySQL 的账号密码 |
| `LOCAL_TOKEN_SECRET` | 新生成的至少 32 随机字节密钥 |
| `LOCAL_REDIS_PASSWORD` | 自己配置的本地 Redis 密码；仅隔离本地实例可留空 |
| `WAREHOUSE_LOG_PATH` | 仓库外的私有日志目录 |
| `LOCAL_UPLOAD_PATH` | 仓库外的上传目录 |

```bash
java -jar ruoyi-admin/target/ruoyi-admin.jar
```

6. 另开终端进入前端目录。

```bash
cd cangchu-admin
npm ci
npm run dev
```

访问 `http://127.0.0.1:5174`，Java 在 `http://127.0.0.1:18080`。使用 `admin` 和自己初始化的密码、页面验证码登录。本地接口前缀是 `/dev-api`。需要验证前端时执行 `npm run test:warehouse` 和 `npm run build:prod`。

细节以 [后端 README](https://github.com/jiangyi3265/cangchu-backend#快速启动)、[前端 README](https://github.com/jiangyi3265/cangchu-admin#快速启动)、[接口契约](https://github.com/jiangyi3265/cangchu-backend/blob/main/BACKEND-CONTRACT.md) 为准。

## 线上怎么接手

完整路径、服务、备份和回退说明见 [DEPLOYMENT.md](DEPLOYMENT.md)。取得项目所有者提供的 SSH 登录方式后，先核对当前发布、服务状态和备份日期。没有必要为了接手代码重新初始化线上数据库或重跑发布脚本。

```bash
readlink -f /opt/cangchu-ruoyi/current
systemctl status cangchu-ruoyi cangchu-ruoyi-mysql cangchu-ruoyi-redis --no-pager
systemctl list-timers --all --no-pager
```

运维脚本、服务单元和 Nginx 配置的非敏感副本已放在 [ops](../ops/README.md)。这些是此次部署的运行快照，不是可以任意重复执行的首次安装器。

## 需要单独私密交接的资料

公开 GitHub 可以交接代码、文档和配置结构，不能代替凭据或业务资料交接。**下面文件只列位置，没有上传内容。**

| 资料 | 现有位置 / 获取方式 |
| --- | --- |
| SSH 登录方式、Mintsoft 登录信息 | 向项目所有者取得；不要把账号密码贴入 issue、README 或 Git 提交 |
| 当前网站管理员密码 | 服务器 `/etc/cangchu-ruoyi/access.txt`；由项目所有者私下提供 |
| Java 运行环境及加密密钥 | `/etc/cangchu-ruoyi/app.env`、`/etc/cangchu-ruoyi/credentials.json` |
| MySQL / Redis 私有配置 | `/etc/cangchu-ruoyi/` 中的客户端及服务配置；保持私有文件权限 |
| 最新线上备份索引 | `/opt/cangchu-ruoyi/backups/latest-ruoyi.json`，指向 SQL、配置和上传目录备份 |
| 本次切换交接压缩包 | 服务器 `/opt/cangchu-ruoyi/backups/deployment-handoff-private.tar.gz`；它是切换时的快照，不保证包含后续业务数据 |
| 原电脑交接文件 | 原工作区 `.github-import-private/换电脑开发交接-私密.txt` |
| 原电脑私密备份 | 原工作区 `.ruoyi-migration-private/deploy-ruoyi-online/线上切换备份-私密.tar.gz` |
| 原电脑本地开发环境 | `.ruoyi-migration-private/runtime-config.json` 及独立 MySQL 开发库备份；运行配置不是数据库备份 |
| 原始需求与客户资料 | `FULFILMENT MINTSOFT.docx`、原工作区 `调研记录` 和客户报价/账单，由所有者按需提供 |

原电脑工作区是 `D:\项目\新项目未完成\海外仓储`；新电脑可以使用自己的路径。上面的本地路径只方便定位旧资料，不是新电脑的固定要求。

如果恢复带有平台凭据的数据库，必须同时保留对应加密密钥；随意重新生成密钥会导致已保存凭据无法解密。服务器 SSH 密码、网站密码、Mintsoft 密码、本地开发密码各不相同。

## 已实现什么，接下来做什么

已经迁入 Java 的主要业务包括七类主数据、ASN 收货和隔离异常处理、库存来源层与盘点、手工订单扫码和多箱装箱、退货、订单数阶梯和其他收费规则、账单及调整审批。WooCommerce 订单读取和仓库接单、DPD UK / DPD Local UK 建单与原始 ZPL 面单已有本地协议验证。

下一阶段不能漏掉：

- DPD 实物交运、库存与费用提交、追踪/取消、未知结果核对，以及平台回传。
- WooCommerce 库存/发货回写；eBay、Amazon、Shopify 和验收表所列其他来源的 Java 适配、授权及真实联调。
- DHL、Royal Mail、DX、Evri 及验收表列出的其他快递。不同区域/产品 API 需要分别确认。
- 剩余仓内异常、组合商品/拆合单/波次、客户门户等业务。
- 客户完整报价表、真实账单、现场设备和实际岗位验收。收费阶梯已明确按**订单数**分档，不按商品件数替代。
- 历史数据映射、导入、对账和正式接替 Mintsoft；异地备份与故障通知尚无实际接收服务，不能声称已启用。

完整范围在 [替换验收表](REPLACEMENT_ACCEPTANCE.md)，按模块查看 [迁移记录](RUOYI_MIGRATION.md)。历史记录中的“尚未上线”指当时开发阶段，当前本站部署以本交接和部署文档为准；本站上线不等于已完成客户 Mintsoft 的全部业务切换。

## 这次验证到什么程度

上线使用的源码已有 494 项 Java 测试、69 项前端测试和生产构建记录。发布前逐个 Git 文件核对了构建来源；上线后检查了真实验证码登录、18 个只读 API、18 个仓储菜单、中英文切换、390px 手机布局与退出登录，没有发现页面或请求错误。

旧 SQLite 备份通过完整性检查，62 张表与停机时的原库逐表一致。新 MySQL 备份在临时库恢复了 90 张表，管理员密码哈希相同。没有执行线上新旧版本来回切换演练，也没有通过这次页面检查声称全部业务完成。

可以把下面这句话直接交给接手的人：

> 请先读 https://github.com/jiangyi3265/cangchu-warehouse/blob/main/docs/HANDOFF.md ，按关联仓库接手若依海外仓储项目。先核对当前状态和未完成清单；需要登录线上系统或恢复数据时，使用项目所有者另外提供的私密资料。
