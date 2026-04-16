---
name: ip-diagnosis
description: 在 macOS + Chrome 上排查公网 IPv4/IPv6 出口、国家/地区、ASN/组织、DNS、默认路由、utun 状态，以及浏览器侧 Server Response 与 WebRTC 暴露情况。适用于用户要求检查 IP、地区一致性、VPN/代理接管情况、IPv6 问题或浏览器网络暴露，并输出详细运维报告与复查链接。
argument-hint: [可选：目标问题或补充上下文]
---

# IP Diagnosis

在 `macOS + Chrome` 上做详细网络诊断，并输出固定结构的运维报告。

## 适用场景

当用户要求以下任务时使用本技能：

- 检查当前公网 `IPv4` / `IPv6`
- 判断 `IPv4/IPv6` 是否地区分裂
- 检查 VPN / 代理是否只接管了部分流量
- 检查浏览器侧是否暴露了额外地址
- 比对命令行出口与浏览器页面看到的结果
- 输出一份可复查的详细网络诊断报告

本技能默认针对当前机器执行，不询问是否继续。

## 执行原则

1. 先补依赖，再做诊断
2. 先本地网络栈，再外部出口，再浏览器交叉验证
3. 至少两类外部来源交叉验证，不依赖单一站点
4. 报告里明确区分：
   - 已证实事实
   - 判断
   - 建议
5. `Server Response` 看到公网 IP，本身不等于浏览器泄露
6. 只有 `Via WebRTC` 暴露出额外私网或异常公网地址时，才判浏览器侧泄露风险

## 0. 依赖检查与安装

先检查：

```bash
command -v curl
command -v dig
command -v jq
command -v python3
command -v npm
command -v playwright-cli
command -v brew
open -Ra "Google Chrome"
```

默认依赖：

- `curl`
- `dig`
- `jq`
- `python3`
- `npm`
- `playwright-cli`
- `Google Chrome`

安装规则：

- 若 `playwright-cli` 缺失但 `npm` 不存在，且 `brew` 可用：
  ```bash
  brew install node
  ```
- 若 `playwright-cli` 缺失：
  ```bash
  npm install -g playwright-cli
  ```
- 安装后立刻校验：
  ```bash
  playwright-cli open --help
  ```
- 若 `Google Chrome` 不存在，明确写出阻塞项并停止；不要自动降级到其他浏览器
- 若 `playwright-cli` 能运行，但 `chrome` 浏览器通道打不开，再尝试：
  ```bash
  playwright-cli install-browser --browser chrome
  ```
- 若 `jq` 缺失且 `brew` 可用：
  ```bash
  brew install jq
  ```
- 若 `python3` 缺失且 `brew` 可用：
  ```bash
  brew install python
  ```

如果关键依赖无法安装，报告中明确写出阻塞项并停止，不要伪造结论。

## 1. 本地网络栈检查

按顺序执行：

```bash
route -n get default
route -n get default | awk '/interface:/{print $2}'
networksetup -listallhardwareports
netstat -rn -f inet6 | sed -n '1,80p'
scutil --dns
ifconfig | grep -E -A3 '^(en0|en1|utun[0-9]+):'
```

然后：

- 先从 `route -n get default` 提取当前默认接口，例如 `en0`
- 再用 `networksetup -listallhardwareports` 把接口映射到对应的网络服务名
- 只有在映射到明确服务名后，才执行：

```bash
networksetup -getinfo "<实际服务名>"
```

- 如果映射不出来，报告里写明 `networksetup service unresolved`，不要硬编码成 `Wi-Fi`

目标：

- 看默认路由走向
- 看 `IPv6` 默认路由是否经由 `utun`
- 看是否存在活跃 `utun`
- 看本地接口是否带原生 `IPv6`
- 看 `DNS` 是否像隧道私网解析器或本地直连解析器

## 2. 本地命令确认公网出口

至少执行：

