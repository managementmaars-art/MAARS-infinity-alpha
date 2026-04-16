#!/usr/bin/env bash

remote_is_wsl_env() {
  if [ -n "${WSL_DISTRO_NAME:-}" ] || [ -n "${WSL_INTEROP:-}" ]; then
    return 0
  fi

  if [ -r /proc/version ] && grep -qi 'microsoft' /proc/version; then
    return 0
  fi

  return 1
}

remote_detect_runtime_type() {
  if [ -n "${REMOTE_RUNTIME_TYPE:-}" ]; then
    printf '%s\n' "$REMOTE_RUNTIME_TYPE"
    return 0
  fi

  local uname_out
  uname_out="$(uname -s 2>/dev/null || printf 'unknown')"
  case "$uname_out" in
    MINGW*|MSYS*|CYGWIN*)
      printf 'windows-msys\n'
      ;;
    Linux)
      if remote_is_wsl_env; then
        printf 'linux-wsl\n'
      else
        printf 'linux-native\n'
      fi
      ;;
    Darwin)
      printf 'macos-native\n'
      ;;
    *)
      printf 'unknown\n'
      ;;
  esac
}

remote_detect_host_os() {
  case "$(remote_detect_runtime_type)" in
    windows-msys)
      printf 'windows\n'
      ;;
    linux-wsl|linux-native)
      printf 'linux\n'
      ;;
    macos-native)
      printf 'macos\n'
      ;;
    *)
      printf 'unknown\n'
      ;;
  esac
}

remote_detect_bash_flavor() {
  case "$(remote_detect_runtime_type)" in
    windows-msys)
      printf 'msys\n'
      ;;
    linux-wsl)
      printf 'wsl\n'
      ;;
    linux-native|macos-native)
      printf 'native\n'
      ;;
    *)
      printf 'unknown\n'
      ;;
  esac
}

remote_detect_sshpass_provider() {
  case "$(remote_detect_runtime_type)" in
    windows-msys)
      # Windows 使用 SSH_ASKPASS 机制，不需要 sshpass
      printf 'none\n'
      ;;
    linux-wsl|linux-native|macos-native)
      printf 'linux\n'
      ;;
    *)
      printf 'unknown\n'
      ;;
  esac
}

remote_print_runtime_summary() {
  printf 'runtime_type=%s\n' "$(remote_detect_runtime_type)"
  printf 'os_type=%s\n' "$(remote_detect_host_os)"
  printf 'bash_flavor=%s\n' "$(remote_detect_bash_flavor)"
  printf 'sshpass_provider=%s\n' "$(remote_detect_sshpass_provider)"
}

runtime_usage() {
  cat <<'EOF'
用法：
  runtime.sh runtime-type
  runtime.sh host-os
  runtime.sh bash-flavor
  runtime.sh sshpass-provider
  runtime.sh summary
EOF
}

runtime_main() {
  case "${1:-summary}" in
    runtime-type)
      remote_detect_runtime_type
      ;;
    host-os)
      remote_detect_host_os
      ;;
    bash-flavor)
      remote_detect_bash_flavor
      ;;
    sshpass-provider)
      remote_detect_sshpass_provider
      ;;
    summary)
      remote_print_runtime_summary
      ;;
    -h|--help|help)
      runtime_usage
      ;;
    *)
      runtime_usage
      return 2
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  set -euo pipefail
  runtime_main "$@"
fi
