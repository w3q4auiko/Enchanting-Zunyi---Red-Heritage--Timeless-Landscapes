# Enchanting Zunyi · Red Heritage, Timeless Landscapes

> 面向遵义文旅内容展示、红色文化传播与旅游资源运营的一体化 Web 系统。

本项目以遵义红色文化、山水景观、地方美食和全域旅游资源为核心，提供公众门户、
注册用户互动与后台内容管理能力。系统采用 Vue 与 Flask 前后端分离架构，支持 MySQL
数据持久化、双令牌认证、响应式管理后台及 Docker 容器化部署。

## 项目特色

- **遵义文旅门户**：集中展示红色文化、热门景点、黔北美食、美食街区和区域攻略。
- **多类型内容管理**：支持景点、美食、街区、区域等资源的新增、编辑、查询与上下架。
- **用户互动体系**：公众用户可以注册、登录并提交文旅内容。
- **现代管理后台**：分组导航、数据概览、统一表格与表单、桌面折叠和移动端抽屉导航。
- **生产级认证设计**：短期访问令牌、HttpOnly 刷新 Cookie、令牌轮换与服务端撤销。
- **登录安全防护**：scrypt 密码摘要、用户名唯一约束、登录限流和统一错误响应。
- **管理员安全边界**：管理员注册受权限控制，禁止删除当前账号和最后一个管理员。
- **SEO 与部署能力**：动态 Sitemap、robots.txt、Nginx、Gunicorn 和 Docker Compose。

## 功能模块

| 使用端 | 模块       | 主要功能                                 |
| ------ | ---------- | ---------------------------------------- |
| 前台   | 首页与专题 | 红城概览、精彩推荐、文化与旅游专题       |
| 前台   | 景点内容   | 景点列表、分类展示、详情和服务信息       |
| 前台   | 地方美食   | 美食分类、推荐店铺、价格与详情展示       |
| 前台   | 全域旅游   | 区县概况、美食街区和旅游路线             |
| 用户端 | 账号与投稿 | 注册、登录、会话刷新、退出和内容投稿     |
| 管理端 | 数据概览   | 景点、美食、街区、区域、用户和管理员统计 |
| 管理端 | 内容运营   | 文旅资源查询、新增、编辑、删除和状态管理 |
| 管理端 | 账号管理   | 管理员列表、权限保护和会话撤销           |

## 技术栈

| 层级      | 技术                                           |
| --------- | ---------------------------------------------- |
| 前端框架  | Vue 3、Vue Router、Vite                        |
| UI 与样式 | Element Plus、Tailwind CSS、自定义后台设计系统 |
| 数据请求  | Axios                                          |
| 地图能力  | 高德地图 JavaScript API                        |
| 后端框架  | Flask、Flask-Cors                              |
| 数据访问  | PyMySQL、DBUtils 连接池                        |
| 身份认证  | PyJWT、Werkzeug scrypt、HttpOnly Cookie        |
| 数据库    | MySQL 8+                                       |
| 生产运行  | Gunicorn、gevent、Nginx                        |
| 容器编排  | Docker Compose                                 |

## 项目结构

```text
Enchanting Zunyi · Red Heritage, Timeless Landscapes/
├─ backend/
│  ├─ migrations/          # 数据库升级脚本
│  ├─ routes/              # 认证、管理端、投稿与旅游数据接口
│  ├─ tests/               # 后端认证与数据库事务测试
│  ├─ utils/               # 数据库、鉴权、校验与请求工具
│  ├─ app.py               # Flask 应用工厂和启动入口
│  ├─ commands.py          # 管理员安全运维命令
│  └─ requirements.txt
├─ frontend/
│  ├─ public/              # 静态资源
│  ├─ scripts/             # 图片优化脚本
│  └─ src/
│     ├─ api/              # 前端 API 封装
│     ├─ assets/css/       # 全局与后台设计系统
│     ├─ router/           # 页面路由和权限守卫
│     ├─ utils/            # 请求与会话管理
│     └─ views/            # 前台、用户端与管理端页面
├─ datebase/
│  └─ zunyi_tourism.sql    # MySQL 基础数据脚本
├─ docker-compose.yml
├─ .env.example
└─ README.md
```