```bash
curl --connect-timeout 8 --max-time 15 -4sS https://api.ipify.org
curl --connect-timeout 8 --max-time 15 -6sS https://api64.ipify.org
curl --connect-timeout 8 --max-time 15 -4sS https://ipinfo.io/json
curl --connect-timeout 8 --max-time 15 -6sS https://ipinfo.io/json
curl --connect-timeout 8 --max-time 15 -4sS https://ifconfig.co/json
curl --connect-timeout 8 --max-time 15 -6sS https://ifconfig.co/json
curl --connect-timeout 8 --max-time 15 -4sS https://api.ip.sb/geoip
curl --connect-timeout 8 --max-time 15 -6sS https://api.ip.sb/geoip
dig +short txt ch whoami.cloudflare @1.1.1.1
```

要求：

- 分别确认 `IPv4` 和 `IPv6`
- 尽量为两者都拿到：
  - IP
  - 国家 / 地区
  - ASN
  - 组织
- 如果 `-6` 查询失败，不要立刻判“没有 IPv6”
- 如果结果是 `::ffff:x.x.x.x` 这类 `IPv4-mapped IPv6`，不要把它当成独立公网 `IPv6`

## 3. Chrome 浏览器交叉验证

必须使用：

- [webbrowsertools IP Address](https://webbrowsertools.com/ip-address/)

推荐顺序：

```bash
playwright-cli open --browser=chrome https://webbrowsertools.com/ip-address/
playwright-cli eval "document.title"
playwright-cli eval "document.body.innerText"
playwright-cli snapshot
```

如需要，可再读取：

```bash
playwright-cli console
playwright-cli network
```

如果出现以下任一情况：

- 页面标题或正文包含 `请稍候`
- 页面标题或正文包含 `Just a moment`
- 页面标题或正文包含 `Verify you are human`
- 页面内容明显是 `Cloudflare` 挑战页
- `playwright-cli network` 或控制台显示主页面请求 `403`
- 页面里看不到 `IP Addresses`、`From Server Response`、`Via WebRTC` 这些关键分组

则执行一次受限重试：

```bash
playwright-cli close
playwright-cli open --browser=chrome --headed --persistent https://webbrowsertools.com/ip-address/
playwright-cli eval "document.title"
playwright-cli eval "document.body.innerText"
playwright-cli snapshot
```

如果重试后仍然是挑战页、403、或关键分组缺失：

- 不要让整份诊断失败
- 在报告中把浏览器交叉验证状态写成 `blocked by challenge / partial / unavailable`
- 明确记录看到的标题、错误、403 或挑战页提示
- 继续完成本地网络栈和外部出口部分的报告
- 把 `webbrowsertools` 标成“浏览器侧验证受阻，需人工复查”

报告里尽量详细记录这些动态结果分组：

- `IP Addresses`
- `From Server Response`
- `Remote Data`
- `Remote IP Services`
- `Via WebRTC`

如果页面上能看到具体行，尽量逐项列出，不要简单摘要。

重点字段通常包括：

- `HTTP_CLIENT_IP`
- `HTTP_CONNECTING_IP`
- `HTTP_COUNTRY_CODE`
- `HTTP_X_FORWARDED`
- `HTTP_X_CLUSTER_CLIENT_IP`
- `HTTP_FORWARDED_FOR`
- `HTTP_FORWARDED`
- `ipapi.co`
- `hostip.info`
- `ipify.org [IPv4]`
- `ipify.org [IPv6]`
- `ipecho.net`
- 各类 `STUN/WebRTC` 行

## 4. 报告输出格式

必须按以下结构输出。

### 结论

- 网络状态：`正常 / 有保留风险 / 明显异常`
- 一句话总结最关键问题

结论判定要求：

- 如果活跃网络服务明确显示 `IPv6 Off`，且：
  - 命令行出口与浏览器侧一致
  - 没有 `Via WebRTC` 额外地址
  - 没有证据表明存在独立公网 `IPv6`
  则默认写成 `正常（IPv6 已关闭）`
- 在上述场景下，不要仅因 `IPv6` 未确认就写成 `有保留风险`
- 只有在存在实际不一致、异常暴露、挑战页阻断关键验证、或 `IPv6` 仍然活跃但状态不清时，才升级为 `有保留风险`

### 证据

#### 本地检查

- `IPv4`：`<ip 或 未确认>`
- `IPv6`：`<ip 或 未确认>`
- `DNS`：`<解析器摘要>`
- `Default route`：`<网关 / 接口>`
- `utun`：`<存在 / 不存在 + 简述>`
- 本地接口 `IPv6`：`<摘要>`

#### 外部出口

- `IPv4`
  - IP
  - 国家 / 地区
  - ASN
  - 组织
  - 来源 1
  - 来源 2
- `IPv6`
  - IP
  - 国家 / 地区
  - ASN
  - 组织
  - 来源 1
  - 来源 2

如果某个来源失败，明确写：

- `Failed to fetch`
- `timeout`
- `blocked`
- `无独立公网 IPv6 证据`
- `待核实`

如果活跃网络服务明确显示 `IPv6 Off`，并且本地接口没有全局 `IPv6`：

- `IPv6` 证据优先写成 `无独立公网 IPv6 证据（IPv6 已关闭）`
- 不要优先写成 `待核实`
- 这里的 `IPv6 已关闭` 以 `networksetup -getinfo "<实际服务名>"` 返回的 `IPv6: Off` 为准

#### 浏览器交叉验证

- 页面： [webbrowsertools IP Address](https://webbrowsertools.com/ip-address/)
- 浏览器交叉验证状态：`success / partial / blocked by challenge / unavailable`
- `IP Addresses`
- `From Server Response` 各项
- `Remote Data` 各项
- `Remote IP Services` 各项
- `Via WebRTC` 各项

### 判断

必须显式回答：

- 是否存在 `IPv4/IPv6` 地区分裂：`是 / 否 / 待核实`
- 命令行出口与浏览器侧是否一致：`是 / 否 / 部分一致`
- 是否存在浏览器侧 `WebRTC` 泄露：`是 / 否 / 待核实`
- `Server Response` 中看到的公网地址是否只是直连网站的正常现象：`是 / 否`
- 是否确认存在独立公网 `IPv6`：`是 / 否 / 待核实`
- 浏览器交叉验证是否被挑战页或 403 阻断：`是 / 否`

### 解决方案

每条建议都要写：

- 适用条件
- 动作
- 为什么有效

建议顺序按优先级从高到低排列。

如果观察到 `IPv4` 与 `IPv6` 国家/地区不一致，必须给出 `macOS` 关闭 `IPv6` 的具体方式：

```bash
networksetup -listallnetworkservices
networksetup -setv6off "Wi-Fi"
```

如果需要恢复，补充：

```bash
networksetup -setv6automatic "Wi-Fi"
```

并明确提示用户：如果当前使用的网络服务不是 `Wi-Fi`，应先从 `networksetup -listallnetworkservices` 输出中找到正确服务名再执行。

如果观察到 `Via WebRTC` 暴露了额外私网或异常公网地址，可以把 Chrome 扩展作为浏览器侧缓解选项之一：

- [WebRTC Protect - Protect IP Leak](https://chromewebstore.google.com/detail/webrtc-protect-protect-ip/bkmmlbllpjdpgcgdohbaghfaecnddhni)

说明要点：

- 该扩展通过调整浏览器的 `WebRTC` 路由与隐私设置来减少私网和公网地址暴露
- 它可能影响依赖 `WebRTC` 的音视频或实时通信站点
- 只适用于 `WebRTC` 暴露问题，不解决网站通过正常直连请求看到的 `Server Response`

如果观察到某些站点显示的 `AS Name` / `ASN` 与当前 `HTTP` 出口 `IP` 的归属不一致，补充一条低优先级建议：

- 适用条件：`HTTP` 出口 `IP` 与多数外部来源一致，但某个站点展示的 `DNS ASN` / `AS Name` 指向其他组织或运营商
- 动作：明确告诉用户这通常是 `DNS` 解析器归属，而不是额外公网 `IP` 泄露；由用户自行决定是否继续处理
- 为什么有效：有些站点会同时检测 `HTTP` 出口和 `DNS` 解析器，页面上的 `AS Name` 可能反映递归解析器的 `ASN`，而不是当前网页连接出口的 `ASN`

如果用户决定继续处理该问题，只把下面这些动作作为可选项，不要默认推荐成必须修复：

- 手动修改 `macOS` 系统 `DNS`
- 在代理 / VPN 客户端中改用可达的 `DoH`
- 切换到能稳定接管系统 `DNS` 的客户端或模式

并明确说明：

- 单独的 `DNS ASN` 暴露通常不按高风险处理
- 是否处理取决于用户对运营商暴露、解析链路一致性和维护成本的容忍度

### 复查链接

至少包含：

- [webbrowsertools IP Address](https://webbrowsertools.com/ip-address/)
- 本次用到的外部查询源链接或域名

如果已经确认了具体公网 IP，建议额外给出把该 IP 直接带入的复查链接：

- `https://ping0.cc/ip/<detected-ip>`
- `https://iplark.com/<detected-ip>`
- `https://ipinfo.io/<detected-ip>`

这里的 `<detected-ip>` 应替换成报告中已确认的实际 `IPv4` 或 `IPv6`，不要硬编码成历史示例值。

当 `WebRTC` 暴露是问题的一部分时，一并给出：

- [WebRTC Protect - Protect IP Leak](https://chromewebstore.google.com/detail/webrtc-protect-protect-ip/bkmmlbllpjdpgcgdohbaghfaecnddhni)

## 5. 判读规则

- `From Server Response` 看见公网 IP：
  - 这是网站直连天然可见，不自动判浏览器泄露
- 只有 `Via WebRTC` 暴露额外私网或异常公网地址：
  - 才判为浏览器侧泄露风险
- `IPv4` 和 `IPv6` 国家/地区不同：
  - 判为地区分裂风险
  - 解决方案优先包含 `macOS` 关闭 `IPv6` 的具体命令
- `IPv6` 查询失败，但本地接口和路由表显示仍有 `IPv6`：
  - 写成 `IPv6 状态待核实`
- 如果活跃网络服务明确显示 `IPv6 Off`，且本地接口没有全局 `IPv6`，外部来源也没有独立公网 `IPv6` 证据：
  - `是否确认存在独立公网 IPv6` 写 `否`
  - `是否存在 IPv4/IPv6 地区分裂` 写 `否（IPv6 已关闭）`
  - 结论默认不要因此升级成 `有保留风险`
  - `utun` 上的 `fe80::`、链路本地 `IPv6` 地址、或残留 `inet6` 路由，不能单独推翻这个结论
- 多个来源在 ASN / 组织 / 地区上冲突：
  - 明确写 `来源不一致，需复查`
- 如果站点展示的 `AS Name` / `ASN` 与 `HTTP` 出口 `IP` 归属冲突，但 `HTTP` 出口 `IP` 本身在多数来源上一致：
  - 先判断该站点是否同时检测了 `DNS` 解析器
  - 优先写成 `DNS ASN 与 HTTP 出口 ASN 不一致`
  - 不要直接写成 `发现隐藏真实 IP` 或 `发生额外公网 IP 泄露`
  - 默认按低风险信息暴露处理，并交给用户自行决策是否继续收敛
- 没有独立公网 `IPv6` 证据：
  - 只能写 `未确认独立公网 IPv6`
  - 不要写成 `IPv6 正常`

## 6. 推荐外部来源

优先用这些来源做交叉验证：

- [ipinfo](https://ipinfo.io/json)
- [ifconfig.co](https://ifconfig.co/json)
- [api.ip.sb](https://api.ip.sb/geoip)
- [Cloudflare whoami TXT](https://1.1.1.1/help)

其中 `webbrowsertools` 只作为浏览器交叉验证页，不作为唯一真值来源。

## 7. 禁止事项

- 不要只引用一个 IP 查询站点
- 不要只看 `IPv4`
- 不要跳过浏览器交叉验证
- 不要把 `Server Response` 直接写成浏览器泄露
- 不要把单个外部站点失败当成最终结论
- 不要在未确认 `IPv6` 状态前草率下结论
