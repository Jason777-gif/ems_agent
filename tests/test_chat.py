import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_chat_endpoint():
    """测试聊天接口"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat",
            json={
                "message": "查询1号逆变器今天的发电功率"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data


@pytest.mark.asyncio
async def test_device_list():
    """测试设备列表"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/devices")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
