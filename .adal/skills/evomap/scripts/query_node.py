import sys
import os
import argparse
import requests
from urllib.parse import urljoin

# 导入公共封装器
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from evomap_client import EvoMapClient

def query_node_details(node_id, hub_url="https://evomap.ai"):
    print(f"🔍 正在查询节点 {node_id} 的详情...\n")
    
    # 1. 组合网页专属直达链接
    web_url = f"{hub_url}/marketplace?author={node_id}" # 直达链接
    print(f"🌐 网页版直达查看链接:")
    print(f"请直接点击链接前往: {web_url}")
    print("-" * 50)

    # 2. 查询节点基础声望信息 (Reputation)
    try:
        # 使用直连的方式确保即使没有实例化 Client 也能查任意节点
        node_res = requests.get(f"{hub_url}/a2a/nodes/{node_id}")
        if node_res.status_code == 200:
            stats = node_res.json()
            print(f"📈 节点声望与统计:")
            print(f"   - 声望积分 (Reputation): {stats.get('reputation_score', 'N/A')}")
            print(f"   - 已发布资产总数: {stats.get('total_published', 0)}")
            print(f"   - 成功推广 (Promoted): {stats.get('total_promoted', 0)}")
            print(f"   - 被拒绝 (Rejected): {stats.get('total_rejected', 0)}")
        else:
            print(f"⚠️ 无法获取节点基础统计数据 (Status: {node_res.status_code})")
    except Exception as e:
        print(f"查询节点统计时出错: {e}")

    print("-" * 50)

    # 3. 遍历查询该节点名下发布的具体资产详情
    try:
        print(f"🗃️ 节点近期发布的资产详情:")
        # 获取全网大量最新资产进行本地筛选
        assets_res = requests.get(f"{hub_url}/a2a/assets", params={"limit": 5000})
        if assets_res.status_code == 200:
            data = assets_res.json()
            # 兼容不同的数据格式，有的直接返回列表，有的包在 assets 字段里
            assets_list = data.get("assets", []) if isinstance(data, dict) else data
            
            # 本地过滤出该 Node 的资产
            node_assets = [a for a in assets_list if a.get("author") == node_id or a.get("sender_id") == node_id]
            
            if not node_assets:
                # 可能是因为 Hub 还没刷新缓存，或者这个节点没有发过 Promoted 的资产
                print("   (在最新的 100 条全网动态中未发现该节点的 promoted 资产)")
            else:
                for idx, asset in enumerate(node_assets, 1):
                    asset_type = asset.get("asset_type", asset.get("type", "Unknown"))
                    gdi = asset.get("gdi_score", "N/A")
                    payload = asset.get("payload", {})
                    summary = payload.get("summary", asset.get("nl_summary", "无摘要信息"))
                    a_id = asset.get("asset_id", "Unknown")
                    status = asset.get("status", "promoted")
                    
                    print(f"   [{idx}] 类型: {asset_type} (状态: {status} | GDI评分: {gdi})")
                    print(f"       🔗 ID: {a_id}")
                    # 显示完整摘要
                    import textwrap
                    wrapped_summary = "\n              ".join(textwrap.wrap(summary, width=65))
                    print(f"       📝 摘要: {wrapped_summary}")
                    
                    # 针对不同类型的资产，展示里面最核心的实质内容文字
                    if asset_type == "Gene":
                        signals = payload.get("signals_match", [])
                        cmds = payload.get("validation", [])
                        print(f"       ⚡ 触发信号: {', '.join(signals)}")
                        print(f"       🛡️ 验证指令: {', '.join(cmds)}")
                    elif asset_type == "Capsule":
                        triggers = payload.get("trigger", [])
                        radius = payload.get("blast_radius", {})
                        print(f"       ⚡ 触发器: {', '.join(triggers)}")
                        print(f"       � 影响半径: 影响了 {radius.get('files', 0)} 个文件中的 {radius.get('lines', 0)} 行代码")
                    elif asset_type == "EvolutionEvent":
                        intent = payload.get("intent", "Unknown")
                        outcome = payload.get("outcome", {})
                        print(f"       🎯 进化意图: {intent}")
                        print(f"       🏆 验证结果: {outcome.get('status')} (验证分: {outcome.get('score')})")
                    
                    print()
        else:
            print(f"⚠️ 无法获取全网资产列表 (Status: {assets_res.status_code})")
    except Exception as e:
        print(f"查询资产列表时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description="查询 EvoMap 上特定节点的资产和声望详情。")
    parser.add_argument("node_id", nargs="?", help="要查询的 Node ID (例如 node_68fbee77258f4c6c)。如果不传，则默认查询本地当前节点。")
    args = parser.parse_args()

    target_node = args.node_id

    # 如果没有提供参数，则尝试读取本地当前的默认 Node
    if not target_node:
        try:
            client = EvoMapClient()
            target_node = client.node_id
            print(f"ℹ️ 未指定 Node ID，自动使用本地当前节点: {target_node}\n")
        except Exception as e:
            print("❌ 未提供 Node ID，且无法读取本地配置。")
            print("用法: python3 query_node.py <node_id>")
            sys.exit(1)

    query_node_details(target_node)

if __name__ == "__main__":
    main()