## 环境要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- MySQL 8 或更高版本
- npm 9 或更高版本
- Docker 与 Docker Compose（可选）

## 本地开发

### 1. 获取项目并准备配置

```powershell
git clone <repository-url>
cd "Enchanting Zunyi · Red Heritage, Timeless Landscapes"
Copy-Item .env.example .env
```

本地直接运行后端时，将 `.env` 中的数据库主机调整为：

```env
APP_ENV=local
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=zunyi_tourism
DB_USER=zunyi_db
DB_PASSWORD=站点专用强密码
TRUST_PROXY=false
```

网站运行时禁止使用 `root`。`root` 仅用于首次初始化数据库、创建站点专用账号和执行结构迁移。

### 2. 初始化数据库

在项目根目录启动 MySQL 客户端，使用 `root` 账号创建数据库并导入基础数据及迁移：

```sql
CREATE DATABASE IF NOT EXISTS zunyi_tourism
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zunyi_tourism;
SOURCE datebase/zunyi_tourism.sql;
SOURCE backend/migrations/001_auth_security.sql;
SOURCE backend/migrations/002_content_import_compat.sql;
SOURCE backend/migrations/003_restore_public_user.sql;
SOURCE backend/migrations/004_route_and_submission_audit.sql;
```

然后创建仅供网站使用的最小权限账号。将下面的 `站点专用强密码` 替换为 `.env` 中的 `DB_PASSWORD`：

```sql
CREATE USER IF NOT EXISTS 'zunyi_db'@'localhost'
  IDENTIFIED BY '站点专用强密码';
CREATE USER IF NOT EXISTS 'zunyi_db'@'127.0.0.1'
  IDENTIFIED BY '站点专用强密码';
ALTER USER 'zunyi_db'@'localhost'
  IDENTIFIED BY '站点专用强密码';
ALTER USER 'zunyi_db'@'127.0.0.1'
  IDENTIFIED BY '站点专用强密码';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON zunyi_tourism.* TO 'zunyi_db'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE
  ON zunyi_tourism.* TO 'zunyi_db'@'127.0.0.1';
FLUSH PRIVILEGES;
```

应用账号不授予建库、建用户或修改表结构的权限。结构迁移继续由 `root` 或独立运维账号执行。请根据项目实际目录修改 SQL 路径；已有数据库执行迁移前应先备份。

### 3. 启动后端

```powershell
cd backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

后端默认地址：`http://127.0.0.1:5000`

健康检查：

```text
GET http://127.0.0.1:5000/
```

### 4. 创建或重置管理员

在已激活的后端虚拟环境中执行：

```powershell
# 创建首个管理员
flask --app app:create_app create-admin

# 安全重置现有管理员密码
flask --app app:create_app reset-admin-password --username admin
```

命令会在终端中隐藏密码输入。不要将管理员明文密码写入 SQL、脚本或环境变量。

### 5. 启动前端

新建终端并执行：

```powershell
cd frontend
npm install
npm run dev
```

访问地址：

- 前台门户：`http://localhost:5173`
- 管理后台：`http://localhost:5173/admin/dashboard`

## Docker 部署

基础数据库文件已位于 `datebase/zunyi_tourism.sql`。完成生产环境变量配置后执行：

```powershell
docker compose up -d --build
```

查看服务状态：

```powershell
docker compose ps
```

按需启动 phpMyAdmin：

```powershell
docker compose --profile tools up -d phpmyadmin
```

已有 MySQL 数据卷不会再次运行初始化脚本，升级时需要手工执行：

按编号顺序执行尚未应用的迁移：

```text
backend/migrations/001_auth_security.sql
backend/migrations/002_content_import_compat.sql
backend/migrations/003_restore_public_user.sql
backend/migrations/004_route_and_submission_audit.sql
```

## 关键环境变量

