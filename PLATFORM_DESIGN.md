# 第二阶段：平台化设计方案

## 📋 目标

将「专家画像 Dashboard」从本地工具升级为通用网页应用平台，支持多用户、多项目、多次上传。

---

## 🏗️ 架构演进

### 当前架构（第一阶段）

```
┌─────────────────────────────────────────┐
│           本地单用户模式                  │
├─────────────────────────────────────────┤
│  Browser  ──────►  FastAPI  ──────►  Mock Data
│                        │
│                    内存缓存
└─────────────────────────────────────────┘
```

### 目标架构（第二阶段）

```
┌─────────────────────────────────────────────────────────────┐
│                      多用户平台模式                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │ Browser │────►│   Nginx      │────►│   FastAPI    │     │
│  │         │     │   (负载均衡)  │     │   (多实例)    │     │
│  └─────────┘     └──────────────┘     └──────┬───────┘     │
│                                              │              │
│        ┌─────────────────────────────────────┤              │
│        │                                     │              │
│        ▼                                     ▼              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │PostgreSQL│  │  Redis   │  │   OSS    │  │ Talent API │  │
│  │ (用户/项目)│  │ (缓存)   │  │ (文件)   │  │  (真实数据) │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 多用户支持

### 用户认证

```python
# 方案一：集成现有系统
# 直接复用 meetchances-platform 的用户体系

