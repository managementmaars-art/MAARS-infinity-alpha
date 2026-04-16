# -*- coding: utf-8 -*-
"""
DailyHotApi Skill - API 客户端封装
"""

import aiohttp
import asyncio
import subprocess
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from config import config
from storage import storage  # 导入存储模块

# 部署状态存储
_deployment_status = {
    "is_deploying": False,
    "last_check": None,
    "needs_deployment": False,
    "message": ""
}


class HotSource:
    """热榜源定义"""

    def __init__(self, id: str, name: str, category: str, description: str = ""):
        self.id = id
        self.name = name
        self.category = category
        self.description = description


# 54 个热榜源定义
HOT_SOURCES = {
    # 视频/直播平台
    "bilibili": HotSource("bilibili", "哔哩哔哩", "video", "热门榜"),
    "acfun": HotSource("acfun", "AcFun", "video", "排行榜"),
    "douyin": HotSource("douyin", "抖音", "video", "热点榜"),
    "kuaishou": HotSource("kuaishou", "快手", "video", "热点榜"),
    "coolapk": HotSource("coolapk", "酷安", "video", "热榜"),

    # 社交媒体
    "weibo": HotSource("weibo", "微博", "social", "热搜榜"),
    "zhihu": HotSource("zhihu", "知乎", "social", "热榜"),
    "zhihu-daily": HotSource("zhihu-daily", "知乎日报", "social", "推荐榜"),
    "tieba": HotSource("tieba", "百度贴吧", "social", "热议榜"),
    "douban-group": HotSource("douban-group", "豆瓣讨论小组", "social", "讨论精选"),
    "v2ex": HotSource("v2ex", "V2EX", "social", "主题榜"),
    "ngabbs": HotSource("ngabbs", "NGA", "social", "热帖"),
    "hupu": HotSource("hupu", "虎扑", "social", "步行街热帖"),

    # 新闻资讯
    "baidu": HotSource("baidu", "百度", "news", "热搜榜"),
    "thepaper": HotSource("thepaper", "澎湃新闻", "news", "热榜"),
    "toutiao": HotSource("toutiao", "今日头条", "news", "热榜"),
    "36kr": HotSource("36kr", "36氪", "news", "热榜"),
    "qq-news": HotSource("qq-news", "腾讯新闻", "news", "热点榜"),
    "sina": HotSource("sina", "新浪网", "news", "热榜"),
    "sina-news": HotSource("sina-news", "新浪新闻", "news", "热点榜"),
    "netease-news": HotSource("netease-news", "网易新闻", "news", "热点榜"),
    "huxiu": HotSource("huxiu", "虎嗅", "news", "24小时"),
    "ifanr": HotSource("ifanr", "爱范儿", "news", "快讯"),

    # 科技/技术社区
    "ithome": HotSource("ithome", "IT之家", "tech", "热榜"),
    "ithome-xijiayi": HotSource("ithome-xijiayi", "IT之家「喜加一」", "tech", "最新动态"),
    "sspai": HotSource("sspai", "少数派", "tech", "热榜"),
    "csdn": HotSource("csdn", "CSDN", "tech", "排行榜"),
    "juejin": HotSource("juejin", "稀土掘金", "tech", "热榜"),
    "51cto": HotSource("51cto", "51CTO", "tech", "推荐榜"),
    "nodeseek": HotSource("nodeseek", "NodeSeek", "tech", "最新动态"),
    "hellogithub": HotSource("hellogithub", "HelloGitHub", "tech", "Trending"),

    # 游戏/ACG
    "genshin": HotSource("genshin", "原神", "game", "最新消息"),
    "miyoushe": HotSource("miyoushe", "米游社", "game", "最新消息"),
    "honkai": HotSource("honkai", "崩坏3", "game", "最新动态"),
    "starrail": HotSource("starrail", "崩坏：星穹铁道", "game", "最新动态"),
    "lol": HotSource("lol", "英雄联盟", "game", "更新公告"),

    # 阅读/文化
    "jianshu": HotSource("jianshu", "简书", "reading", "热门推荐"),
    "guokr": HotSource("guokr", "果壳", "reading", "热门文章"),
    "weread": HotSource("weread", "微信读书", "reading", "飙升榜"),
    "douban-movie": HotSource("douban-movie", "豆瓣电影", "reading", "新片榜"),

    # 工具/其他
    "52pojie": HotSource("52pojie", "吾爱破解", "tool", "榜单"),
    "hostloc": HotSource("hostloc", "全球主机交流", "tool", "榜单"),
    "weatheralarm": HotSource("weatheralarm", "中央气象台", "tool", "全国气象预警"),
    "earthquake": HotSource("earthquake", "中国地震台", "tool", "地震速报"),
    "history": HotSource("history", "历史上的今天", "tool", "月-日"),
}


