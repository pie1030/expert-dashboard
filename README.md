# Dashboard

一个轻量级的专家画像分析工具。上传 `talent_ids.txt` 文件，自动生成Dashboard。

## 功能特性

- **一键上传**：拖拽或点击上传 talent_ids.txt
- **自动分析**：自动解析并生成专家画像统计
- **美观可视化**：基于 ECharts 的专业图表展示
- **即开即用**：一条命令启动，无需复杂配置

## Dashboard 内容

### 概览指标
- 专家总数
- 高学历占比（硕博比例）
- 名校背景（985/211/海外）
- 大厂经历比例

### 分布图表
- 学校层级分布
- 学历分布
- 技术栈分布 TOP 10
- 任务类型分布

---

## 快速开始

### 方式一：本地运行（开发/测试）

```bash
# 1. 进入项目目录
cd expert-dashboard

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python run.py

# 4. 打开浏览器访问
open http://127.0.0.1:8080
```

### 方式二：Docker 部署（推荐）

```bash
# 1. 构建并启动
docker-compose up -d

# 2. 访问
open http://localhost:8080

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 方式三：Docker 单独运行

```bash
# 1. 构建镜像
docker build -t expert-dashboard .

# 2. 运行容器
docker run -d -p 8080:8080 --name expert-dashboard expert-dashboard

# 3. 访问
open http://localhost:8080
```

---

## 部署到服务器

### 1. 准备服务器

确保服务器已安装 Docker 和 Docker Compose：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose -y

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 上传代码

```bash
# 方式 A：使用 scp
scp -r expert-dashboard/ user@your-server:/path/to/

# 方式 B：使用 git
git clone your-repo-url
cd expert-dashboard
```

### 3. 启动服务

```bash
cd expert-dashboard
docker-compose up -d
```

### 4. 配置反向代理（可选）

如果需要通过域名访问，配置 Nginx：

```nginx
server {
    listen 80;
    server_name dashboard.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 文件上传大小限制
        client_max_body_size 10M;
    }
}
```

### 5. 配置 HTTPS（可选）

使用 Let's Encrypt 免费证书：

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d dashboard.example.com
```

---

## 项目结构

```
expert-dashboard/
├── app/                    # 后端应用
│   ├── api/
│   │   └── routes.py      # API 路由
│   ├── models/
│   │   └── schemas.py     # 数据模型
│   ├── services/
│   │   ├── mock_data.py   # Mock 数据生成器
│   │   └── talent_service.py  # 业务逻辑
│   └── main.py            # FastAPI 应用入口
├── static/                 # 前端静态文件
│   ├── css/
│   │   └── style.css      # 样式表
│   ├── js/
│   │   └── dashboard.js   # 前端逻辑
│   └── index.html         # 主页面
├── uploads/               # 上传文件目录
├── Dockerfile             # Docker 镜像配置
├── docker-compose.yml     # Docker Compose 配置
├── requirements.txt       # Python 依赖
├── run.py                 # 启动脚本
└── README.md
```

---

## 开发说明

### 开发模式

```bash
python run.py --reload
```

启用热重载，代码修改后自动重启。

### 自定义端口

```bash
python run.py --port 3000
```

### API 文档

启动服务后访问：http://127.0.0.1:8080/docs

### 主要 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传 talent_ids.txt |
| `/api/dashboard/{session_id}` | GET | 获取 Dashboard 数据 |
| `/api/health` | GET | 健康检查 |

---

## 配色方案

采用 Forest Green & Deep Sea Blue 双色系设计：

```css
--forest-green: #54A072;
--deep-sea-blue: #6684A3;
--bg-color: #F7F8FA;
--text-dark: #2C3E50;
```

字体使用 Alegreya 衬线字体家族。

---

## 数据说明

当前版本使用 Mock 数据进行演示。如需对接真实 API，修改 `app/services/talent_service.py` 中的 `fetch_experts` 方法。

---

## 常见问题

### Q: 如何修改监听端口？

```bash
# 方式一：命令行参数
python run.py --port 3000

# 方式二：修改 docker-compose.yml
ports:
  - "3000:8080"
```

### Q: 如何限制上传文件大小？

在 Nginx 配置中设置 `client_max_body_size`，或在代码中添加校验。

### Q: 如何添加用户认证？

参考 `PLATFORM_DESIGN.md` 中的第二阶段设计方案。

---

Made with care by MeetChances Team
