"""
每日热榜技能主入口示例

这个文件展示如何将三个扩展功能集成到主Skill中。
在实际使用时，可以根据需要调整和整合。
"""

import asyncio
from typing import Dict, Any, Optional

# 支持相对导入（作为包的一部分）和绝对导入（直接运行）
try:
    from .news_digest import NewsDigest, DigestConfig, create_digest as create_news_digest
    from .industry_hot import IndustryHot, IndustryConfig, create_industry_hot
    from .personalized import PersonalizedSubscription, UserPreferences, create_personalized
    from .storage import storage
    from .api_client import api_client, check_api_availability, deploy_daily_hot_api, get_deployment_status
    from .config import config
except ImportError:
    from news_digest import NewsDigest, DigestConfig, create_digest as create_news_digest
    from industry_hot import IndustryHot, IndustryConfig, create_industry_hot
    from personalized import PersonalizedSubscription, UserPreferences, create_personalized
    from storage import storage
    from api_client import api_client, check_api_availability, deploy_daily_hot_api, get_deployment_status
    from config import config


class DailyHotNewsSkill:
    """每日热榜技能主类"""

    def __init__(self, api_client=None, formatter=None):
        """
        初始化技能

        Args:
            api_client: API客户端实例（用于获取热榜数据）
            formatter: 格式化器实例（用于格式化输出）
        """
        self.api_client = api_client
        self.formatter = formatter

        # 初始化各功能模块
        self.news_digest: Optional[NewsDigest] = None
        self.industry_hot: Optional[IndustryHot] = None
        self.personalized: Optional[PersonalizedSubscription] = None

        # 标记是否已检查过旧数据（避免每次都提示）
        self._old_data_checked = False
        self._old_data_notification = None

    async def initialize(self):
        """初始化各模块"""
        self.news_digest = await create_news_digest(
            api_client=self.api_client,
            formatter=self.formatter
        )
        self.industry_hot = await create_industry_hot(
            api_client=self.api_client,
            formatter=self.formatter
        )
        self.personalized = await create_personalized(
            api_client=self.api_client,
            formatter=self.formatter
        )

        # 启动时检查是否有7天前的旧数据
        await self._check_old_data()

    async def _check_old_data(self):
        """检查并提示用户清理7天前的旧数据"""
        if self._old_data_checked:
            return

        old_files = storage.get_old_data_files(days=7)
        if old_files:
            # 统计
            sources = set(f["source_id"] for f in old_files)
            print(f"\n⚠️ 发现 {len(old_files)} 个旧数据文件（7天前）")
            print(f"   涉及平台: {', '.join(list(sources)[:5])}...")
            print(f"   示例文件: {old_files[0]['date_str']} - {old_files[0]['source_id']}")

            # 返回提示信息给用户
            self._old_data_notification = {
                "has_old_data": True,
                "count": len(old_files),
                "sources": list(sources),
                "message": f"""🗑️ **发现旧热榜数据**

检测到 {len(old_files)} 个热榜数据文件已超过7天未清理，涉及 {len(sources)} 个平台。

是否需要清理这些旧数据？
- 回复"**清理**"或"**是**"：删除7天前的所有旧数据
- 回复"**跳过**"或"**否**"：保留数据，下次启动不再提醒"""
            }
        else:
            self._old_data_notification = None

        self._old_data_checked = True

    def get_old_data_notification(self) -> Optional[Dict[str, Any]]:
        """获取旧数据清理提示（如果有）"""
        return self._old_data_notification

    async def handle_old_data_cleanup(self, confirm: bool = False) -> Dict[str, Any]:
        """
        处理旧数据清理

        Args:
            confirm: 是否确认清理

        Returns:
            清理结果
        """
        if not confirm:
            return {
                "action": "ask_confirm",
                "message": "请确认是否清理7天前的旧数据？\n回复\"清理\"确认，回复\"跳过\"取消。"
            }

        old_files = storage.get_old_data_files(days=7)
        if not old_files:
            return {
                "action": "show_message",
                "message": "✅ 没有需要清理的旧数据"
            }

        deleted = storage.cleanup_old_files(old_files)
        return {
            "action": "show_message",
            "message": f"✅ 成功清理 {deleted} 个旧数据文件"
        }
    
    async def handle_request(self, user_input: str, intent: str = None) -> Dict[str, Any]:
        """
        处理用户请求

        Args:
            user_input: 用户输入
            intent: 意图（可选，用于路由到对应功能）

        Returns:
            处理结果
        """
        user_input_lower = user_input.lower()

        # 检查是否是清理旧数据命令
        cleanup_keywords = ["清理", "删除旧数据", "清除缓存", "clean"]
        if any(kw in user_input_lower for kw in cleanup_keywords):
            return await self.handle_old_data_cleanup(confirm=True)

        # 检查是否是获取热榜的请求
        is_hot_request = any([
            intent == "news_digest",
            self._is_news_digest_request(user_input_lower),
            intent == "industry_hot",
            self._is_industry_hot_request(user_input_lower),
        ])

        if is_hot_request:
            # 先检查API是否可用
            api_url = config.api_url
            print(f"\n[DailyHotSkill] 检查后端服务可用性: {api_url}")

            api_available = await check_api_availability(api_url)

            if not api_available:
                print(f"[DailyHotSkill] ⚠️ 后端服务不可用，触发自动部署...")
                deploy_result = await deploy_daily_hot_api()

                # 返回部署状态给用户
                if deploy_result["success"]:
                    # 构建部署步骤消息
                    steps_text = ""
                    for step in deploy_result.get("steps", []):
                        steps_text += f"{step}\n"

                    return {
                        "action": "show_deploying",
                        "message": f"""🚀 **正在自动部署后端服务**

{steps_text}

⏳ **请稍候...**

后端服务正在启动，预计需要1-2分钟。

**部署完成后**，请再次发送请求获取热榜数据。

---
💡 如果自动部署失败，请手动执行：
1. `cd /root/.openclaw`
2. `git clone https://github.com/imsyy/DailyHotApi.git`
3. `cd DailyHotApi`
4. `bash deploy.sh`""",
                        "deploy_success": True,
                        "steps": deploy_result.get("steps", [])
                    }
                else:
                    # 部署失败，返回错误和手动部署指南
                    steps_text = ""
                    for step in deploy_result.get("steps", []):
                        steps_text += f"{step}\n"

                    return {
                        "action": "show_deploy_failed",
                        "message": f"""⚠️ **后端服务不可用**

自动部署失败，需要手动部署。

**部署步骤：**
```bash
cd /root/.openclaw
git clone https://github.com/imsyy/DailyHotApi.git
cd DailyHotApi
bash deploy.sh
```""",
                        "deploy_success": False,
                        "steps": deploy_result.get("steps", [])
                    }

        # 路由到对应功能
        if intent == "news_digest" or self._is_news_digest_request(user_input_lower):
            return await self._handle_news_digest(user_input)

        elif intent == "industry_hot" or self._is_industry_hot_request(user_input_lower):
            return await self._handle_industry_hot(user_input)

        elif intent == "personalized" or self._is_personalized_request(user_input_lower):
            return await self._handle_personalized(user_input)

        else:
            # 默认返回功能选择引导
            return await self._show_main_menu()
    
    def _is_news_digest_request(self, user_input: str) -> bool:
        """判断是否为新闻摘要请求"""
        keywords = ["热点", "摘要", "标签", "科技", "游戏", "娱乐", "财经", "新闻"]
        return any(kw in user_input for kw in keywords)
    
    def _is_industry_hot_request(self, user_input: str) -> bool:
        """判断是否为行业热榜请求"""
        keywords = ["行业", "汽车", "金融", "医疗", "旅游", "餐饮", "房产"]
        return any(kw in user_input for kw in keywords)
    
    def _is_personalized_request(self, user_input: str) -> bool:
        """判断是否为个性化请求"""
        keywords = ["配置", "设置", "偏好", "关注", "个性化", "订阅"]
        return any(kw in user_input for kw in keywords)
    
    async def _handle_news_digest(self, user_input: str) -> Dict[str, Any]:
        """处理新闻摘要请求"""
        if not self.news_digest:
            return {"error": "模块未初始化"}
        
        return await self.news_digest.process_user_request(user_input)
    
    async def _handle_industry_hot(self, user_input: str) -> Dict[str, Any]:
        """处理行业热榜请求"""
        if not self.industry_hot:
            return {"error": "模块未初始化"}
        
        return await self.industry_hot.process_user_request(user_input)
    
    async def _handle_personalized(self, user_input: str) -> Dict[str, Any]:
        """处理个性化订阅请求"""
        if not self.personalized:
            return {"error": "模块未初始化"}
        
        return await self.personalized.process_user_request(user_input)
    
    async def _show_main_menu(self) -> Dict[str, Any]:
        """显示主菜单"""
        # 检查是否有旧数据清理提示
        old_data = self.get_old_data_notification()

        menu_text = """🎯 **每日热榜 - 功能选择**

请选择您想使用的功能：

1. **📰 热点新闻摘要**
   按标签浏览热点新闻（科技、游戏、娱乐、财经等）

2. **🏭 行业热榜垂直**
   按行业分类查看热榜（汽车、金融、医疗、旅游等）

3. **⚙️ 个性化订阅**
   配置您的偏好，获取定制化热榜

💡 您可以直接告诉我您想做什么，例如：
- "今天有什么科技热点"
- "看看汽车行业热榜"
- "配置个性化热榜"
"""

        result = {
            "action": "show_menu",
            "message": menu_text
        }

        # 如果有旧数据，添加提示
        if old_data:
            result["old_data_prompt"] = old_data["message"]

        return result
    
    # 便捷方法
    
    async def get_news_digest_tags(self) -> str:
        """获取新闻摘要标签选项"""
        if self.news_digest:
            return await self.news_digest.get_tag_options()
        return "模块未初始化"
    
    async def get_industry_options(self) -> str:
        """获取行业选项"""
        if self.industry_hot:
            return await self.industry_hot.get_industry_options()
        return "模块未初始化"
    
    async def get_personalized_options(self) -> str:
        """获取个性化配置选项"""
        if self.personalized:
            return await self.personalized.get_config_options()
        return "模块未初始化"
    
    def get_current_config(self) -> Optional[UserPreferences]:
        """获取当前个性化配置"""
        if self.personalized:
            return self.personalized.get_current_config()
        return None


# 便捷函数
async def create_skill(api_client=None, formatter=None) -> DailyHotNewsSkill:
    """创建技能实例"""
    skill = DailyHotNewsSkill(api_client=api_client, formatter=formatter)
    await skill.initialize()
    return skill


# 示例使用
if __name__ == "__main__":
    async def example():
        # 创建技能实例（不传入api_client时的模拟示例）
        skill = await create_skill()
        
        # 示例1：展示主菜单
        result = await skill.handle_request("帮助")
        print(result["message"])
        
        print("\n" + "="*60 + "\n")
        
        # 示例2：展示标签选择
        result = await skill.get_news_digest_tags()
        print(result)
        
        print("\n" + "="*60 + "\n")
        
        # 示例3：展示行业选择
        result = await skill.get_industry_options()
        print(result)
        
        print("\n" + "="*60 + "\n")
        
        # 示例4：展示个性化配置选项
        result = await skill.get_personalized_options()
        print(result)
    
    asyncio.run(example())