class DailyHotApiClient:
    """DailyHotApi 客户端"""

    def __init__(self):
        self.api_url = config.api_url
        self.timeout = config.timeout

    async def fetch_hot_list(self, source_id: str, use_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取热榜数据

        Args:
            source_id: 热榜源 ID（如 weibo, zhihu, bilibili）
            use_cache: 是否使用缓存（默认False，每次获取最新数据）

        Returns:
            热榜数据字典或 None（失败时）
        """
        # 获取热榜源信息
        source = HOT_SOURCES.get(source_id)
        if not source:
            return None

        # 构建请求 URL
        url = config.get_api_url(source_id)

        # 步骤1：检查API是否可用
        print(f"[DailyHotApi] 正在连接 {source.name}...")
        api_available = await check_api_availability(url)

        if not api_available:
            # API不可用，尝试部署
            print(f"[DailyHotApi] ⚠️ 后端服务不可用，尝试自动部署...")

            # 触发部署
            deploy_result = await deploy_daily_hot_api()

            if deploy_result["success"]:
                # 部署成功，等待服务启动
                print(f"[DailyHotApi] ⏳ 等待服务启动 (5秒)...")
                await asyncio.sleep(5)

                # 再次检查API
                api_available = await check_api_availability(url)

                if not api_available:
                    # 仍然不可用，可能需要更多时间
                    print(f"[DailyHotApi] ⏳ 服务可能需要更多时间启动，再次等待 (10秒)...")
                    await asyncio.sleep(10)
                    api_available = await check_api_availability(url)

            # 返回部署状态
            if deploy_result["success"]:
                return {
                    "success": True,
                    "deploy_message": deploy_result["message"],
                    "is_deployed": True,
                    "data": None,
                    "message": "🎉 后端服务已部署成功！请稍后再次尝试获取热榜数据。"
                }
            else:
                return {
                    "success": False,
                    "deploy_message": "❌ 自动部署失败",
                    "steps": deploy_result.get("steps", []),
                    "data": None,
                    "message": f"⚠️ 无法连接后端服务\n\n自动部署失败：{deploy_result['message']}\n\n请手动部署：\n1. cd /root/.openclaw\n2. git clone https://github.com/imsyy/DailyHotApi.git\n3. cd DailyHotApi\n4. bash deploy.sh"
                }

        # API可用，获取数据
        try:
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    result = await response.json()

                    # 检查返回格式
                    if result.get("code") != 200:
                        return None

                    # 格式化数据
                    data = {
                        "platform": source.name,
                        "category": source.category,
                        "source_id": source_id,
                        "update_time": result.get("updateTime"),
                        "from_cache": result.get("fromCache", False),
                        "total": result.get("total", 0),
                        "data": self._format_items(result.get("data", [])),
                    }

                    # 每次获取最新数据后，保存到本地历史记录
                    save_result = storage.save_hot_list(source_id, data)
                    if save_result:
                        print(f"[DailyHotApi] ✅ 已保存 {source.name} 热榜数据到历史记录")

                    return data

        except Exception as e:
            print(f"[DailyHotApi] Error fetching {source_id}: {e}")
            return None

    async def get_hot榜单(self, source_id: str, limit: int = 10) -> Optional[List[Dict]]:
        """
        获取热榜条目列表（兼容旧接口）

        Args:
            source_id: 热榜源 ID
            limit: 返回条目数限制

        Returns:
            热榜条目列表或 None
        """
        data = await self.fetch_hot_list(source_id)
        if data:
            return data.get("data", [])[:limit]
        return None

    def _format_items(self, items: List[Dict]) -> List[Dict]:
        """格式化热榜条目"""
        formatted = []
        for i, item in enumerate(items[:config.max_items], 1):
            formatted.append({
                "rank": i,
                "title": item.get("title", ""),
                "desc": item.get("desc", ""),
                "hot": item.get("hot", ""),
                "url": item.get("url", ""),
                "mobile_url": item.get("mobileUrl", ""),
            })
        return formatted

    def get_all_sources(self) -> Dict[str, Dict]:
        """获取所有热榜源"""
        return {
            source_id: {
                "id": source_id,
                "name": source.name,
                "category": source.category,
                "description": source.description,
            }
            for source_id, source in HOT_SOURCES.items()
        }

    def get_sources_by_category(self) -> Dict[str, List[Dict]]:
        """按类别获取热榜源"""
        categories = {}
        for source_id, source in HOT_SOURCES.items():
            if source.category not in categories:
                categories[source.category] = []
            categories[source.category].append({
                "id": source_id,
                "name": source.name,
                "description": source.description,
            })
        return categories

    def search_sources(self, query: str) -> List[Dict]:
        """搜索热榜源"""
        query = query.lower()
        results = []
        for source_id, source in HOT_SOURCES.items():
            if (query in source.name.lower() or
                query in source.id.lower() or
                query in source.category.lower()):
                results.append({
                    "id": source_id,
                    "name": source.name,
                    "category": source.category,
                })
        return results


# 全局客户端实例
api_client = DailyHotApiClient()


# ============================================
# 自动检测和部署功能
# ============================================

async def check_api_availability(url: str, timeout: int = 3) -> bool:
    """
    检查API是否可用

    Args:
        url: API地址
        timeout: 超时时间（秒）

    Returns:
        True表示可用，False表示不可用
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(url, allow_redirects=True) as response:
                return response.status == 200
    except Exception as e:
        print(f"[DailyHotApi] API不可用: {e}")
        return False


async def deploy_daily_hot_api() -> Dict[str, Any]:
    """
    自动部署DailyHotApi后端服务

    Returns:
        部署结果字典
    """
    global _deployment_status

    if _deployment_status["is_deploying"]:
        return {
            "success": False,
            "message": "部署正在进行中，请稍候...",
            "is_deploying": True
        }

    _deployment_status["is_deploying"] = True
    _deployment_status["message"] = "🚀 正在自动部署DailyHotApi后端服务..."

    result = {
        "success": False,
        "message": "",
        "steps": []
    }

    try:
        # 检查是否已安装
        daily_hot_path = "/root/.openclaw/DailyHotApi"
        if not os.path.exists(daily_hot_path):
            # 步骤1：克隆仓库
            step_msg = "📦 正在克隆DailyHotApi仓库..."
            print(step_msg)
            result["steps"].append(step_msg)

            clone_cmd = ["git", "clone", "https://github.com/imsyy/DailyHotApi.git", daily_hot_path]
            clone_proc = await asyncio.create_subprocess_exec(
                *clone_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await clone_proc.communicate()

            if clone_proc.returncode != 0:
                error_msg = f"❌ 克隆失败: {stderr.decode()}"
                print(error_msg)
                result["steps"].append(error_msg)
                result["message"] = "部署失败：无法克隆仓库"
                _deployment_status["is_deploying"] = False
                return result

            result["steps"].append("✅ 克隆成功")
        else:
            result["steps"].append("✅ DailyHotApi已存在，跳过克隆")

        # 步骤2：部署服务
        if os.path.exists(daily_hot_path):
            step_msg = "🔧 正在部署DailyHotApi服务..."
            print(step_msg)
            result["steps"].append(step_msg)

            deploy_script = os.path.join(daily_hot_path, "deploy.sh")
            deploy_cmd = ["bash", deploy_script]

            deploy_proc = await asyncio.create_subprocess_exec(
                *deploy_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await deploy_proc.communicate()

            deploy_output = stdout.decode() + stderr.decode()

            if deploy_proc.returncode == 0:
                result["steps"].append("✅ 部署成功")
                result["success"] = True
                result["message"] = "🎉 DailyHotApi后端服务部署成功！正在启动..."
                _deployment_status["message"] = result["message"]
            else:
                error_msg = f"❌ 部署失败: {deploy_output}"
                print(error_msg)
                result["steps"].append(error_msg)
                result["message"] = "部署失败，请手动检查"

    except Exception as e:
        error_msg = f"❌ 部署异常: {str(e)}"
        print(error_msg)
        result["steps"].append(error_msg)
        result["message"] = f"部署异常: {str(e)}"

    finally:
        _deployment_status["is_deploying"] = False
        _deployment_status["last_check"] = datetime.now().isoformat()

    return result


def get_deployment_status() -> Dict[str, Any]:
    """
    获取当前部署状态

    Returns:
        部署状态字典
    """
    return {
        "is_deploying": _deployment_status["is_deploying"],
        "last_check": _deployment_status["last_check"],
        "message": _deployment_status["message"]
    }


async def test_connection() -> bool:
    """测试 API 连接"""
    try:
        timeout_obj = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(f"{config.api_url}/") as response:
                return response.status == 200
    except Exception:
        return False


if __name__ == "__main__":
    import sys
    print("Testing DailyHotApi connection...")

    if asyncio.run(test_connection()):
        print("✓ Service is running")
    else:
        print("✗ Service not available")
        print(f"  URL: {config.api_url}")
        sys.exit(1)
