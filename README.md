# cangchu-warehouse · 海外仓储项目总览

**接手项目先读：[开发与部署交接文件](docs/HANDOFF.md)**。这个入口包含三个代码仓库、换电脑启动步骤、线上部署位置、备份回退方法和剩余工作。可以直接把该文件的 GitHub 链接交给下一位开发者。

线上站点：[cangchu.oksja.cn](https://cangchu.oksja.cn)。2026-11-16 20:37（America/New_York）已切换到若依 Vue 3 + Java，按用户要求使用空白业务库，旧 Node 版本及数据保留备份。密码、密钥、数据库备份通过私密渠道交接，不在这个公开仓库中。

海外仓储系统的项目说明、迁移记录和替换验收文档，关联独立的 Java 后端与 Vue 3 管理后台。

## 项目简介

项目基于若依建设入库、库存、订单履约、退货和财务计费能力，目标是逐步接替当前 Mintsoft 业务。本仓库负责项目总览和验收依据，源代码分别由 `cangchu-backend` 和 `cangchu-admin` 管理；当前没有独立 App 或小程序项目。

已实现七类主数据、ASN 分批收货及隔离处理、库存来源与盘点、订单逐件扫码与多箱装箱、隔离退货、收费预览与账单调整。WooCommerce 读取与仓库接单、DPD 英国建单与原始面单已有本地验证。本站若依版本已经上线；真实账号联调、实物交运、平台回传、其他平台/快递、客户历史数据迁移及 Mintsoft 业务正式接替仍需继续验收。

完整边界见 [替换验收表](docs/REPLACEMENT_ACCEPTANCE.md)，模块证据与操作记录见 [迁移记录](docs/RUOYI_MIGRATION.md)，线上运行资料见 [部署与运维](docs/DEPLOYMENT.md)。本次交接文档提交没有再次修改线上服务或数据。

## 技术栈

| 子项目 | 实际技术栈 |
| --- | --- |
| cangchu-backend | Java 17、Spring Boot 3.5、Spring Security、MyBatis、Spring JDBC、MySQL 8、Redis、Maven、JUnit 5 |
| cangchu-admin | Vue 3、JavaScript、Vite 6、Element Plus、Pinia、Vue Router、Axios、Sass |
| cangchu-warehouse | Markdown 文档、JSON 仓库索引，无独立运行服务 |

Node.js / npm 仅用于 Vue 前端工具链；当前应用后端为 Java。各版本以对应仓库的 `pom.xml`、`package.json` 和锁文件为准。

## 关联仓库

| 项目 | 说明 | GitHub |
| --- | --- | --- |
| cangchu-warehouse | 项目总览、迁移记录与替换验收文档 | [cangchu-warehouse](https://github.com/jiangyi3265/cangchu-warehouse) |
| cangchu-backend | Java / Spring Boot 后端服务 | [cangchu-backend](https://github.com/jiangyi3265/cangchu-backend) |
| cangchu-admin | Vue 3 仓储管理后台 | [cangchu-admin](https://github.com/jiangyi3265/cangchu-admin) |

## 快速启动

三个仓库使用同一工作区下的并列目录。已有目录请直接进入使用，无须再次克隆。

```bash
git clone https://github.com/jiangyi3265/cangchu-warehouse.git
git clone https://github.com/jiangyi3265/cangchu-backend.git
git clone https://github.com/jiangyi3265/cangchu-admin.git
```

三个仓库各自独立，均使用 `main`；总览仓库只保存文档及仓库索引，不重复提交前后端源码。

后端先阅读 [启动与数据库初始化说明](https://github.com/jiangyi3265/cangchu-backend#快速启动)，配置独立 MySQL、Redis 和私有进程环境，再构建并启动：

```bash
cd cangchu-backend
mvn -B -ntp verify
java -jar ruoyi-admin/target/ruoyi-admin.jar
```

在另一个终端进入前端目录：

```bash
cd cangchu-admin
npm ci
npm run dev
```

前端开发地址为 `http://127.0.0.1:5174`，代理至本地 Java `http://127.0.0.1:18080`。数据库不会随应用自动建表；初始化工具只处理指定的空本地库，已有库按编号迁移。真实凭据只配置在仓库外，不提交 `.env`、数据库备份、运行日志或测试私有材料。

更多运行细节见 [后端 README](https://github.com/jiangyi3265/cangchu-backend#readme) 和 [前端 README](https://github.com/jiangyi3265/cangchu-admin#readme)。

## 项目结构

```text
README.md                      项目入口与关联仓库
repositories.json              仓库名称、目录和默认分支索引
DESIGN.md                      既有若依界面规范
docs/
  HANDOFF.md                   接手入口、开发步骤与私密资料清单
  DEPLOYMENT.md                当前线上部署、备份与回退说明
  deployed-release.json        已发布代码提交与构建标识
  REPLACEMENT_ACCEPTANCE.md     完整替换范围与验收门槛
  RUOYI_MIGRATION.md            模块进度、验证证据及操作记录
ops/                           不含凭据的运维脚本、systemd 与 Nginx 配置
../cangchu-backend/             并列的独立 Java 源码仓库
../cangchu-admin/               并列的独立 Vue 源码仓库
```

## 简历描述示例

参与海外仓储系统向若依 Vue 3 与 Java Spring Boot 的迁移，梳理入库、库存、订单履约和计费的业务边界，维护模块验证证据、异常恢复要求与分阶段替换验收文档。

## 上游与许可

前后端源自若依官方项目，两个代码仓库各自保留 MIT 许可与 `UPSTREAM.md` 来源说明。本项目不是 Mintsoft 或任何第三方仓储产品的官方版本。