# 方案二：独立轻量认证
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """验证 JWT Token，获取当前用户"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
```

### 数据模型扩展

```python
class User(BaseModel):
    """用户模型"""
    id: str
    email: str
    name: str
    role: str  # admin / manager / viewer

class Project(BaseModel):
    """项目模型"""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    updated_at: datetime

class Upload(BaseModel):
    """上传记录"""
    id: str
    project_id: str
    user_id: str
    filename: str
    talent_count: int
    status: str  # processing / completed / failed
    created_at: datetime
    stats_snapshot: Optional[dict]  # 快照统计数据
```

---

## 📂 多次上传支持

### 上传历史管理

```python
@router.get("/projects/{project_id}/uploads")
async def list_uploads(
    project_id: str,
    current_user: User = Depends(get_current_user)
) -> List[Upload]:
    """获取项目的上传历史"""
    return await upload_service.list_by_project(project_id)

@router.get("/uploads/{upload_id}/dashboard")
async def get_upload_dashboard(
    upload_id: str,
    current_user: User = Depends(get_current_user)
) -> DashboardResponse:
    """获取特定上传的 Dashboard 数据"""
    upload = await upload_service.get(upload_id)
    return upload.stats_snapshot
```

### 版本对比功能

```python
@router.get("/projects/{project_id}/compare")
async def compare_uploads(
    project_id: str,
    upload_id_1: str,
    upload_id_2: str,
    current_user: User = Depends(get_current_user)
) -> CompareResponse:
    """对比两次上传的差异"""
    stats_1 = await get_upload_stats(upload_id_1)
    stats_2 = await get_upload_stats(upload_id_2)
    return calculate_diff(stats_1, stats_2)
```

---

## 🔒 权限与数据隔离

### 权限矩阵

| 角色 | 查看项目 | 上传文件 | 管理成员 | 删除项目 |
|------|---------|---------|---------|---------|
| Owner | ✅ | ✅ | ✅ | ✅ |
| Manager | ✅ | ✅ | ❌ | ❌ |
| Viewer | ✅ | ❌ | ❌ | ❌ |

### 数据隔离策略

```python
# 基于项目的数据隔离
class ProjectPermission:
    @staticmethod
    async def check_access(user: User, project_id: str, required_role: str):
        """检查用户对项目的访问权限"""
        membership = await get_project_membership(user.id, project_id)
        if not membership:
            raise HTTPException(status_code=403, detail="无权访问此项目")
        
        role_hierarchy = {"owner": 3, "manager": 2, "viewer": 1}
        if role_hierarchy[membership.role] < role_hierarchy[required_role]:
            raise HTTPException(status_code=403, detail="权限不足")

# 在路由中使用
@router.post("/projects/{project_id}/upload")
async def upload_file(
    project_id: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    await ProjectPermission.check_access(current_user, project_id, "manager")
    # ... 处理上传
```

---

## 📊 数据库设计

### PostgreSQL 表结构

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目成员表
CREATE TABLE project_members (
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- owner, manager, viewer
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id)
);

-- 上传记录表
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    talent_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',
    stats_snapshot JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 专家数据表（可选，用于持久化）
CREATE TABLE experts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id UUID REFERENCES uploads(id),
    talent_id VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 API 对接

### 接口适配层设计

```python
# app/services/talent_api.py

from abc import ABC, abstractmethod

class TalentDataSource(ABC):
    """专家数据源抽象接口"""
    
    @abstractmethod
    async def fetch_expert(self, talent_id: str) -> Expert:
        """获取单个专家信息"""
        pass
    
    @abstractmethod
    async def fetch_experts(self, talent_ids: List[str]) -> List[Expert]:
        """批量获取专家信息"""
        pass

class MockDataSource(TalentDataSource):
    """Mock 数据源（开发测试用）"""
    
    async def fetch_expert(self, talent_id: str) -> Expert:
        return generate_mock_expert(talent_id)
    
    async def fetch_experts(self, talent_ids: List[str]) -> List[Expert]:
        return [await self.fetch_expert(tid) for tid in talent_ids]

class RealAPIDataSource(TalentDataSource):
    """真实 API 数据源"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def fetch_expert(self, talent_id: str) -> Expert:
        response = await self.client.get(
            f"{self.base_url}/talents/{talent_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return Expert(**response.json())
    
    async def fetch_experts(self, talent_ids: List[str]) -> List[Expert]:
        # 使用批量接口提高效率
        response = await self.client.post(
            f"{self.base_url}/talents/batch",
            json={"talent_ids": talent_ids},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return [Expert(**item) for item in response.json()]

# 配置使用哪个数据源
def get_data_source() -> TalentDataSource:
    if settings.USE_MOCK_DATA:
        return MockDataSource()
    else:
        return RealAPIDataSource(
            base_url=settings.TALENT_API_URL,
            api_key=settings.TALENT_API_KEY
        )
```

---

## 🐳 部署方案

### Docker Compose（开发/测试）

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/expert_dashboard
      - REDIS_URL=redis://redis:6379
      - USE_MOCK_DATA=false
      - TALENT_API_URL=https://api.meetchances.com
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: expert_dashboard
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes（生产）

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expert-dashboard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: expert-dashboard
  template:
    metadata:
      labels:
        app: expert-dashboard
    spec:
      containers:
      - name: app
        image: meetchances/expert-dashboard:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        envFrom:
        - secretRef:
            name: expert-dashboard-secrets
```

---

## 📅 实施计划

### 阶段 2.1：多用户基础（1-2 周）
- [ ] 集成用户认证系统
- [ ] 添加项目管理功能
- [ ] 实现上传历史

### 阶段 2.2：数据持久化（1 周）
- [ ] PostgreSQL 数据库集成
- [ ] Redis 缓存集成
- [ ] 文件存储（OSS）

### 阶段 2.3：API 对接（1 周）
- [ ] 实现真实 API 数据源
- [ ] 添加数据同步机制
- [ ] 错误处理和重试

### 阶段 2.4：部署上线（1 周）
- [ ] Docker 镜像构建
- [ ] K8s 部署配置
- [ ] 监控和日志

---

## 🎯 预期成果

完成第二阶段后，系统将支持：

1. **多用户协作**：团队成员可共同查看和分析专家数据
2. **项目管理**：按项目组织专家画像分析
3. **历史追溯**：保存每次上传的分析结果，支持版本对比
4. **权限控制**：细粒度的访问权限管理
5. **真实数据**：对接生产环境的专家数据 API
6. **高可用**：容器化部署，支持水平扩展

---

Made with ❤️ by MeetChances Team