| 变量                 | 说明                                 | 生产要求               |
| -------------------- | ------------------------------------ | ---------------------- |
| `APP_ENV`            | 运行环境，支持 `local`、`production` | 使用 `production`      |
| `FLASK_DEBUG`        | Flask 调试开关                       | 必须为 `False`         |
| `SECRET_KEY`         | JWT 签名密钥                         | 至少 32 位随机字符串   |
| `CORS_ORIGINS`       | 允许携带凭据的前端来源               | 必须明确配置，禁止 `*` |
| `SITE_URL`           | Sitemap 使用的站点根地址             | 建议配置正式域名       |
| `DB_HOST`            | 数据库主机                           | Docker 内通常为 `db`   |
| `DB_NAME`            | 数据库名称                           | 默认 `zunyi_tourism`   |
| `DB_USER`            | 数据库用户                           | 使用最小权限账号       |
| `DB_PASSWORD`        | 数据库密码                           | 必须使用强密码         |
| `JWT_ACCESS_MINUTES` | 访问令牌有效期                       | 允许 5–60 分钟         |
| `AUTH_REFRESH_DAYS`  | 刷新会话有效期                       | 允许 1–90 天           |
| `TRUST_PROXY`        | 是否信任反向代理头                   | 仅在可信代理后启用     |
| `UPLOAD_ROOT`        | 运行期图片持久化目录               | 必须可写并纳入备份     |
| `MAX_IMAGE_UPLOAD_BYTES` | 单张图片大小上限                  | 默认 5MB              |

完整配置项参见 `.env.example`。

## 常用接口

### 公众接口

| 方法   | 路径                   | 说明             |
| ------ | ---------------------- | ---------------- |
| `GET`  | `/api/attractions`     | 景点列表         |
| `GET`  | `/api/foods`           | 美食列表         |
| `GET`  | `/api/food-streets`    | 美食街区列表     |
| `GET`  | `/api/regions`         | 区域列表         |
| `GET`  | `/api/routes`          | 已发布旅游路线   |
| `POST` | `/api/public/register` | 公众用户注册     |
| `POST` | `/api/public/login`    | 公众用户登录     |
| `GET`  | `/api/public/info`     | 当前公众用户信息 |
| `POST` | `/api/submission/add`  | 提交文旅内容     |
| `POST` | `/api/media/images`    | 登录用户上传图片 |
| `GET`  | `/api/media/images/*`  | 访问已上传图片   |

### 认证与管理接口

| 方法                  | 路径                 | 说明                       |
| --------------------- | -------------------- | -------------------------- |
| `POST`                | `/api/auth/login`    | 管理员登录                 |
| `POST`                | `/api/auth/refresh`  | 轮换刷新令牌               |
| `POST`                | `/api/auth/logout`   | 撤销当前刷新会话           |
| `GET`                 | `/api/auth/me`       | 当前管理员信息             |
| `POST`                | `/api/auth/register` | 创建管理员，需要管理员权限 |
| `GET`                 | `/api/admin/stats`   | 后台资源统计               |
| `GET/POST/PUT/DELETE` | `/api/admin/*`       | 后台资源管理               |

## 测试与构建

运行后端测试：

```powershell
cd backend
python -m unittest discover -s tests -v
```

构建前端生产包：

```powershell
cd frontend
npm run build
```

构建结果输出到 `frontend/dist/`。

## 安全说明

- 生产环境必须通过 HTTPS 提供服务，否则 Secure 刷新 Cookie 无法正常工作。
- 访问令牌仅保存在前端内存，刷新令牌由 HttpOnly Cookie 管理。
- 管理员密码通过 Werkzeug scrypt 生成摘要，数据库不保存明文密码。
- 刷新令牌只保存 SHA-256 摘要，并在每次刷新时自动轮换。
- 登录与注册操作具有数据库审计和频率限制。
- 管理员注册接口只允许已登录管理员访问。
- 删除管理员时会撤销其刷新会话，并至少保留一个管理员账号。
- `.env`、数据库备份、生产日志与本地资料目录不得提交到 Git。
- 本地部署需定期备份 `backend/uploads/`；Docker 部署需备份 `upload_data` 数据卷。

---

本项目用于遵义文旅信息展示、内容运营与软件工程实践。
