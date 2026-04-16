---
name: xiaomi-cam-snapshot
description: 获取小米摄像头画面截图。当用户需要查看小米摄像头实时画面、获取摄像头截图、监控摄像头画面、或者提到"小米摄像头"、"摄像头截图"、"camera snapshot"、"摄像头画面"时使用此技能。支持列出摄像头、获取指定摄像头图片、自定义文件名等功能。
---

# 小米摄像头截图技能

通过 Miloco 后端服务获取小米摄像头的实时画面截图。

## 首次设置流程

### 步骤 1: 启动 Miloco 服务

```bash
docker run -d \
  --name miloco \
  --network host \
  -e BACKEND_PORT=8001 \
  ghcr.io/tiancheng91/miloco-backend:dev
```

### 步骤 2: 完成小米账号认证

服务启动后，引导用户完成以下操作：

1. **打开浏览器访问**: `http://localhost:8001`
2. **登录小米账号**: 使用小米账号完成登录认证
3. **设置密码**: 设置一个六位数字密码（用于后续 API 调用）

**等待用户确认**: 询问用户是否已完成认证和密码设置，等待用户回复"已完成"或"确认"后继续。

### 步骤 3: 验证配置

用户确认后，尝试获取摄像头列表验证配置是否成功：

```bash
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --list
```

### 步骤 4: 保存配置（可选）

如果获取摄像头列表成功，询问用户是否保存以下信息以便后续使用：

1. **密码**: 保存到 `MILOCO_PASSWORD` 环境变量或配置文件
2. **摄像头列表**: 记录摄像头 ID 和名称的对应关系

示例保存方式：
```bash
# 保存到环境变量（当前会话）
export MILOCO_PASSWORD="你的六位密码"

# 或保存到 shell 配置文件（永久保存）
echo 'export MILOCO_PASSWORD="你的六位密码"' >> ~/.zshrc
```

## 后续使用流程

完成首次设置后，后续可直接获取摄像头截图：

### 1. 确认服务状态

```bash
docker ps | grep miloco
```

如果服务未运行，先启动：
```bash
docker start miloco
```

### 2. 获取摄像头截图

```bash
# 使用已保存的密码环境变量
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password $MILOCO_PASSWORD \
  --camera-id "CAMERA_ID" \
  --output ./images
```

## 脚本功能说明

脚本位于 `scripts/camera_client.py`，支持以下功能：

### 列出所有摄像头

```bash
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --list
```

输出示例：
```
摄像头列表:
--------------------------------------------------------------------------------
  ID: 1036201996
  名称: 客厅摄像头
  在线: 是
  位置: 我家 - 客厅
--------------------------------------------------------------------------------
```

### 获取指定摄像头截图

```bash
# 使用默认文件名 (日期_did_时分秒.jpg)
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --camera-id "1036201996" \
  --output ./images

# 指定自定义文件名
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --camera-id "1036201996" \
  --output ./images \
  --filename "living_room_snapshot"
```

### 持续获取截图（监控模式）

```bash
# 每30秒获取一次
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --camera-id "1036201996" \
  --output ./images \
  --loop

# 每60秒获取一次，自动清理1天前的图片
python scripts/camera_client.py \
  --server http://localhost:8001 \
  --password YOUR_PASSWORD \
  --camera-id "1036201996" \
  --output ./images \
  --loop --interval 60 --cleanup
```

## 参数说明

| 参数 | 短参数 | 说明 | 必填 |
|------|--------|------|------|
| `--server` | `-s` | Miloco 服务器地址 | 是 |
| `--password` | `-p` | 密码（也可通过 `MILOCO_PASSWORD` 环境变量设置） | 是 |
| `--username` | `-u` | 用户名，默认 admin | 否 |
| `--list` | `-l` | 列出所有摄像头 | 否 |
| `--camera-id` | `-c` | 摄像头设备ID (did) | 否* |
| `--output` | `-o` | 输出目录，默认当前目录 | 否 |
| `--filename` | `-f` | 自定义文件名（不含扩展名） | 否 |
| `--loop` | | 持续获取图片 | 否 |
| `--interval` | `-i` | 循环间隔秒数，默认30 | 否 |
| `--cleanup` | | 自动清理过期图片 | 否 |
| `--cleanup-days` | | 清理多少天前的图片，默认1 | 否 |
| `--debug` | `-d` | 启用调试日志 | 否 |

\* 获取截图时必填

## 工作流程总结

```
首次使用:
┌─────────────────┐
│ 1. 启动 Docker  │
└────────┬────────┘
         ▼
┌─────────────────────────────────┐
│ 2. 引导用户访问 localhost:8001  │
│    完成小米账号认证 + 设置密码   │
└────────┬────────────────┘
         ▼
┌─────────────────────────────────┐
│ 3. 等待用户确认完成             │
└────────┬────────────────┘
         ▼
┌─────────────────────────────────┐
│ 4. 尝试获取摄像头列表           │
└────────┬────────────────┘
         ▼
┌─────────────────────────────────┐
│ 5. 询问是否保存密码和摄像头信息 │
└────────┬────────────────┘
         ▼
┌─────────────────────────────────┐
│ 6. 完成，可随时获取截图         │
└─────────────────────────────────┘

后续使用:
┌─────────────────┐
│ 确认服务运行    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 直接获取截图    │
└─────────────────┘
```

## 注意事项

- 确保摄像头设备在线才能获取截图
- 截图文件名默认格式：`日期_did_时分秒.jpg`
- 支持的图片格式：JPG、PNG（根据响应自动判断）
- 如果认证失败会自动重试登录一次
- 密码为六位数字，在 Miloco Web 界面设置

## 项目信息

- Miloco 项目地址: https://github.com/tiancheng91/xiaomi-miloco
- Docker 镜像: `ghcr.io/tiancheng91/miloco-backend:dev`
