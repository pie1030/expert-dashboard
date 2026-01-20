"""
API 路由定义
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse, DashboardResponse
from app.services.talent_service import talent_service

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.post("/upload", response_model=UploadResponse)
async def upload_talent_ids(file: UploadFile = File(...)):
    """
    上传 talent_ids.txt 文件
    
    - 解析文件中的 talent_id
    - 获取专家数据
    - 返回会话 ID 用于后续查询
    """
    # 验证文件类型
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="只支持 .txt 文件格式"
        )
    
    try:
        content = await file.read()
        file_content = content.decode('utf-8')
    except UnicodeDecodeError:
        # 尝试 GBK 编码
        try:
            file_content = content.decode('gbk')
        except:
            raise HTTPException(
                status_code=400,
                detail="文件编码不支持，请使用 UTF-8 或 GBK 编码"
            )
    
    # 生成会话 ID
    session_id = str(uuid.uuid4())[:8]
    
    # 处理上传
    try:
        experts, stats = talent_service.process_upload(file_content, session_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理文件失败: {str(e)}"
        )
    
    return UploadResponse(
        success=True,
        message=f"成功解析 {len(experts)} 位专家数据",
        talent_count=len(experts),
        session_id=session_id
    )


@router.get("/dashboard/{session_id}", response_model=DashboardResponse)
async def get_dashboard(session_id: str):
    """
    获取 Dashboard 数据
    
    - 根据 session_id 获取之前上传的专家数据
    - 返回统计数据
    """
    experts = talent_service.get_cached_experts(session_id)
    
    if not experts:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或已过期，请重新上传文件"
        )
    
    stats = talent_service.calculate_stats(experts)
    
    return DashboardResponse(
        success=True,
        message="获取成功",
        stats=stats
    )


@router.get("/dashboard/{session_id}/experts")
async def get_experts_detail(session_id: str, limit: int = 50, offset: int = 0):
    """
    获取专家详情列表（分页）
    """
    experts = talent_service.get_cached_experts(session_id)
    
    if not experts:
        raise HTTPException(
            status_code=404,
            detail="会话不存在或已过期"
        )
    
    paginated = experts[offset:offset + limit]
    
    return {
        "success": True,
        "total": len(experts),
        "data": [e.model_dump() for e in paginated]
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "expert-dashboard"}
