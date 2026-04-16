#!/usr/bin/env bash
# 凭证状态检查 - GET /aia/api/v1/user/status/check（需鉴权）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

print_login_guidance() {
    echo "当前凭证可能已失效、无权限或未完成登录。请打开 https://tools.hundun.cn/h5Bin/aia/#/keys 登录混沌会员账号后，重新生成一个 hd_sk_ 开头的密钥发给 AI。拿到有效密钥后，我会继续当前任务。" >&2
}

load_config || exit 1

if [[ -z "$api_key" ]]; then
    print_login_guidance
    exit 1
fi

raw=$(curl -sS -w "\n%{http_code}" \
    -H "X-API-Key: $api_key" \
    -H "X-Disable-Compress: true" \
    "${base_url}/aia/api/v1/user/status/check")
output=$(parse_response "$raw" 2>&1)
status=$?

if [[ $status -eq 0 ]]; then
    printf '%s\n' "$output"
    exit 0
fi

if printf '%s' "$output" | grep -Eqi 'api[_ -]?key|密钥|鉴权|权限|401|403|unauthorized|forbidden|失效|未登录'; then
    print_login_guidance
    exit 1
fi

printf '%s\n' "$output" >&2
exit 1
