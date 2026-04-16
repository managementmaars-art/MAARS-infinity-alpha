#!/usr/bin/env bash
# 用户意图收集 - POST /aia/api/v1/intent/collect
# 用法: intent_collect.sh "意图描述" [场景描述] [场景值] [附加内容]
# 场景值见 USER_INTENT_SCENE_VALUE 枚举，如 skill_version_check, skill_search_keyword 等
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

intent_desc="$1"
scene_desc="${2:-}"
scene_value="${3:-}"
extra_related_content="${4:-}"

if [[ -z "$intent_desc" ]]; then
    echo "用法: $0 <意图描述> [场景描述] [场景值] [附加内容]" >&2
    echo "场景值示例: skill_version_check, skill_search_keyword, skill_search_tree, skill_get_script 等" >&2
    exit 1
fi

load_config || exit 1
# 生成 JSON（优先 jq，否则 python3，均无则报错）
if command -v jq &>/dev/null; then
    body=$(jq -n \
        --arg intent "$intent_desc" \
        --arg scene_desc "$scene_desc" \
        --arg scene_value "$scene_value" \
        --arg extra "$extra_related_content" \
        '{intent_desc: $intent, scene_desc: $scene_desc, scene_value: $scene_value, extra_related_content: $extra}')
elif command -v python3 &>/dev/null; then
    body=$(python3 -c "
import json, sys
print(json.dumps({
    'intent_desc': sys.argv[1],
    'scene_desc': sys.argv[2],
    'scene_value': sys.argv[3],
    'extra_related_content': sys.argv[4]
}))" "$intent_desc" "$scene_desc" "$scene_value" "$extra_related_content")
elif command -v python &>/dev/null; then
    body=$(python -c "
import json, sys
print(json.dumps({
    'intent_desc': sys.argv[1],
    'scene_desc': sys.argv[2],
    'scene_value': sys.argv[3],
    'extra_related_content': sys.argv[4]
}))" "$intent_desc" "$scene_desc" "$scene_value" "$extra_related_content")
else
    echo "错误：需要 jq 或 python/python3 生成 JSON，请安装其一" >&2
    exit 1
fi

raw=$(api_post "/aia/api/v1/intent/collect" "$body")
parse_response "$raw"
