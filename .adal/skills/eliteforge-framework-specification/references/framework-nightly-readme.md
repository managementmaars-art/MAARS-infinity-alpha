---
lang: zh-CN
title: 璀璨工坊统一框架-使用手册-nightly
version: nightly
description: 璀璨工坊统一框架-使用手册-nightly
---

# 璀璨工坊统一框架-使用手册-nightly

## 1 概述

> Warning:  
> nightly版本，包含实验性功能，后续可能发生较大变动。    

统一框架致力于帮助团队构建 **可治理、可演进、可规模化** 的Spring 生态微服务系统。

它以工程化核心，对 `SpringBoot 3.X` 框架及常用中间件组件给出明确、成熟的二次封装，让绝大多数系统无需重复进行基础设施选型与配置，即可获得生产级能力支持。  

统一框架适用于新项目快速落地，也同样适合存量系统的渐进式治理与演进。

### 1.1 为什么选择璀璨工坊统一框架

<h3>它解决的是“长期问题”，而不是短期便利</h3>
框架关注的是在复杂、长期运行的生产环境中，系统是否依然可控、可演进、可治理。  

在大量实际项目中，系统通常面临以下关键卡点：  

- **中间件资源争用严重**
多业务共享 Redis、MQ、线程池等中间件资源，缺乏统一隔离与配额控制，单一业务流量突增即可拖垮整套系统。

- **基础设施能力散落在各系统中**
缓存、加解密、对象存储、多数据源等能力以“复制代码 + 局部改造”的方式反复实现，标准不一、难以统一升级，隐性技术债不断累积。

- **系统配置高度耦合、难以治理**
大量配置硬编码在业务中，配置模型不统一，导致环境切换困难、问题定位成本高、线上变更风险不可控。

- **技术栈长期停留在 JDK 8 、SpringBoot 2 时代**
大量历史代码依赖过时 API、第三方库的旧版本，使团队在面对 JDK 17 / 21 及新一代 Spring 生态时被迫长期停留在 JDK 8，错失性能、安全性、语言特性、AI生态带来的红利，同时持续累积难以回避的技术债。

针对上述现实问题，框架提供了工程化层面的系统性支撑：
- 提供 **中间件与基础资源的规范化隔离能力** ，避免不同业务在同一物理资源上的无序竞争
- 在架构上 **天然适配云原生、容器化与服务网格体系** ，而非后期被动适配，为系统未来演进预留空间
- 持续演进并主动适配最新技术，通过向后兼容、统一引入的方式完成升级，使技术演进不再依赖单个系统的改造，而是让**所有系统在同一节奏下同时受益**。

### 1.2 核心特性

#### 1.2.1 提供标准化的对接能力

统一框架不是简单封装第三方组件，而是围绕 **统一规范** 与 **可控演进** 提供标准化基础能力：

- 统一配置规范与加载：提供标准化的公共配置文件，支持Spring Cloud Config 、K8S ConfigMap热更新
- 统一中间件抽象层，提供多种实现，屏蔽底层厂商的差异
- 统一基础设施：CICD、脚手架、AI Agent、AI MCP、Agent编排

核心价值在于 **“约束”**，而不是 **“功能数量”**。

#### 1.2.2 提供统一的Starter依赖治理 {#elite-forge-framework-feature-starter-list}

框架通过集中化的依赖管理机制，对所有starter的版本进行对齐与兼容性控制：
- 避免多服务间依赖版本漂移
- 降低框架升级对业务系统的侵入性

目前提供的starter清单：  
| 模块         | 类型    | starter名                                                              | 入口章节锚点        | 备注                                                                                 |
| ------------ | ------- | ---------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------ |
| Web MVC 基座 | Starter | `cisdigital-elite-forge-infra-web-spring-boot3-starter`                | `#5-3-web-mvc`      | Spring MVC 基座：ResVo、Filter/Interceptor、全局异常、多语言、多时区、统一序列化     |
| 服务间调用   | Starter | `cisdigital-elite-forge-infra-httpexchange-spring-boot3-starter`       | `#5-4-服务间调用`   | Spring 6 HttpExchange（RestClient 默认）；Header 透传、curl 日志、SSL、Mock 配置     |
| Mybatis-Plus | Starter | `cisdigital-elite-forge-infra-mybatis-plus-spring-boot3-starter`       | `#5-5-mybatis-plus` | 多租户隔离、审计字段、通用枚举、插件集合（分页/乐观锁/防全表/Dm 大小写转换等）       |
| 加解密       | Starter | `cisdigital-elite-forge-infra-crypto-spring-boot3-starter`             | `#5-6-加解密`       | AES/SM4/SM2/Base64/MD5/SHA/Hmac/SM3/脱敏；需注册 CryptoConfig 的序列化模块           |
| 缓存抽象层   | Starter | `cisdigital-elite-forge-infra-cache-spring-boot3-starter`              | `#5-7-缓存抽象层`   | CacheService 抽象；Redisson/Caffeine；资源池 var.yml + custom.yml；支持逻辑/物理隔离 |
| 多数据源     | Starter | `cisdigital-elite-forge-infra-dynamic-datasource-spring-boot3-starter` | `#5-8-多数据源`     | 主数据源 + 扩展数据源；`@DS("资源ID")` 切换；资源池化配置                            |
| 代码生成器   | Starter | `cisdigital-elite-forge-infra-code-generator`                          | `#5-9-代码生成器`   | 通过运行 `RunCodeGenerator` 执行生成；支持 CODE/HUMAN 模式                           |
| 资源抽象层   | Starter | `cisdigital-elite-forge-infra-resource-spring-boot3-starter`           | `#5-10-资源抽象层`  | 基于Spring Resource框架，扩展S3协议的资源交互                                        |

:::kb-tags
keywords: starter列表, starters, starter catalog, 统一框架starter, elite-forge starter, infra starters
query-hints: "有哪些starter", "starter清单", "starter列表", "统一框架有哪些starter"
:::

#### 1.2.3 约定优于配置，减少非必要复杂度

坚持 **约定优于配置（Convention over Configuration）** 的设计原则：
- 提供合理、可落地的默认配置
- 聚焦“80% 通用场景”，开箱即用，但不过度设计
- 保留必要扩展点，但不强迫业务理解全部细节

### 1.3 已接入团队

- 通用组件
- 基础框架
- 低开平台
- 五矿财务
- 五矿商旅
- 五矿资产
- 五矿合同
- 五矿商城
- 五矿冶金建设
- 基础服务平台
- 赛迪工单系统

## 2 系统要求

统一框架要求如下运行与构建环境：

**Java**  
JDK 21 或更高版本（编译与运行环境）  
所有模块均基于 Java 21 语言特性与字节码语义构建，推荐使用最新的长期支持发行版。

**Build Tools**  
- **Maven 3.9.10 或更高版本** 
框架及其 Starter 组件在 Maven 3.9.10+ 上提供明确支持，用于项目构建、依赖管理与插件执行。
- **Python 3.12 或更高版本**  
若使用框架生态中的辅助脚本、 本地规范校验、测试工具等需要 Python 3.12+ 环境。

**Servlet 容器**
支持部署在任何 兼容 Servlet 6.1+ 的容器 上（如最新版本的 Tomcat、TongWeb 等）。  
这确保 Web / HTTP 模块在标准 Java EE / Jakarta EE 容器中均可运行，无需额外适配层。  

## 3 接入统一框架

### 3.1 新项目直接在线生成

通过[CISDigital 项目生成器](/elite-forge/generator/)直接生成开箱即用的项目工程。  

### 3.2 存量项目手动升级

**1 统一 Parent 与 Properties**

在业务系统根 pom.xml 中统一继承 `build-parent`，并声明必要的版本属性：  

```xml
<parent>
  <groupId>cn.cisdigital</groupId>
  <artifactId>cisdigital-build-parent</artifactId>
  <version>最新的发布版本</version>
  <relativePath />
</parent>
```

```xml
<properties>
  <java.version>21</java.version>
  <!-- 当前项目的版本，不要修改，构建过程动态替换 -->
  <revision>nightly-SNAPSHOT</revision>

  <!-- JDK21统一依赖管理 -->
  <cisdigital-platform-jdk21-dependencies.version>
    最新发布的版本
  </cisdigital-platform-jdk21-dependencies.version>

  <!-- 统一框架依赖管理 -->
  <cisdigital-elite-forge-infra-dependencies.version>
    最新发布的版本
  </cisdigital-elite-forge-infra-dependencies.version>
</properties>
```

**2 导入统一依赖管理（BOM）**
在业务系统根 POM 中引入统一依赖管理，集中控制所有基础设施与第三方组件版本：  

```xml
<dependencyManagement>
  <dependencies>
    <!-- JDK 21 统一依赖管理 -->
    <dependency>
      <groupId>cn.cisdigital</groupId>
      <artifactId>cisdigital-platform-jdk21-dependencies</artifactId>
      <version>${cisdigital-platform-jdk21-dependencies.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>

    <!-- 统一框架依赖管理 -->
    <dependency>
      <groupId>cn.cisdigital.elite.forge.infra</groupId>
      <artifactId>cisdigital-elite-forge-infra-dependencies</artifactId>
      <version>${cisdigital-elite-forge-infra-dependencies.version}</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

**3 按需引入Starter**  

所有Starter由统一 BOM 管理版本，无需显式声明 `<version>`。  

```xml
<dependencies>
  <!-- 示例：仅接入动态数据源能力 -->
  <dependency>
    <groupId>cn.cisdigital.elite.forge.infra</groupId>
    <artifactId>
      cisdigital-elite-forge-infra-dynamic-datasource-spring-boot3-starter
    </artifactId>
  </dependency>

  <!-- 示例：一次性启用全部基础设施能力 -->
  <dependency>
    <groupId>cn.cisdigital.elite.forge.infra</groupId>
    <artifactId>
      cisdigital-elite-forge-infra-all-spring-boot3-starter
    </artifactId>
  </dependency>
</dependencies>
```

**4 增加国际化资源**

在spring国际化yaml配置中，添加：  

```yaml
spring:
  messages:
    basename: i18n/cisdigital-elite-forge-infra-framework
```

在 `resources` 目录下创建国际化资源文件夹 `i18n` ，目录结构如下：

```
resources
├── i18n
    ├── __serviceName__.properties
    ├── __serviceName___en_US.properties
    └── __serviceName___zh_CN.properties
```

**5 根据数据库类型划分mapper xml**  

框架可适配多种数据库。为确保 SQL 方言与映射文件匹配，需要将 MyBatis 的 Mapper XML 按数据库类型分别归档。  

在 `resources` 目录下创建mybaits mapper文件夹 `mapper`:  

```
resources
└──mapper
    ├── dm
    ├── mysql
    ├── oceanbase
    └── pg
```
随后将现有的 Mapper XML 文件，移动到对应数据库类型的目录中，以完成适配与加载。   

**6 调整yaml配置文件**

通过[CISDigital 项目生成器](/elite-forge/generator/)直接生成开箱即用的项目工程。  
然后参考boot模块下的配置文件进行调整，具体见[配置文件共识](#41-配置文件共识)。  

**7 调整项目根目录的规范文件**

通过[CISDigital 项目生成器](/elite-forge/generator/)直接生成开箱即用的项目工程。  
然后复制项目根目录的规范文件，到自己的项目中，具体见[项目规范文件共识](#41-项目规范文件共识)。

## 4 升级统一框架

> Tips:  
> 正常情况下，统一框架都会保证向下兼容升级。    
> 但最好查看每个版本的升级文档，做对应的配置调整，以达到最佳使用体验。

### 4.1 本次升级内容

注意！！， nightly版本，包含实验性功能，后续可能发生较大变动。    

### 4.2 升级步骤

1. 修改项目根pom中，统一框架的版本到期望的版本

```xml
<properties>
  <!-- 统一框架依赖管理 -->
  <cisdigital-elite-forge-infra-dependencies.version>
    nightly-SNAPSHOT
  </cisdigital-elite-forge-infra-dependencies.version>
</properties>
```   

## 5 使用统一框架

### 5.0 统一框架内置工具清单

#### 5.0.1 时间工具

**系统时钟**  
`cn.cisdigital.elite.forge.infra.commons.util.SystemClock`  
防止频繁调用 `System.currentTimeMillis()` 导致的性能问题。  
使用SystemClock.now()获取当前系统时间。  

**时间工具类**
`cn.cisdigital.elite.forge.infra.commons.util.TimeUtils`  
提供方便的时间类型的操作、转换、时区、格式化等能力，默认使用UTC时间。    
如：TimeUtils.nowLocalDateTime()。  

#### 5.0.2 Bean转换为Properties
`cn.cisdigital.elite.forge.infra.commons.util.PropertiesConvertUtils`  
提供将任意 Java Bean 转换为 Properties类的能力。  


#### 5.0.3 Spring上下文工具
`cn.cisdigital.elite.forge.infra.commons.util.SpringUtils`   
提供获取Spring上下文中的Bean、ActiveProfiles、Environment等信息的能力。  

使用案例：  

```java
SpringUtils.getApplicationName();
SpringUtils.getBean(MyService.class);
```

#### 5.0.4 Jackson Json转换

`cn.cisdigital.elite.forge.infra.commons.util.JsonUtils`  
使用统一的ObjectMapper配置，统一 JSON 解析与序列化行为。  

| 能力                   | 方法                                    |
| ---------------------- | --------------------------------------- |
| JSON → 对象            | `parseObject(String, Class<T>)`         |
| JSON → 泛型对象        | `parseObject(String, TypeReference<T>)` |
| JSON Array → List      | `parseList(String, Class<T>)`           |
| JSON Object → Map      | `parseMap(String, Class<K>, Class<V>)`  |
| JsonNode → 对象        | `parseObject(JsonNode, Class<T>)`       |
| JSON String → JsonNode | `readTree(String)`                      |
| 对象 → JSON String     | `toJsonString(Object)`                  |

#### 5.0.5 国际化工具

`cn.cisdigital.elite.forge.infra.commons.util.I18nUtils`  
统一国际化消息获取方式。  

| 能力                                 | 方法                                           |
| ------------------------------------ | ---------------------------------------------- |
| 根据上下文中的 Locale 获取文案       | `getMessage(String)`                           |
| 根据上下文中的 Locale + 参数获取文案 | `getMessage(String, Object[])`                 |
| key 不存在时返回默认文案             | `getMessageWithDefault(String, String)`        |
| key 不存在时返回 key 本身            | `getOriginMessageIfNotExits(String)`           |
| key 不存在时返回 key（带参数）       | `getOriginMessageIfNotExits(String, Object[])` |

#### 5.0.6 模糊查询转译工具

`cn.cisdigital.elite.forge.infra.commons.util.EscapeKeywordUtils`  
为 SQL LIKE 模糊查询提供统一、可控的关键字转义能力，避免通配符误匹配与潜在注入风险。  

在 LIKE 查询中，以下字符具有特殊含义：  
```
%  _  \  [  ]  ^  "  '
```

如果用户输入未转义，会导致：
  - 模糊范围扩大
  - 查询结果不可预期，不准确
  - 极端情况下放大 SQL 注入风险
  
| 能力                                                                                  | 方法                        |
| ------------------------------------------------------------------------------------- | --------------------------- |
| 将字符串中的 `"%", "_", "\\", "[", "]", "^", "\"", "'"` 进行转译                      | `formatKeyword(String)`     |
| 根据Active Profiles激活的数据库类型，获取对应数据库的 escape 字符                     | `getEscapeCharByEnv()`      |
| 根据Active Profiles激活的数据库类型，根据对应数据库的书写习惯，得到大写或小写后的文本 | `getFieldNameByEnv(String)` |

#### 5.0.7 上下文工具
`cn.cisdigital.elite.forge.infra.commons.context.ContextStore`  
通用请求上下文存储工具，基于TTL实现，支持嵌套（栈式）上下文 、支持线程池/异步透传。  

| 能力                     | 方法                                       |
| ------------------------ | ------------------------------------------ |
| 获取当前请求上下文       | `currRequestContext()`                     |
| 获取当前应用+租户信息    | `currentAppAndTenant()`                    |
| 获取上下文值             | `getContext(String)`                       |
| 获取上下文值（带默认值） | `getContextOrDefault(String, T)`           |
| 单上下文执行             | `executeWithContext(...)`                  |
| 多上下文执行（Map）      | `executeWithContexts(Map, Supplier)`       |
| 多上下文执行（可变参数） | `executeWithContexts(Supplier, Object...)` |
| 清理所有上下文           | `clear()`                                  |

> Tips:
> 请查阅 `TransmittableThreadLocal（TTL）` 官方文档，了解如何在线程池、父子线程中正确传递参数  

### 5.1 项目规范文件共识

以下项目文件必须存在，且不能修改：  

```
.
├── .editorconfig             编辑器配置
├── .gitignore                git忽略文件配置
├── .gitlab                   gitlab仓库配置
├──├── merge_request_templates  MR默认模版
├── .gitlab-ci.yml            ci远程配置
├── .mvn                      maven wrapper配置
├── .pre-commit-config.yaml   本地校验配置
├── lombok.config             lombok配置文件
├── Makefile                  封装了常用的项目构建命令
├── mvnw                      maven wrapper命令
├── mvnw.cmd                  maven wrapper命令 for windows
└── readme.md                 项目说明
```

### 5.2 YAML配置文件共识

boot模块中，`resources`文件夹下，配置文件结构如下： 
```
├── application.yml
├── config
│   ├── application-dm.yml
│   ├── application-mysql.yml
│   ├── application-oceanbase.yml
│   ├── application-pg.yml
│   └── custom.yml
├── env
│   ├── <服务名>-common-config.yml
└── └── <服务名>-var.yml
```


- **application.yml**: 配置文件加载的总入口，此配置会按照顺序加载env、config文件夹下的其他配置文件，后加载的配置会覆盖前面的配置  
- **env/common-config.yml**: 公共配置，spring框架的一些共性模板配置，配置的值会从 `custom.yml` 或 `env/var.yml` 中加载  
- **env/var.yml**: 公共变量，存放当前环境下的一些中间件地址、账号、密码、域名等信息，运维人员只需要修改此配置文件即可
- **config/custom.yml**: 应用配置，存放当前应用自己的一些配置项，环境中的值需要从 `env/var.yml` 中读取  
- **config/application-xx.yml**: 数据库配置，针对不同的数据库的个性化配置项

应用只允许修改 `config/custom.yml` 中的配置项，其余配置文件，均不允许修改，特殊情况需找技术委员会评审。  

### 5.3 Web Mvc

> cisdigital-elite-forge-infra-web-spring-boot3-starter

#### 5.3.1 核心特性
为应用提供统一的 Spring MVC 基座能力。  

##### 5.3.1.1 统一返回对象

所有请求的响应都使用 `ResVo` 对象进行包装，如：
```java
import cn.cisdigital.elite.forge.infra.commons.model.vo.ResVo;
import cn.cisdigital.demo.user.service.UserService;
import cn.cisdigital.demo.user.vo.UserVo;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Slf4j
@RestController
@RequestMapping("/foo/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/test")
    public ResVo<UserVo> getUserById(@RequestParam("userId") Long userId) {
        return ResVo.ok(userService.getUserById(userId));
    }
}
```

##### 5.3.1.2 过滤器&拦截器

过滤器顺序：  
ExceptionFilter(1) → TraceIdFilter(10) → ContextFilter(20) → AuthFilter(30)

**ExceptionFilter**  
兜底 Filter 层异常，通过 `/filter/error` 转交到 Spring MVC，保证所有异常统一走 `GlobalExceptionHandler`。  

**TraceIdFilter**  
确保每个请求带有 `request-id`（若无则自动生成 TSID），并通过 `MDC` 和响应头回传，方便链路追踪。  


**ContextFilter**  
在 Web 请求进入业务层之前，从 `HttpServletRequest` 中统一解析并构建请求上下文信息，最后统一存储到 `ContextStore` 对象中，供后续获取用户信息、权限控制、多租户、审计等基础能力使用。  

默认提供的上下文策略为，五矿财务管控项目请求上下文策略，该策略会从请求Header中读取以下内容：
- `Authorization`: 用户令牌
- `Menu-Id`: 菜单标识
- `Super-Admin`: 超级管理员标识
- `User-Id`: 登录用户ID
- `User-Code`: 登录用户编码
- `User-Name`: 登录用户姓名
- `Org-Id`: 登录用户所属组织ID
- `Org-Code`: 登录用户所属组织编码
- `Tenant-Id`: 资源隔离id
- `Accept-Language`: 当前用户使用的语言
- `Timezone`: 当前请求使用的时区信息，如 `Asia/Shanghai`

**AuthFilter**  
在认证阶段基于 `已构建的请求上下文` 对当前请求进行合法性校验，决定请求是否具备继续处理的条件。  

默认提供的认证策略为，五矿财务管控项目认证策略，该策略认证逻辑为：  
- 只针对前端接口进行认证，匹配：
  - /{serviceName}/api/**
  - /{productName}/{serviceName}/api/**
- 从 `ContextStore.currRequestContext()` 中获取当前请求对应的 RequestContext
- 应用信息（appId）是否存在（可配置）
- 资源隔离标签（tenantId）必须存在
- 用户信息必须都存在
  - userId
  - userName
  - userCode
以上条件全部满足，则认为是合法的前端请求。  

**RequestLogInterceptor**  
用于打印请求信息，会在非 `/filter/error` 与 `/actuator/**` 请求上打印：
  - 必要请求头 (`App-Id`、`Tenant-Id`、`User-Id`、`Org-Id` 等)
  - 查询参数（自动解码 GET Query）
  - 请求耗时与响应头

##### 5.3.1.3 全局异常处理

> 异常类的错误码遵守[错误码规范](/elite-forge/error-code-specification/)  

提供 `GlobalExceptionHandler` 统一拦截并处理系统异常，覆盖以下常见场景：
  •	业务异常（BizException）
  •	认证与鉴权异常（AuthException、ForbiddenException）
  •	参数校验异常（JSR-303）
  •	国际化消息缺失（NoSuchMessageException）
  •	请求体解析异常（HttpMessageNotReadableException）等

异常返回的 message 信息统一通过 `I18nUtils` 进行国际化解析，避免业务代码直接处理多语言逻辑。

##### 5.3.1.4 多语言

> 多语言遵守[国际化规范](/elite-forge/i18n-specification/)  

ProjectResourceBundleMessageSource 支持跨模块加载 `spring.messages.basename` 配置的多个资源文件。  

多语言在框架层面，对以下范围进行了自动处理：  
- JSR303校验注解的message属性
- `BizEnum` 的messageKey字段
- `ErrorCode` 的messageKey字段
- `@Slf4j` log.info打印日志

在上述场景中，仅需使用国际化资源properteis文件中定义的 key，框架即可根据当前请求语言环境自动解析并输出对应语言的内容，无需在业务代码中显式处理多语言逻辑。  

##### 5.3.1.5 多时区

后端基础容器镜像默认配置 TZ=UTC，所有后端服务 统一以 UTC 作为内部时间基准，避免因部署环境或节点差异导致的时间偏移问题。  

统一框架在此基础上提供 `TimeUtils` 工具类，用于时间获取、转换与计算，作为系统内处理时间相关逻辑的唯一推荐入口，确保时间语义在多时区、多环境场景下保持一致。

##### 5.3.1.6 序列化与反序列化

> 序列化遵守[前后端开发共识](/elite-forge/code-specification/be-fe/v1/)  

通过 `MvcAutoConfiguration` 移除 Spring MVC 默认的 MappingJackson2HttpMessageConverter，统一替换为基于 `ObjectMapperHolder.OBJECT_MAPPER` 的消息转换器实现，确保序列化行为在整个框架范围内保持一致，包括：
- Long 类型精度处理
- Java 8 时间类型序列化
- 枚举序列化与反序列化策略等

##### 5.3.1.7 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `ResVo<T>` | `cn.cisdigital.elite.forge.infra.commons.model.vo.ResVo` | `code`、`message`、`data`、`requestId`、`error` | `ok(...)`、`error(...)` |
| `AuthenticationStrategy` | `cn.cisdigital.elite.forge.infra.web.mvc.filter.auth.AuthenticationStrategy` | 无 | `authenticate(HttpServletRequest)` |
| `RequestContextStrategy` | `cn.cisdigital.elite.forge.infra.web.mvc.filter.context.RequestContextStrategy` | 无 | `resolveRequestContexts(...)`、`resolveAdditionalContexts(...)` |
| `ObjectMapperPostProcessor` | `cn.cisdigital.elite.forge.infra.web.mvc.serializer.ObjectMapperPostProcessor` | 无 | `postConfig(ObjectMapper)` |
| `CustomInterceptor` | `cn.cisdigital.elite.forge.infra.web.mvc.interceptor.CustomInterceptor` | 无 | `pathPatterns()`、`excludePathPatterns()` |


#### 5.3.2 引入Starter 

```xml
<dependencies>
    <dependency>
        <groupId>cn.cisdigital.elite.forge.infra</groupId>
        <artifactId>cisdigital-elite-forge-infra-web-spring-boot3-starter</artifactId>
    </dependency>
</dependencies>
```

#### 5.3.3 配置starter

一般情况，无需任何yaml配置，开箱即用。  
启动服务，发现以下日志，即说明web starter已经生效：  
```
[自动装配] 注册elite-forge ResourceBundle国际化资源
[自动装配] 注册elite-forge exceptionFilter
[自动装配] 注册elite-forge authfilter
[自动装配] 注册elite-forge traceIdFilter
[自动装配] 注册elite-forge ObjectMapper
[自动装配] 注册elite-forge SpringUtils
[自动装配] 注册elite-forge MappingJackson2HttpMessageConverter
[自动装配] 注册elite-forge 五矿财务管控项目认证策略
[自动装配] 注册elite-forge 五矿财务管控项目请求上下文策略
```

##### 5.3.3.1 yaml全量配置 

```yaml
elite-forge-framework:
  web:
    # 上下文过滤器配置
    context-filter:
      # 是否开启此过滤器，默认开启
      # 开启后会根据上下文获取策略，将请求中的数据设置到上下文ContextStore中，供后续使用
      enabled: true
    # 认证过滤器配置
    auth-filter:
      # 是否开启此过滤器，默认开启
      # 开启后会根据认证策略，对前端请求进行认证
      enabled: true
      # 白名单配置，白名单内的接口，可跳过认证
      white-list:
        # 支持Ant匹配
        - /demo-service/api/user/login/**
        - /**/api/actuator/**
```

#### 5.3.4 扩展starter

| 扩展点                                       | 说明                                                                                                                                     |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `CustomInterceptor`                          | 自定义拦截器实现此接口，并注册为bean即可。通过实现 pathPatterns() / excludePathPatterns() 方法，精确控制拦截器的生效路径范围。           |
|                                              |
| `CustomConverter` / `CustomConverterFactory` | 实现此接口，并注册为bean即可。自定义扩展 Spring MVC 的参数绑定与转换能力，为 @RequestParam、@PathVariable 等场景提供额外的类型转换支持。 |
| `ObjectMapperPostProcessor`                  | 实现此接口，并注册为bean即可。例如注册自定义 Module、Serializer、Deserializer，在不破坏框架默认序列化策略的前提下进行扩展                |
| `AuthenticationStrategy`                     | 实现此接口，并注册为bean即可。提供AuthFilter使用的认证策略。                                                                             |
| `RequestContextStrategy`                     | 实现此接口，并注册为bean即可。提供ContextFilter使用的读取请求上下文策略。                                                                |

##### 示例1：为 `LocalDate` 添加全局的自定义序列化

```java
import cn.cisdigital.elite.forge.infra.web.mvc.serializer.ObjectMapperPostProcessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Component
public class LocalDateObjectMapperCustomizer implements ObjectMapperPostProcessor {

    @Override
    public void postConfig(ObjectMapper mapper) {
        mapper.registerModule(new JavaTimeModule()
            .addSerializer(LocalDate.class, new LocalDateSerializer(DateTimeFormatter.BASIC_ISO_DATE)));
    }
}
```

##### 示例2：使用自己的请求上下文处理逻辑

```java
import cn.cisdigital.elite.forge.infra.web.mvc.filter.context.RequestContextStrategy;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;
import java.util.Map;

/**
 * 自定义上下文获取逻辑
 */
@Slf4j
@RequiredArgsConstructor
public class CustomRequestContextStrategy implements RequestContextStrategy {

    @Override
    public Map<String, Object> resolveRequestContexts(HttpServletRequest request) {
        Map<String, Object> contextMap = new HashMap<>();
        // 自己处理如何从request读取数据，放到contextMap里即可
        return contextMap;
    }
}
```

然后将此策略注册为bean：
```java
import cn.cisdigital.elite.forge.infra.web.mvc.filter.context.RequestContextStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class WebMvcContextStrategyConfiguration {

    private static final Logger log = LoggerFactory.getLogger(WebMvcContextStrategyConfiguration.class);

    @Bean
    @Primary
    public RequestContextStrategy requestContextStrategy() {
        log.info("[自动装配] 注册自定义请求上下文策略");
        return new CustomRequestContextStrategy();
    }
}
```

再此过滤器之后，就可以通过 `ContextStore.getContext("key")` 获取到上下文信息。  

##### 示例3：使用自己的认证逻辑

```java
import cn.cisdigital.elite.forge.infra.web.mvc.filter.auth.AuthenticationStrategy;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * 自定义认证逻辑
 */
@Slf4j
@RequiredArgsConstructor
public class CustomAuthenticationStrategy implements AuthenticationStrategy {

    @Override
    public void authenticate(HttpServletRequest request) {
        // 自定义如何从ContextStore中读取数据
        // 自定义如何进行认证，认证失败直接抛出AuthException异常
    }
}
```

然后将此策略注册为bean：
```java
import cn.cisdigital.elite.forge.infra.web.mvc.filter.auth.AuthenticationStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class WebMvcAuthStrategyConfiguration {

    private static final Logger log = LoggerFactory.getLogger(WebMvcAuthStrategyConfiguration.class);

    @Bean
    @Primary
    public AuthenticationStrategy authenticationStrategy() {
        log.info("[自动装配] 注册自定义认证策略");
        return new CustomAuthenticationStrategy();
    }
}
```

### 5.4 服务间调用

> cisdigital-elite-forge-infra-httpexchange-spring-boot3-starter

#### 5.4.1 核心特性
为应用提供统一的，服务间调用能力。  

##### 5.4.1.1 预留了扩展点，同时支持RestClient和WebClient

目前底层默认使用RestClient进行接口调用，WebClient未完全测试。

##### 5.4.1.2 保持与OpenFeign一致的使用习惯

新框架里不会使用 `Spring Cloud OpenFeign` 而使用 Spring 6 原生的 `HttpExchange` 。  
开发者只需通过声明式接口 + 注解即可完成远程 HTTP 调用的定义，无需手动编写 RestTemplate / WebClient 等模板代码。  
**注解和yaml配置都是尽可能贴近OpenFeign的方式，以前如何使用OpenFeign，现在就如何使用HttpExchange。**  

类级注解对照表：  
| Feign                | HttpExchange                | 说明                   |
| -------------------- | --------------------------- | ---------------------- |
| `@EnableFeignClient` | `@EnableHttpExchange`       | 开启客户端扫描         |
| `basePackages`       | `basePackages`              | 指定扫描client的包路径 |

| Feign            | HttpExchange          | 说明                                         |
| ---------------- | --------------------- | -------------------------------------------- |
| `@FeignClient`   | `@HttpExchangeClient` | 声明远程 HTTP 客户端                         |
| `name` / `value` | `name`                | 服务名，保持与波塞冬的应用名一致             |
| `path`           | `path`                | controller路径前缀                           |
| `url`            | `url`                 | 指定url后直接用url调用，不会用name           |
| 无               | `mockUrl`             | torna mock地址 / 本地调试 / 测试环境替代地址 |
| `contextId`      | （不需要）            | 接口注册天然唯一                             |

方法注解对照表：
| Feign                         | HttpExchange 注解 | HTTP 方法 | 说明                   |
| ----------------------------- | ----------------- | --------- | ---------------------- |
| `@GetMapping`                 | `@GetExchange`    | GET       |                        |
| `@PostMapping`                | `@PostExchange`   | POST      |                        |  |
| `@RequestMapping(method = …)` | （不支持）        | —         | 明确禁止，避免语义歧义 |

参数注解对照表(限定只允许使用以下注解)：  
| Feign            | HttpExchange     | 说明             |
| ---------------- | ---------------- | ---------------- |
| `@RequestParam`  | `@RequestParam`  | Query 参数       |
| `@RequestHeader` | `@RequestHeader` | 增加Header 参数  |
| `@RequestBody`   | `@RequestBody`   | 请求体           |
| `@RequestPart`   | `@RequestPart`   | 用于处理文件片段 |

> Tips:  
> RestClient并不是所有MVC的注解都支持，WebClient也是如此，具体见[官方文档说明](https://docs.spring.io/spring-framework/reference/6.0/integration/rest-clients.html#rest-http-interface-method-parameters)  

##### 5.4.1.3 保持与MVC一致的序列化、反序列化

RestClient 与 Web Mvc 使用相同的 `cn.cisdigital.elite.forge.infra.commons.serialize.ObjectMapperHolder` Jackson配置。  

##### 5.4.1.4 支持配置SSL证书

- 支持自定义 `SSL` 证书信任策略（证书需要以文本方式挂载到应用容器里）。
- 支持多协议版本（`TLSv1.2`、`TLSv1.3`）；
- 默认忽略 SSL 证书验证

##### 5.4.1.5 支持Header透传

目前RestClient会透传上下文中的以下 **不为空的** 数据：  
| Header名        | ContextStore中的Key | 备注                                                                 |
| --------------- | ------------------- | -------------------------------------------------------------------- |
| App-Id          | app_id              | 来自@HttpExchangeClient注解中的name属性                              |
| Tenant-Id       | tenant_id           | 从前端请求中获取，或者自己手动设置到上下文中                         |
| User-Id         | principal_id        | 从前端请求中获取，或者自己手动设置到上下文中                         |
| User-Code       | principal_code      | 从前端请求中获取，或者自己手动设置到上下文中                         |
| User-Name       | principal_name      | 从前端请求中获取，或者自己手动设置到上下文中。  会对值进行URL Encode |
| Org-Id          | org_id              | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Org-Code        | org_code            | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Menu-Id         | menu_id             | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Super-Admin     | super_admin         | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Env             | env                 | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Accept-Language | language_tag        | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Authorization   | token               | 从前端请求中获取，或者自己手动设置到上下文中。                       |
| Timezone        | timezone            | 从前端请求中获取，或者自己手动设置到上下文中。                       |

##### 5.4.1.6 支持打印请求日志

默认启用了日志打印，请求会直接以CRUL的形式打印出来，方便排查问题。  

```
[HttpExchange][RestClient] curl -i -X POST 'http://localhost:8080/first/xxx' \
 -H 'App-Id: mock-service-one' \
 -H 'Tenant-Id: tenant_001' \
 -H 'User-Id: 10086' \
 -H 'User-Code: cloud_s3n' \
 -H 'User-Name: Cloud%20Sen' \
 -H 'Org-Id: org_1001' \
 -H 'Org-Code: ORG_HQ' \
 -H 'Menu-Id: menu_2001' \
 -H 'Super-Admin: false' \
 -H 'Env: prod' \
 -H 'Accept-Language: zh-CN' \
 -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...' \
 -H 'Content-Type: application/json' \
 -H 'Accept: application/json' \
 --data '{"orderId":123456,"amount":99.50}'
```

##### 5.4.1.7 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `EnableHttpExchange` | `cn.cisdigital.elite.forge.infra.httpexchange.annotation.EnableHttpExchange` | `BASE_PACKAGES` | `basePackages()` |
| `HttpExchangeClient` | `cn.cisdigital.elite.forge.infra.httpexchange.annotation.HttpExchangeClient` | 注解属性：`name`、`path`、`url`、`mockUrl` | `name()`、`path()`、`url()`、`mockUrl()` |
| `CallServerWrapper` | `cn.cisdigital.elite.forge.infra.httpexchange.support.CallServerWrapper` | `REQUEST_ID_KEY`、`REMOTE_RESULT` | `getWithoutData(...)`、`checkObjectResult(...)`、`checkVoidResult(...)`、`getData(...)`、`getNonNullData(...)` |

#### 5.4.2 引入starter

```xml
<dependencies>
    <dependency>
        <groupId>cn.cisdigital.elite.forge.infra</groupId>
        <artifactId>cisdigital-elite-forge-infra-httpexchange-spring-boot3-starter</artifactId>
    </dependency>
</dependencies>
```

#### 5.4.3 配置starter

##### 5.4.3.1 最小配置

最小接入只需在服务启动类上，开启 `EnableHttpExchange` 的包扫描即可，一般情况，无需任何yaml配置，开箱即用。 

```java
import cn.cisdigital.elite.forge.infra.httpexchange.annotation.EnableHttpExchange;
import org.springframework.context.annotation.Configuration;

@Configuration
// 添加此注解，配置自己的包
@EnableHttpExchange(basePackages = "cn.cisdigital.demo.http")
public class HttpExchangeConfiguration {

}
```

启动服务，发现以下日志client相关的注册日志，代表已经生效：  

```
已注册HttpExchangeClient [xxx], 使用的Bean Name: xxx
```

##### 5.4.3.2 yaml全量配置说明

```yaml
elite-forge-framework:
  http-exchange:
     # 是否打印 curl 日志，默认 true，支持实时生效
    print-curl: true
    # 是否全局启用 Mock，默认 false
    enable-mock: false
    # 接口调用时，是否使用 https，默认 false
    use-https: false
    # 所有客户端的默认配置
    defaults:
      # 请求发起的端口，默认8080
      # 仅在 Mesh 且未使用url时生效
      port: 8080
      # 指定客户端类型 rest-client | web-client，默认rest-client
      client-type: rest-client
      # 指定负载均衡类型 mesh | client，默认mesh
      # mesh为服务端负载均衡;client代表客户端负载均衡，如SpringCloud Loadbalancer
      loadbalance: mesh
      # SSL的配置
      ssl:
        # 是否忽略 SSL 证书验证，默认true
        trust-all: true
        # 是否忽略主机名验证，默认false
        ignore-hostname-verification: false
        # KeyStore 路径，指定容器里的路径
        key-store: ""
        # KeyStore 密码
        key-store-password: ""
        # KeyStore 类型JKS |PKCS12，默认JKS
        key-store-type: JKS
        # TrustStore 路径，指定容器里的路径
        trust-store: ""
        # TrustStore 密码
        trust-store-password: ""
        # TrustStore类型JKS |PKCS12，默认JKS
        trust-store-type: JKS
        # 支持的 TLS 协议版本
        enabled-protocols:
          - TLSv1.2
          - TLSv1.3
      # okhttp客户端配置
      okhttp:
        # 连接超时时间，最小值10s，默认10s
        connect-timeout: 10
        # 读取超时时间，最小值10s，默认10s
        read-timeout: 10
        # 写超时时间，最小值10s，默认10s
        write-timeout: 10
        # 请求调用的超时时间，最小值60s，默认60s
        call-timeout: 60
        # 否在连接失败时重试，默认true
        retry-on-connection-failure: true
        # 最大请求数，最小值1，默认100
        max-requests: 100
        # 每个host的最大请求数，最小值1，默认100
        max-requests-per-host: 10
        connection-pool:
          # 连接池，最大idle连接数，最小值1，默认5
          max-idle-connections: 5
          # idle连接的最小保持时间(分钟)，最小值1，默认5分钟
          keep-alive-duration: 5m
          # 连接池最大连接数，默认200
          max-connections: 200
          # 获取连接的最大等待数
          pending-acquire-max-count: 50
          # 获取连接超时时间（秒），默认5
          pending-acquire-timeout-seconds: 5
          # 空闲连接最大存活时间（秒），默认30
          max-idle-time-seconds: 30
          # 连接最长生命周期（分钟），默认5
          max-life-time-minutes: 5
          # 后台清理频率（秒），默认30
          evict-in-background-seconds: 30
          # 连接超时时间（毫秒），默认5秒
          connect-timeout-millis: 5000
          # 响应超时时间（秒），默认10秒
          response-timeout-seconds: 10
    # 客户端个性化配置
    clients:
      # 针对哪个客户端的配置，对应@HttpExchangeClient的name属性
      mock-service-one:
        # 当前 client ，发起请求的端口，不配则使用 defaults 的配置
        # 仅在 Mesh 且未使用url时生效
        port: 8080
        # 当前客户端是否启用 Mock，不配则使用 defaults 的值
        enable-mock: false
        # 真实服务地址，配置后请求的路径不再使用 name
        url: http://www.baidu.com
        # 覆盖@HttpExchangeClient的mockUrl属性，mock开启时，使用此地址
        mock-url: http://mock.local
```

#### 5.4.5 使用starter

##### 5.4.5.1 服务提供方

在 `client` maven模块下，定义innerApi接口：  
```java
import cn.cisdigital.elite.forge.infra.commons.model.vo.ResVo;
import cn.cisdigital.elite.forge.infra.httpexchange.annotation.HttpExchangeClient;
import cn.cisdigital.demo.http.vo.FooVo;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.GetExchange;

@HttpExchangeClient(name = "与spring.application.name一致", path = "/服务前缀/innerApi/xxx", mockUrl="tornar上的mock地址前缀")
public interface FirstTestClient {

    @GetExchange("/xxx")
    ResVo<FooVo> getXXX(@RequestParam("id") String id);
}
```

在 `biz` maven模块下，实现xxxInnerController接口：  

```java
import cn.cisdigital.elite.forge.infra.commons.model.vo.ResVo;
import cn.cisdigital.demo.http.client.FirstTestClient;
import cn.cisdigital.demo.http.service.FirstTestService;
import cn.cisdigital.demo.http.vo.FooVo;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/服务前缀/innerApi/xxx")
@RequiredArgsConstructor
public class FirstTestInnerController implements FirstTestClient {

    private final FirstTestService fts;

    @Override
    public ResVo<FooVo> getXXX(@RequestParam("id") String id) {
        return ResVo.ok(fts.getXXX(id));
    }
}
```

对外发布client maven模块：  
```bash
make deploy VERSION=xxx MODEL=<指定到client模块>
```

##### 5.4.5.2 服务使用方

根pom管理，服务提供方的client包：  

```
<properteis>
  <xxx-client.version>client的版本</xxx-client.version>
</properties>

<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>xxxx</groupId>
      <artifactId>xxx-client</artifactId>
      <version>${xxx-client.version}</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

在biz模块，引入client包：  

```
<dependencies>
  <dependency>
    <groupId>xxxx</groupId>
    <artifactId>xxx-client</artifactId>
  </dependency>
</dependencies>
```

启动类上，开启扫描：  
```java
import cn.cisdigital.elite.forge.infra.httpexchange.annotation.EnableHttpExchange;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@EnableHttpExchange(basePackages = "cn.cisdigital.demo.http")
@SpringBootApplication
public class xxxApplication {
}
```

在业务服务中，引入client使用：  
```java
import cn.cisdigital.demo.http.client.FirstTestClient;
import cn.cisdigital.demo.http.vo.FooVo;
import cn.cisdigital.elite.forge.infra.httpexchange.support.CallServerWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class DemoService {

    private final FirstTestClient firstTestClient;

    public String callRemote() {
        // 这里使用了方便取值的包装器，后面有说明
        Optional<FooVo> fooOpt = CallServerWrapper.getData(() -> firstTestClient.getXXX("1001"));
        return fooOpt.map(FooVo::toString).orElse(null);
    }
}
```

##### 5.4.5.3 服务使用方本地测试

本地测试有两种场景需要注意yaml配置：  
1. 本地启动两个服务，需要真实调用另一个服务接口  

```yaml
elite-forge-framework:
  http-exchange:
    clients:
      # client的name
      mock-service-one:
        # 配置url后，不会基于name调用
        url: http://localhost:8080
```

2. 本地启动服务，远程接口调用走mock  

开启全局mock，或只开启某个客户端的mock，然后指定mockUrl。  
```yaml
elite-forge-framework:
  http-exchange:
    enabl-mock: true
```

```yaml
elite-forge-framework:
  http-exchange:
    clients:
      # 目标client
      mock-service-one:
        enable-mock: true
        # 配置mockUrl
        mockUrl: https://torna.cisdigital.cn/mock/app-cisdigital-cap-cache-center-dashboard
```

##### 5.4.5.4 辅助类CallServerWrapper

`CallServerWrapper` 是一个用于封装远程服务调用的工具类，提供统一的异常处理、结果校验、取数逻辑、打印结果数据。  
此包装类，调用失败时会抛出自定义异常 `HttpExchangeException` 。 

| 方法名              | 简要说明                               | 返回值        |
| ------------------- | -------------------------------------- | ------------- |
| `getWithoutData`    | 仅校验远程调用是否成功，不关心返回数据 | 无            |
| `checkObjectResult` | 校验返回对象结果是否成功               | 无            |
| `checkVoidResult`   | 校验无返回值接口是否成功               | 无            |
| `getData`           | 获取返回数据，允许为空                 | `Optional<T>` |
| `getNonNullData`    | 获取非空返回数据，data 为空直接失败    | `T`           |

案例：  
```java
import cn.cisdigital.elite.forge.infra.httpexchange.support.CallServerWrapper;

import java.util.Optional;

// 调用无返回值的服务
CallServerWrapper.getWithoutData(() -> userService.updateUser(user));

// 获取非空数据，若数据为空直接抛异常
User user = CallServerWrapper.getNonNullData(() -> userService.getUserById(1L));

// 获取有可能为空的数据，若数据为空，不会抛出异常
Optional<User> userOpt = CallServerWrapper.getData(() -> userService.findUserByName("tom"));
```


#### 5.4.5 扩展starter

暂不支持扩展。

### 5.5 Mybatis-Plus

> cisdigital-elite-forge-infra-mybatis-plus-spring-boot3-starter

#### 5.5.1 核心特性
为应用提供统一的，ORM层交互能力。  

##### 5.5.1.1 支持数据逻辑隔离

通过扩展Mybatis-Plus的插件机制，支持给SQL WERE条件自动添加隔离字段，默认字段名为 `tenant_id`。

##### 5.5.1.2 支持审计字段自动填充

支持从上下文 `ContextStore` 中获取用户信息。  
Insert时，自动填充Entity实体类的以下字段：  
- id：自动生成TSID
- createBy: 上下文中的userId
- createTime: 当前UTC时间
- updateBy: 上下文中的userId
- updateTime: 当前UTC时间
- tenantId: 上下文中的tenantId
- archived: 赋值false
- version: 赋值0
- updateName: 上下文中的username
- createName: 上下文中的username

Update时，自动填充Entity实体类的以下字段：  
- updateBy: 上下文中的userId
- updateTime: 当前UTC时间
- updateName: 上下文中的username

##### 5.5.1.3 通用枚举处理

Entity类支持直接使用枚举类，枚举类需要实现 `cn.cisdigital.elite.forge.infra.commons.interfaces.enums.BizEnum
`。  
框架与数据库交互时，会自动将枚举序列化为int类型的code字段，进行存储。  

##### 5.5.1.4 提供多种优化后的插件

内置插件列表：

- TenantLineInnerInterceptor（数据隔离）
- PaginationInnerInterceptor（分页）
- BlockAttackInnerInterceptor（防全表更新/删除）
- CustomOptimisticLockInterceptor（乐观锁）
- CustomFieldInterceptor + DmFieldCaseConverter（达梦字段大小写转换）

插件优化逻辑说明：
- 数据插件：
  - 租户标识为空时不拼接条件；
  - _i18n 表和 ignore-tables 中的表自动跳过；
  - 插入语句已带 tenant_id 时不重复追加。
- 乐观锁插件：
  - 只有实体存在 version 字段或实现 Versionable 时才生效，避免无版本字段时报错。
- 达梦字段大小写转换：
  - 开启时，会将双引号标识符中的字段名，自动转换为大写后，再执行SQL。

##### 5.5.1.5 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `MybatisInterceptorCustomizer` | `cn.cisdigital.elite.forge.infra.mp.interceptor.MybatisInterceptorCustomizer` | 无 | `customize(MybatisPlusInterceptor)` |
| `CustomTenantFieldHandler` | `cn.cisdigital.elite.forge.infra.mp.handler.CustomTenantFieldHandler` | `properties`、`resourceIsolationTagProvider` | `getTenantId()`、`getTenantIdColumn()`、`ignoreInsert(...)`、`ignoreTable(...)` |
| `ResourceIsolationTagProvider` | `cn.cisdigital.elite.forge.infra.support.provider.isolation.ResourceIsolationTagProvider` | 无 | `getIsolationTag()` |
| `MybatisPlusConfigProperties` | `cn.cisdigital.elite.forge.infra.mp.property.MybatisPlusConfigProperties` | `enablePage`、`enableOptimisticLocker`、`enableBlockAttack`、`tenantFieldHandler`、`enableDmFiledCaseConvert` | Lombok 自动生成的 `get/set` 方法 |

#### 5.5.2 引入starter

```xml
<dependency>
  <groupId>cn.cisdigital.elite.forge.infra</groupId>
  <artifactId>cisdigital-elite-forge-infra-mybatis-plus-spring-boot3-starter</artifactId>
</dependency>
```

#### 5.5.3 配置starter

引入starter后，可直接使用；如需调整插件行为可通过yaml进行配置。  
启动服务，发现以下日志，即说明 `mybatis plus starter` 已经生效：  

```
[自动装配] 注册租户插件: TenantLineInnerInterceptor
[自动装配] 注册分页插件: PaginationInnerInterceptor
[自动装配] 注册防全表删除和更新插件: BlockAttackInnerInterceptor
[自动装配] 注册乐观锁插件: CustomOptimisticLockInterceptor
[自动装配] 注册达梦大小写转换插件: CustomFieldInterceptor
```

##### 5.5.3.1 全量yaml

```yaml
elite-forge-framework:
  mybatis-plus:
    # 是否开启分页插件，默认true
    enable-page: true
    # 是否开启乐观锁插件，默认true
    enable-optimistic-locker: true
    # 是否开启防全表删除和更新插件，默认true
    enable-block-attack: true
    # 是否开启大梦大小写转换插件，默认false
    enable-dm-filed-case-convert: false
    # 租户字段处理器配置
    tenant-field-handler:
      # 启用开关，默认true
      enabled: true
      # 数据隔离字段名，默认 tenant_id
      tenant-id-column: tenant_id
      # 指定不需要数据隔离的表全名，默认为空
      # 注意：此处指定的表以及_i18n表，都不会在Where条件自动拼接数据隔离条件
      ignore-tables:
        - audit_log
```

#### 5.5.4 扩展starter

##### 5.5.4.1 自定义Mybatis-Plus Interceptor注册逻辑

可实现 `MybatisInterceptorCustomizer` 接口，达到新增或调整拦截器的目的:  

末尾新增拦截器：  
```java
import cn.cisdigital.elite.forge.infra.mp.interceptor.MybatisInterceptorCustomizer;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.stereotype.Component;

@Component
public class PaginationCustomizer implements MybatisInterceptorCustomizer {
    @Override
    public void customize(MybatisPlusInterceptor interceptor) {
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
    }
}
```

替换默认插件顺序，或者替换为自己的自定义插件：

```java
import cn.cisdigital.elite.forge.infra.mp.interceptor.MybatisInterceptorCustomizer;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.BlockAttackInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.stereotype.Component;

@Component
public class InterceptorOrderCustomizer implements MybatisInterceptorCustomizer {
    @Override
    public void customize(MybatisPlusInterceptor interceptor) {
        interceptor.getInterceptors().clear();
        interceptor.addInnerInterceptor(new BlockAttackInnerInterceptor());
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor());
    }
}
```

##### 5.5.4.2 自定义数据隔离标识

数据隔离插件中的 `CustomTenantFieldHandler` 使用的是 `ResourceIsolationTagProvider` 来获取隔离字段的数据值。  
可实现自己的 `ResourceIsolationTagProvider` 配合 `MybatisInterceptorCustomizer` 覆盖默认租户来源。
```java
import cn.cisdigital.elite.forge.infra.commons.context.ContextKeys;
import cn.cisdigital.elite.forge.infra.mp.handler.CustomTenantFieldHandler;
import cn.cisdigital.elite.forge.infra.mp.interceptor.MybatisInterceptorCustomizer;
import cn.cisdigital.elite.forge.infra.mp.property.MybatisPlusConfigProperties;
import cn.cisdigital.elite.forge.infra.support.provider.isolation.ResourceIsolationTagComposers;
import cn.cisdigital.elite.forge.infra.support.provider.isolation.ResourceIsolationTagProvider;
import cn.cisdigital.elite.forge.infra.support.provider.isolation.ResourceIsolationTagProviders;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.TenantLineInnerInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;

@Bean
public ResourceIsolationTagProvider customTenantIdProvider() {
    return ResourceIsolationTagProviders.builder()
            .appendContext(ContextKeys.APP_ID)
            .appendContext(ContextKeys.TENANT_ID)
            .composer(ResourceIsolationTagComposers.minusJoining())
            .build();
}

@Component
@RequiredArgsConstructor
public class CustomCustomizer implements MybatisInterceptorCustomizer {

    @Qualifier("customTenantIdProvider")
    private final ResourceIsolationTagProvider customTenantIdProvider;
    private final MybatisPlusConfigProperties properties;

    @Override
    public void customize(MybatisPlusInterceptor interceptor) {
        interceptor.getInterceptors().clear();
        interceptor.addInnerInterceptor(
          new TenantLineInnerInterceptor(
            new CustomTenantFieldHandler(properties, customTenantIdProvider)
          )
        );
        // ...省略其他拦截器的注册
    }
}
```

其他的扩展点与 `Mybatis-Plus` 官方扩展点一致。  

### 5.6 加解密

> cisdigital-elite-forge-infra-crypto-spring-boot3-starter

#### 5.6.1 核心特性

为应用提供统一的，标准化的加解密能力，屏蔽底层算法差异，降低接入和使用成本。  

##### 5.6.1.1 统一加解密接口入口

通过统一的接口规范对外提供加解密能力，避免应用直接对接多种加解密 API，减少耦合与重复实现。  

不同算法原生调用方式差异：  
```java
import org.apache.commons.codec.binary.Hex;

import javax.crypto.Cipher;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

// MD5（摘要算法）
MessageDigest md5 = MessageDigest.getInstance("MD5");
byte[] md5Bytes = md5.digest(data.getBytes(StandardCharsets.UTF_8));
String md5Hex = Hex.encodeHexString(md5Bytes);

// AES（对称加密）
Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivParameterSpec);
byte[] aesEncrypted = cipher.doFinal(data.getBytes(StandardCharsets.UTF_8));
```

统一封装后的使用方式:  
```java
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoConfig;
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoService;

// 伪码：通过统一接口调用
String ciphertext = cryptoService.encrypt(cryptoConfig, "text");
String plainText = cryptoService.decrypt(cryptoConfig, ciphertext);
```

##### 5.6.1.2 内置常用加解密算法实现
内置多种常见的对称加密、非对称加密、编解码、摘要、脱敏等算法，特别是SM国密算法，支持开箱即用。  

目前已实现：
- 对称加密
  - AES
  - SM4
- 非对称加密
  - SM2
- 编解码
  - Base64
- 摘要
  - MD5
  - SHA1
  - SHA256
  - SHA512
  - SM3
  - Hmac
    - HmacMd5
    - HmacSHA1
    - HmacSHA256
    - HmacSHA512
    - HmacSM3
- 脱敏
  - 掩码

##### 5.6.1.3 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `CryptoService` | `cn.cisdigital.elite.forge.infra.crypto.abs.CryptoService` | 无 | `encrypt(...)`、`decrypt(...)`、`check(...)`、`support()` |
| `CryptoProvider` | `cn.cisdigital.elite.forge.infra.crypto.abs.CryptoProvider` | `cryptoServiceMap` | `getCryptoServiceCount()`、`getCryptoServiceOf(...)` |
| `CryptoConfig` | `cn.cisdigital.elite.forge.infra.crypto.abs.CryptoConfig` | 无 | `getCryptoType()`、`getKey()`、`getIv()`、`getMode()`、`getPadding()`、`getRandomSalt()` |
| `Md5CryptoConfig` | `cn.cisdigital.elite.forge.infra.crypto.algorithm.digest.md5.Md5CryptoConfig` | `randomSalt`、`salt`、`saltSize` | `getCryptoType()`，以及 Lombok 自动生成的 `get/set` 方法 |

#### 5.6.2 引入starter

```xml
<dependency>
  <groupId>cn.cisdigital.elite.forge.infra</groupId>
  <artifactId>cisdigital-elite-forge-infra-crypto-spring-boot3-starter</artifactId>
</dependency>
```

#### 5.6.3 配置starter

无需任何yaml配置，但是需要配置一下额外的序列化、反序列化。  

新增bean：  
```java
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoConfig;
import cn.cisdigital.elite.forge.infra.crypto.config.CryptoConfigDeserializer;
import cn.cisdigital.elite.forge.infra.crypto.config.CryptoConfigSerializer;
import cn.cisdigital.elite.forge.infra.web.mvc.serializer.ObjectMapperPostProcessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.springframework.stereotype.Component;

@Component
public class CryptoJacksonPostProcessor implements ObjectMapperPostProcessor {

    @Override
    public void postConfig(ObjectMapper objectMapper) {
        SimpleModule module = new SimpleModule("elite-forge-crypto");
        module.addSerializer(CryptoConfig.class, new CryptoConfigSerializer());
        module.addDeserializer(CryptoConfig.class, new CryptoConfigDeserializer());
        objectMapper.registerModule(module);
    }
}
```

#### 5.6.4 使用starter

CryptoService加密接口说明：  

| 方法签名                                                                         | 功能说明                           | 返回值   |
| -------------------------------------------------------------------------------- | ---------------------------------- | -------- |
| `String encrypt(CryptoConfig cryptoConfig, InputStream originInputStream)`       | 加密输入流数据                     | `String` |
| `String encrypt(CryptoConfig cryptoConfig, String text)`                         | 加密原文字符串                     | `String` |
| `String encrypt(CryptoConfig cryptoConfig, byte[] text)`                         | 加密原文字节数组                   | `String` |
| `byte[] encryptToBytes(CryptoConfig cryptoConfig, String text)`                  | 加密原文字符串为字节数组           | `byte[]` |
| `byte[] encryptToBytes(CryptoConfig cryptoConfig, byte[] text)`                  | 加密原文字节数组为字节数组         | `byte[]` |
| `void encryptSteam(CryptoConfig cryptoConfig, InputStream in, OutputStream out)` | 流式加密（输入原文流，输出密文流） | 无       |
| `String encryptWithoutValid(CryptoConfig cryptoConfig, String text)`             | 加密原文（跳过参数合法性校验）     | `String` |

CryptoService解密接口说明：  

| 方法签名                                                                         | 功能说明                           | 返回值           |
| -------------------------------------------------------------------------------- | ---------------------------------- | ---------------- |
| `boolean check(CryptoConfig cryptoConfig, String text, String ciphertext)`       | 校验原文加密后是否与指定密文一致   | `boolean`        |
| `String decrypt(CryptoConfig cryptoConfig, String ciphertext)`                   | 解密密文字符串                     | `String`         |
| `String decrypt(CryptoConfig cryptoConfig, byte[] ciphertext)`                   | 解密密文字节数组                   | `String`         |
| `byte[] decryptToBytes(CryptoConfig cryptoConfig, String ciphertext)`            | 解密密文字符串为字节数组           | `byte[]`         |
| `byte[] decryptToBytes(CryptoConfig cryptoConfig, byte[] ciphertext)`            | 解密密文字节数组为字节数组         | `byte[]`         |
| `void decryptSteam(CryptoConfig cryptoConfig, InputStream in, OutputStream out)` | 流式解密（输入密文流，输出原文流） | 无               |
| `String decryptWithoutValid(CryptoConfig cryptoConfig, String ciphertext)`       | 解密密文（跳过参数合法性校验）     | `String`         |
| `CryptoTypeEnum support()`                                                       | 返回当前实现支持的加密算法类型     | `CryptoTypeEnum` |


示例代码：  
```java
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoConfig;
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoProvider;
import cn.cisdigital.elite.forge.infra.crypto.abs.CryptoService;
import cn.cisdigital.elite.forge.infra.crypto.algorithm.digest.md5.Md5CryptoConfig;
import cn.cisdigital.elite.forge.infra.crypto.model.enums.CryptoTypeEnum;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class CryptoDemoService {

    private final CryptoProvider cryptoProvider;

    public String encryptByMd5(String plainText) {
        CryptoService md5Service = cryptoProvider.getCryptoServiceOf(CryptoTypeEnum.MD5);
        CryptoConfig config = new Md5CryptoConfig()
                .setRandomSalt(false)
                .setSalt("123");
        return md5Service.encrypt(config, plainText);
    }
}
```

#### 5.6.5 扩展starter

暂不支持扩展，有其他算法需求请提需求申请，我们也在持续实现其他算法。  

### 5.7 缓存抽象层

> cisdigital-elite-forge-infra-cache-spring-boot3-starter

#### 5.7.1 核心特性
为应用提供统一、标准化的缓存能力，屏蔽底层实现差异，降低使用和接入成本。 

##### 5.7.1.1 支持从资源池中指定数据源

支持 `var.yml` 与 `custom.yml` 的资源池配置。    
通过应用ID、资源池ID、资源ID来定位和加载实用的数据源。

##### 5.7.1.2 统一缓存接口入口

定义统一的 CacheService接口，框架将业务逻辑与特定缓存技术的解耦。

开发者只需与标准接口交互，无需关心底层实现，极大降低了代码的复杂性和重复性，并使得更换缓存技术对业务代码几乎无感。

##### 5.7.1.3 支持资源隔离

**逻辑层面**：通过租户感知的缓存键（例如自动添加租户前缀）确保数据隔离。

**物理层面**：通过资源池化技术，根据请求上下文中的隔离标识分配独立的RedissonClient。

>注意，完整的物理与逻辑隔离能力目前仅由Redisson实现提供。

##### 5.7.1.4 支持自定义缓存实现扩展

框架具备良好的扩展性，如需集成新的缓存实现，开发者只需实现`CacheService`接口，并完成其内部方法，然后将该实现注册为Spring Bean即可。

框架本身的默认实现（如`Redisson`、`Caffeine`）也遵循此方式接入，从而保证架构的开放性和灵活性。

##### 5.7.1.5 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `CacheService` | `cn.cisdigital.elite.forge.infra.cache.abs.service.CacheService` | 无 | `name()`、`get(...)`、`getLong(...)`、`getObject(...)`、`delete(...)`、`exists(...)`、`expire(...)`、`increment(...)`、`decrement(...)` |
| `CacheServiceManager` | `cn.cisdigital.elite.forge.infra.cache.abs.service.CacheServiceManager` | `environment`、`cacheServiceMap`、`defaultCacheService`、`properties` | `getService()`、`getService(String)`、`setEnvironment(...)` |
| `CaffeineCacheServiceImpl` | `cn.cisdigital.elite.forge.infra.cache.caffeine.service.CaffeineCacheServiceImpl` | `name`、`cache` | `name()`、`get(...)`、`delete(...)`、`exists(...)`、`increment(...)`、`decrement(...)` |

#### 5.7.2 引入starter

```xml
<dependencies>
    <dependency>
        <groupId>cn.cisdigital.elite.forge.infra</groupId>
        <artifactId>cisdigital-elite-forge-infra-cache-spring-boot3-starter</artifactId>
    </dependency>
</dependencies>
```

#### 5.7.3 配置starter

>注意：默认启用了`redisson`，redis中间件的环境信息需要在`var.yml`中的资源池进行配置，并在`custom.yml`中使用配置的资源。

##### 5.7.3.1 资源池相关配置

**`<spring.application.name>-var.yml`配置redisson连接信息**

```yaml
cisdigital:
  # 租户资源配置
  tenancy:
  # 默认的资源隔离标签，这里用的100000
    default-tenant-id: 100000
    # 资源池
    resource:
      # 资源隔离标签
      100000:
        # redis类型的资源
        redis:
          # 资源id
          rds:
            redisson:
              # 这里的config yml配置跟redisson官方的一致
              config: |
                singleServerConfig:
                  idleConnectionTimeout: 10000
                  connectTimeout: 10000
                  timeout: 10000
                  retryAttempts: 4
                  retryDelay: !<org.redisson.config.EqualJitterDelay> {baseDelay: PT1S, maxDelay: PT2S}
                  reconnectionDelay: !<org.redisson.config.EqualJitterDelay> {baseDelay: PT0.1S, maxDelay: PT10S}
                  password: xxxxxxxxxxxxxxx
                  subscriptionsPerConnection: 5
                  clientName: cache-center
                  address: "redis://xxx.xxx.xxx.xx:6379"
                  subscriptionConnectionMinimumIdleSize: 1
                  subscriptionConnectionPoolSize: 1
                  connectionMinimumIdleSize: 2
                  connectionPoolSize: 2
                  database: 0
                threads: 2
                nettyThreads: 4
                transportMode: "NIO"
```

**`config/custom.yml`配置使用对应资源**

```yaml
cisdigital:
  app:
    # 默认的appId
    default-app-id: ${spring.application.name}
    # 配置app中租户对应的资源id
    config:
      # appId
      当前应用名（spring.application.name）:
        tenancy:
          # 资源隔离标签
          100000:
            # redis对应的资源id
            redis: rds
```

##### 5.7.3.2 最小yaml配置

```yaml
elite-forge-framework:
  cache:
    # 默认缓存实现caffeine或redisson
    default-cache-service-name: caffeine
``` 

##### 5.7.3.3 全量yaml配置

```yaml
cisdigital:
  tenancy:
    #是否启用逻辑隔离，默认开启
    enableNamespace: true
elite-forge-framework:
  cache:
    # 是否开启缓存，默认开启
    enabled: true
    # 默认缓存实现caffeine或redisson
    default-cache-service-name: caffeine
    # redisson缓存配置
    redisson:
      # 缓存实现名，默认redisson
      name: redisson
      # 是否开启，默认开启
      enabled: true
      # 是否启用spring boot的缓存管理器 默认false
      enableSpringCacheManager: false
      # 缓存空间过期配置
      keyExpireTimeMap:
        # 缓存空间名称
        myCache:
          #生存时间
          ttl: 30m
          #最大空闲时间
          maxIdleTime: 30m
    # caffeine本地缓存配置
    caffeine:
      # 缓存实现名，默认caffeine
      name: caffeine
      # 是否开启，默认开启
      enabled: true
      # 最大条目数量，默认值1000
      maximumSize: 1000
      # 初始容量，默认值100
      initialCapacity: 100
      # 更新操作是否刷新失效时间 默认关闭
      operationRefresh: false
      # 访问是否刷新失效时间 默认关闭
      accessRefresh: false
      # 过期时间 默认三十分钟
      defaultExpire: 1800
      # 时间单位 默认秒
      timeUnit: SECONDS
```

#### 5.7.4 使用starter

启动服务，发现以下日志，即说明cache starter已经生效：  
```
[ 自动装配 ] 加载缓存服务
注册缓存服务实现: {caffeine} -> {cn.cisdigital.elite.forge.infra.cache.caffeine.service.CaffeineCacheServiceImpl}
注册缓存服务实现: {redisson} -> {cn.cisdigital.elite.forge.infra.cache.redisson.service.RedissonCacheServiceImpl}
默认缓存服务实现: {caffeine} -> {cn.cisdigital.elite.forge.infra.cache.caffeine.service.CaffeineCacheServiceImpl}
```

注入`CacheServiceManager`，获取缓存实现操作缓存

```java
import cn.cisdigital.elite.forge.infra.cache.abs.service.CacheService;
import cn.cisdigital.elite.forge.infra.cache.abs.service.CacheServiceManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class CustomizerService{
  private final CacheServiceManager cacheServiceManager;

  /**
   * 从缓存服务管理器中获取默认缓存实现类<br>
   * <p>getService()方法不传参数是返回配置的默认缓存实现</p>
   */
  public String getString(String key){
    CacheService cacheService = cacheServiceManager.getService();
    return cacheService.get(key);
  }

  /**
   * 通过名称获取对应的缓存实现类
   */
  public Long getLong(String key){
    CacheService cacheService = cacheServiceManager.getService("caffeine");
    return cacheService.getLong(key);
  }
  
  /**
   * 通过属性表达式获取对应的缓存实现类<br/>
   * <p>内部逻辑会从Environment中获取属性对应配置的名称</p>
   */
  public Boolean delete(String key){
    String propertiesKey = "customizer.conf.cache-service-name";
    CacheService cacheService = cacheServiceManager.getService(propertiesKey);
    return cacheService.delete(key);
  }
}
```

#### 5.7.5 扩展starter

| 扩展点         | 说明                                                                                            |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `CacheService` | 自定义缓存类实现此接口，并注册为bean，即可通过`CacheServiceManager`缓存管理器获取提供服务能力。 |

##### 示例：自定义缓存实现

```java
import cn.cisdigital.elite.forge.infra.cache.abs.service.CacheService;
import org.springframework.stereotype.Component;

@Component
public class CustomizerCacheService implements CacheService {

    @Override
    public String name() {
      //返回缓存服务实现名
      return "customizer";
    }

    //按需重写CacheService中的方法，未重写的方法调用都会报错：UnsupportedException
}
```

### 5.8 多数据源

> cisdigital-elite-forge-infra-dynamic-datasource-spring-boot3-starter

#### 5.8.1 核心特性
为应用提供统一的，多数据源能力。  

##### 5.8.1.1 支持从资源池中指定主数据源

支持 `var.yml` 与 `custom.yml` 的资源池配置。    
通过应用ID、资源池ID、资源ID来定位和加载实用的数据源。

##### 5.8.1.2 支持从资源池中指定扩展数据源

提供 `@DS("资源ID")` 注解， 在方法/类级别加载和切换到扩展数据源。  

##### 5.8.1.3 支持配置数据源连接池参数

支持 `hikari` 原生参数绑定。可以根据业务情况调整数据库连接池。  

##### 5.8.1.4 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `DS` | `cn.cisdigital.elite.forge.infra.datasource.DS` | 注解属性：`value` | `value()` |
| `MultiDataSource` | `cn.cisdigital.elite.forge.infra.datasource.MultiDataSource` | `holder`、`resources`、`extResources`、`resourceProperties` | `addExtDataSource(...)`、`doInitialize(...)`、`getConnection(...)`、`getResources()` |
| `ExtDataSourceRoutingAdvice` | `cn.cisdigital.elite.forge.infra.datasource.ExtDataSourceRoutingAdvice` | 无 | `invoke(MethodInvocation)` |

#### 5.8.2 引入starter

```xml
<dependencies>
  <dependency>
    <groupId>cn.cisdigital.elite.forge.infra</groupId>
    <artifactId>cisdigital-elite-forge-infra-dynamic-datasource-spring-boot3-starter</artifactId>
  </dependency>
</dependencies>
```

#### 5.8.3 配置starter

需要同时配置 `custom.yml` 中的应用配置 `cisdigital.app` 与 `var.yml` 中的资源池配置 `cisdigital.tenancy`。  

在资源池 `var.yml` 中，定义当前环境会使用到的数据库:  

```yaml
cisdigital:
  tenancy:
    default-tenant-id: demo-tenant
    resource:
      demo-tenant:
        datasource:
          pg:
            url: jdbc:postgresql://127.0.0.1:5432/demo
            driver-class-name: org.postgresql.Driver
            username: postgres
            password: demo
            # 可以自定义连接池参数，目前都使用hikari
            hikari:
              maximum-pool-size: 10
          mysql:
            url: jdbc:mysql://127.0.0.1:3306/demo
            driver-class-name: com.mysql.cj.jdbc.Driver
            username: root
            password: demo
```

在应用配置 `custom.yml` 中，指定当前应用使用到的数据库：  

```yaml
cisdigital:
  app:
    default-app-id: demo-app
    config:
      demo-app:
        tenancy:
          "100000":
            # [必须指定] 主数据源标识
            datasource: pg
            # [可选] 扩展数据源标识，多个用英文逗号分隔
            ext-datasource: mysql
```

启动服务后，不报错，说明已经加载成功。  

#### 5.8.4 使用starter

#### 5.8.4.1 服务只用到了主数据源

一般的简单服务，只需要连接自己的数据库即可。  
正常的CRUD类和方法，都会使用主数据源的 `DataSource` 类。  

#### 5.8.4.2 服务用到了多个数据源

某些业务场景下，一个服务需要同时连接多个数据源。  
正常的CRUD类和方法，依然使用主数据源的 `DataSource` 类。  
需要切换数据源时，请在类/方法上，使用 `@DS("资源ID")` 注解。  

```java
import cn.cisdigital.elite.forge.infra.datasource.DS;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.sql.SQLException;

@Service
@RequiredArgsConstructor
public class DemoService {

    private final DemoRepository repo;

    public Object mainDatasource() throws SQLException {
        return repo.queryxxx();
    }

    @DS("mysql")
    public Object extDatasource() throws SQLException {
        return repo.queryxxx();
    }
}

@Service
@DS("mysql")
@RequiredArgsConstructor
public class DemoExtService {

    private final DemoRepository repo;

    public Object extDatasource() throws SQLException {
        return repo.queryxxx();
    }

    public Object bothExtDatasource() throws SQLException {
        return repo.queryxxx();
    }
}

```

> Tips:  
> `@DS` 指定的资源未配置时会抛出 `DATASOURCE_NOT_FOUND` 相关的异常。

#### 5.8.5 扩展starter

暂不支持扩展。


### 5.9 代码生成器

> cisdigital-elite-forge-infra-code-generator

#### 5.9.1 核心特性

为应用提供统一的，生成ORM层代码的能力。  

##### 5.9.1.1 基于数据库信息逆向生成Java代码

依托数据库表的名称、字段、描述等基础信息，代码生成器可自动逆向生成 Java 层的 Controller、Service、Repository、Mapper、POJO 代码，  
有效省去人工手动创建这些代码的工作量，大幅提升开发效率。

##### 5.9.1.2 提供CODE和HUMAN两种模式

**CODE（全代码模式）**  
在代码中预先配置全部参数，直接执行生成器，一次性完成全部代码生成。  

**HUMAN（人机交互模式）**  
在代码中仅配置必要的基础参数（如数据库连接信息），执行生成器后，其余参数在运行过程中由用户交互式输入，最终完成代码生成。  

##### 5.9.1.3 支持数据库枚举字段自动生成Java枚举类

如需依据数据库枚举值字段生成 Java 枚举类，数据库字段的 Comment 需遵循以下编写规范：

```
[枚举]{'valid':'有效(1)','invalid':'无效(0)'}
```
说明：
- `[枚举]` 为代码识别标志位，系统将据此判定是否生成 Java 枚举类
- 枚举的成员变量名，使用键值对的key
- 枚举的成员变量对应的code，会使用键值对value中，括号里的数字
- 枚举的成员变量对应的messageKey，会使用键值对value中的中文描述

生成的枚举类示例：  

```java
import cn.cisdigital.elite.forge.infra.commons.interfaces.enums.BizEnum;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum FieldEnum implements BizEnum {
    VALID(1, "有效"),
    INVALID(0, "无效");

    private final int code;
    private final String messageKey;

    /**
    * 根据编码获取枚举
    */
    public static FieldEnum getByCode(int code) {
        for (FieldEnum value : values()) {
            if (value.getCode() == code) {
                return value;
            }
        }
        throw new IllegalArgumentException("未知的枚举编码: " + code);
    }

    @Override
    public String toString() {
        return String.format("%s(%d): %s", this.name(), this.code, this.messageKey);
    }
}
```

> Tips:  
> 此处生成后，需要开发完善国际化properties文件后，将枚举的messageKey替换为国际化的key。

##### 5.9.1.4 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `GeneratorProperty` | `cn.cisdigital.elite.forge.infra.code.generator.common.coder.GeneratorProperty` | `mode`、`dataSourceBuilder`、`tableMatchMode`、`company`、`product`、`service`、`version` | `buildPackagePrefix(...)`、`buildPackageModelPrefix(...)`、`buildProjectName()`、`buildServiceName()` |
| `CodeGenerator` | `cn.cisdigital.elite.forge.infra.code.generator.CodeGenerator` | 无 | `generate(GeneratorProperty)` |
| `InteractiveMode` | `cn.cisdigital.elite.forge.infra.code.generator.common.coder.InteractiveMode` | `code`、`messageKey` | `getCode()`、`getMessageKey()` |
| `TableMatchMode` | `cn.cisdigital.elite.forge.infra.code.generator.common.coder.TableMatchMode` | `code`、`messageKey` | `getCode()`、`getMessageKey()` |


#### 5.9.2 引入starter

```xml
<dependencies>
    <dependency>
        <groupId>cn.cisdigital.elite.forge.infra</groupId>
        <artifactId>cisdigital-elite-forge-infra-code-generator</artifactId>
    </dependency>
</dependencies>
```

#### 5.9.3 配置starter

GeneratorProperty配置类说明：  
| 属性名                | 类型                     | 描述                                                                                                                                                | 约束 / 默认值                                        |
| --------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| mode                  | InteractiveMode          | 使用代码生成器交互方式。支持CODE全代码模式和HUMAN人机交互模式                                                                                       | 必须项，默认值：InteractiveMode.CODE                 |
| dataSourceBuilder     | DataSourceConfig.Builder | 数据源配置Builder                                                                                                                                   | 必须项                                               |
| tableMatchMode        | TableMatchMode           | 定位数据库表的匹配模式，支持：通过表前缀选择（TableMatchMode.TABLE_PREFIX）、指定表全名选择（TableMatchMode.FULL_NAME）、全部表（TableMatchMode.ALL | 必须项。默认使用全名匹配                             |
| company               | String                   | 公司命名                                                                                                                                            | 必须项                                               |
| product               | String                   | 产品命名                                                                                                                                            | 必须项                                               |
| service               | String                   | 服务命名                                                                                                                                            | 必须项                                               |
| version               | String                   | 版本号，javadoc的@since标签会用到                                                                                                                   | 必须项                                               |
| matchPrefixSelectList | `Set<String>`            | 指定定位数据库表的前缀列表                                                                                                                          | tableMatchMode为表前缀时，为必须项；其他情况非必须。 |
| overwriteFiles        | Boolean                  | 生成文件时是否覆盖已有的文件                                                                                                                        | 可选项，默认值：false                                |
| disableConfig         | DisableConfig            | 禁用配置                                                                                                                                            | 可选项，默认禁用Controller生成                       |
| businessDomain        | String                   | 业务领域名，如果配置了该项，则mvc层都创建在biz模块下的对应java包内，否则mvc层是平铺的                                                               | 可选项，默认值：null                                 |
| entitySuperClass      | `Class<?>`               | Entity实体类的父类，不配置会根据表的字段，自动选择统一框架的Entity父类                                                                              | 可选项，默认值：null                                 |
| isMultiModuleProject  | Boolean                  | 是否是多模块项目                                                                                                                                    | 可选项，默认值：true                                 |
| skipBusinessDomain    | Boolean                  | 跳过业务域配置                                                                                                                                      | 可选项，默认值：false                                |
| removeTablePrefixList | `Set<String>`            | 生成的类名会去掉配置的前缀                                                                                                                          | 可选项，默认与matchPrefixSelectList一致              |
| tables                | `List<String>`           | 需要生成的表全名（当使用表前缀匹配时不需要指定表名称）                                                                                              | 可选项，默认值：null                                 |
| codePath              | String                   | 代码生成根路径，默认使用当前命令执行的路径进行生成（指定路径需要使用绝对路径）                                                                      | 可选项，默认值：null                                 |


#### 5.9.4 使用starter

使用生成器，都需要写代码进行一些配置。  
需要先在工程的 **boot** 启动模块下新增RunCodeGenerator.java类。  

> 使用 [CISDigital 项目生成器](/elite-forge/generator/) 时，该类为工程默认自带类，无需手动创建。  

然后启动**RunCodeGenerator.java**类的main()方法，即可自动生成 Controller、Service、Repository、Mapper、Entity、Enum 等核心代码文件。  

##### 5.9.4.1 HUMAN模式，生成代码

参考代码：  
```java
import cn.cisdigital.elite.forge.infra.code.generator.CodeGenerator;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.GeneratorProperty;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.InteractiveMode;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.TableMatchMode;
import cn.cisdigital.elite.forge.infra.code.generator.common.util.DriverClassConstants;
import com.baomidou.mybatisplus.generator.config.DataSourceConfig;

import java.util.Set;

public class RunCodeGenerator {

    public static void main(String[] args) {
        GeneratorProperty property = new GeneratorProperty();
        // 覆盖文件
        property.setOverwriteFiles(true);
        // 定位数据库表的匹配模式，这里是前缀匹配
        property.setTableMatchMode(TableMatchMode.TABLE_PREFIX);
        // 定位数据库表的前缀列表，这里匹配job_前缀
        property.setMatchPrefixSelectList(Set.of("job_"));
        // 设置当前业务模块名为job，生成的代码都会在job java包下
        property.setBusinessDomain("job");
        // 业务库地址，支持MYSQL、PG、ORACLE、OCEANBASE、DM数据库
        DataSourceConfig.Builder dataSourceBuilder = new DataSourceConfig.Builder(
                "jdbc:mysql://xxx:port/数据库",
                "用户名",
                "密码");
        dataSourceBuilder.driverClassName(DriverClassConstants.MYSQL_DRIVER);
        property.setDataSourceBuilder(dataSourceBuilder);
        // 人机交互模式
        property.setMode(InteractiveMode.HUMAN);
        // 执行代码生成
        CodeGenerator.generate(property);
    }
}
```

代码交互提示补全信息如下：
```
// kebab-case风格
> 请输入公司名称:

// kebab-case风格
> 请输入产品命名:

// kebab-case风格
> 请输入服务命名:

// 会将该版本号放在javadoc中的@since中
> 请输入版本号:

// 会生成biz maven模块下，对应名字的java package
> 请输入领域模块名，可以为空

```

全部交互完毕后，自动开始生成代码。  

##### 5.9.4.2 CODE模式，生成代码

参考代码：  
```java
import cn.cisdigital.elite.forge.infra.code.generator.CodeGenerator;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.GeneratorProperty;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.InteractiveMode;
import cn.cisdigital.elite.forge.infra.code.generator.common.coder.TableMatchMode;
import cn.cisdigital.elite.forge.infra.code.generator.common.util.DriverClassConstants;
import com.baomidou.mybatisplus.generator.config.DataSourceConfig;

import java.util.Set;

public class RunCodeGenerator {

    public static void main(String[] args) {
        GeneratorProperty property = new GeneratorProperty();
        // 覆盖文件
        property.setOverwriteFiles(true);
        // 定位数据库表的匹配模式，这里是前缀匹配
        property.setTableMatchMode(TableMatchMode.TABLE_PREFIX);
        // 定位数据库表的前缀列表，这里匹配job_前缀
        property.setMatchPrefixSelectList(Set.of("job_"));
        // 设置当前业务模块名为job，生成的代码都会在job java包下
        property.setBusinessDomain("job");
        // 业务库地址，支持MYSQL、PG、ORACLE、OCEANBASE、DM数据库
        DataSourceConfig.Builder dataSourceBuilder = new DataSourceConfig.Builder(
                "jdbc:mysql://xxx:port/数据库",
                "用户名",
                "密码");
        dataSourceBuilder.driverClassName(DriverClassConstants.MYSQL_DRIVER);
        property.setDataSourceBuilder(dataSourceBuilder);
        // 公司名，对应注册信息
        property.setCompany("xxx-company");
        // 产品名
        property.setProduct("yyy-product");
        // 服务名
        property.setService("zzz-service");
        // 纯代码模式
        property.setMode(InteractiveMode.CODE);
        // 执行代码生成
        CodeGenerator.generate(property);
    }
}
```

运行后，不会有任何交互，直接开始生成代码。

##### 5.9.4.3 生成内容说明

skipBusinessDomain为true时，代码全部平铺：  

```
├── xxx-biz
│   ├── controller
│   │   ├── api
│   │   ├── innerapi
│   │   ├── openapi
│   ├── service
│   ├── repository
│   │   ├── mapper
├── xxx-model
│   ├── entity
│   ├── enums
```

skipBusinessDomain为false时，businessDomain配置为"job"时，代码会放到job java包下：  

```
├── xxx-biz
│   ├── job
│   │   ├── controller
│   │   │   ├── api
│   │   │   ├── innerapi
│   │   │   ├── openapi
│   │   ├── service
│   │   ├── repository
│   │   │   ├── mapper
├── xxx-model
│   │   ├── job
│   │   │   ├── entity
│   │   │   ├── enums
```

#### 5.9.5 扩展starter

暂不支持扩展  

### 5.10 资源抽象层

> cisdigital-elite-forge-infra-resource-spring-boot3-starter  

#### 5.10.1 核心特性

资源抽象层用于为应用提供统一、协议无关的资源访问与存储能力，屏蔽底层厂商的底层技术细节。     

##### 5.10.1.1 基于 URI 协议的统一资源访问模型

本框架基于 `Spring Resource` 抽象层进行扩展，统一以 `URI` 作为资源唯一标识：  
```
scheme://authority/path[?query][#fragment]
```
如：  
```
s3://bucket-name/path/to/object.txt
file:///data/files/report.pdf
classpath:/config/application.yml
```

框架通过 `cn.cisdigital.elite.forge.infra.resource.ResourceUtils` 作为获取Resource的统一入口。然后上传、下载、预览等操作，全部由统一的Resource接口提供。  

业务代码只依赖 URI 协议与 Resource 接口能力，无需感知底层存储类型，以一致的方式进行上传、下载、删除、判断存在等操作，从而实现：
- 类型零耦合：不再关心S3Client、MinioClient等具体实现类
- 异常零耦合：底层 SDK 的异常体系，不会扩散到业务层
- 配置零耦合：各oss的配置，不再散落在yaml各处

##### 5.10.1.2 提供对象存储协议

本starter提供对 `s3://` 协议的 Resource 实现，支持兼容s3协议的对象存储中间件：
- minio
- 华为obs

并提供了大文件相关的优化与支持：
- 支持流式读取
- 支持流式写入
- 支持文件分片
- 支持流式对文件加解密

##### 5.10.1.3 支持基于资源池的隔离

`S3 Resource` 支持基于资源池配置，在运行时，加载不同对象存储实例供业务使用。

##### 5.10.1.4 核心接口类说明（全包名）

| 接口/类 | 全包名 | 核心成员变量 | 核心方法名 |
| --- | --- | --- | --- |
| `ResourceUtils` | `cn.cisdigital.elite.forge.infra.resource.ResourceUtils` | 无 | `getResourceFrom(...)`、`getResourceFromDefaultLoader(...)`、`addPrefixIfNot(...)`、`readableFileSize(...)`、`upload(...)` |
| `CisdiAbstractResource` | `cn.cisdigital.elite.forge.infra.resource.CisdiAbstractResource` | `resourceLocation`、`selfInputStream`、`relatedResources` | `upload()`、`download()`、`delete(...)`、`listChildren(...)`、`createMultipartUpload()`、`uploadPart(...)` |
| `ResourceMetadata` | `cn.cisdigital.elite.forge.infra.resource.ResourceMetadata` | `size`、`sizeWithUnit`、`name`、`lastModified`、`path`、`isFolder`、`mimeType` | Lombok 自动生成的 `get/set` 方法 |
| `ResourceStream` | `cn.cisdigital.elite.forge.infra.resource.ResourceStream` | `inputStream`、`outputStream` | `close()` |

#### 5.10.2 引入 starter

```xml
<dependencies>
    <dependency>
        <groupId>cn.cisdigital.elite.forge.infra</groupId>
        <artifactId>cisdigital-elite-forge-infra-resource-spring-boot3-starter</artifactId>
    </dependency>
</dependencies>
```

#### 5.10.3 配置starter

##### 5.10.3.1 资源池相关配置

**`<spring.application.name>-var.yml`配置s3连接信息**

```yaml
cisdigital:
  # 租户资源配置
  tenancy:
  # 默认隔离标签为100000
    default-tenant-id: 100000
    # 资源池
    resource:
      # 隔离标签
      100000:
        # s3类型的资源
        s3:
          s3-cluster-1:
            # [全部必改] S3基本配置
            endpoint: 你的地址，https://xxx或http://xxx
            access-key: 你的key
            secret-key: 你的secret
            bucket: 你是用的桶
            region: 区域，如cn-south-1
            # [非必要不修改，可以不配置] S3服务端高级配置
            server-options:
              # 避免域名不匹配引起的重定向签名问题，默认 true
              enablePathStyleAccess: false
              # 是否开启分块编码上传能力，默认 false
              enableChunkedEncoding: false
              # 是否启用 Transfer Acceleration 加速域名，默认 false
              enableAccelerateMode: false
              # 是否启用 SDK 对响应体的校验和验证，默认 true
              enableChecksumValidation: true
              # 是否在使用 ARN 访问点时使用 ARN 中的区域，默认 null, 表示遵循 SDK 默认行为
              enableUseArnRegion: ~
              #  服务端是否支持缩略图，默认false，表示由上层自行处理
              supportThumbnail: false
            # [非必要不修改，可以不配置] S3 SDK 分片上传相关阈值配置
            multipart-options:
              # 分片上传时允许的最小分片大小（字节），默认 8 MiB，低于该值时 SDK 会改用单请求上传
              minimumPartSizeInBytes: 8388608
              # 当对象大小达到该阈值（字节）时触发分片上传流程，默认 64 MiB
              thresholdInBytes: 67108864
              # 上传请求预分配的缓冲区大小（字节），用来减少频繁的内存申请，默认为 null 表示沿用 SDK 默认值
              apiCallBufferSizeInBytes: ~
```

**`config/custom.yml`配置使用对应资源**

```yaml
cisdigital:
  app:
    # 默认的appId
    default-app-id: ${spring.application.name}
    # 配置app中租户对应的资源id
    config:
      # appId
      当前应用名（spring.application.name）:
        tenancy:
          # 资源隔离标签
          100000:
            # 指定使用资源池中的哪个s3
            s3: s3-cluster-1
```

##### 5.10.3.2 最小yaml配置
在 `config/custom.yml` 中配置资源 starter 相关参数：

```yaml
elite-forge-framework:
  resource:
    s3:
      # 开启分块上传功能
      enableMultipart: false
```

启动服务后，日志中应出现以下关键字，表示资源加载器已生效：

```
[ 自动装配 ] 加载对象存储服务
[ 自动装配 ] 注册资源解析器：s3://
```

##### 5.10.3.3 全量yaml配置
在 `config/custom.yml` 中配置资源 starter 相关参数：

```yaml
elite-forge-framework:
  resource:
    s3:
      # 是否启用s3协议，默认true
      enabled: true
      # 允许的最大文件大小, 单位MB, 默认值1024Mb
      maxFileSize: 1024
      # 允许的最大批量上传文件个数, 默认值: 10
      maxBitchUploadNumber: 10
      # 是否开启分片上传，默认false
      enableMultipart: false
```

#### 5.10.4 使用starter


##### 5.10.4.1 资源的基本操作 

资源的URI信息，需要业务系统自行存储，然后通过此starter操作资源。  
```java
import cn.cisdigital.elite.forge.infra.resource.CisdiAbstractResource;
import cn.cisdigital.elite.forge.infra.resource.ResourceUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

@Service
@RequiredArgsConstructor
public class MyService {

    private final ResourceLoader resourceLoader;

    /**
     * 通过文件File上传
     */
    public void uploadFile(File file) throws IOException {
        String location = "s3://my-bucket/my-folder/my-file.txt";
        // 使用工具类得到资源对象
        CisdiAbstractResource resource = ResourceUtils.getResourceFrom(resourceLoader, location);

        // 上传文件三选一：文件/输入流/字节流
        resource.setSelfInputStream(new FileInputStream(file));
        // 已自动关流
        resource.upload();
    }

    /**
     * 通过输入流上传
     */
    public void uploadInputStream(FileInputStream fileInputStream) throws IOException {
        String location = "s3://my-bucket/my-folder/my-file.txt";
        CisdiAbstractResource resource = ResourceUtils.getResourceFrom(resourceLoader, location);

        resource.setSelfInputStream(fileInputStream);
        // 已自动关流
        resource.upload();
    }

    /**
     * 通过字节流上传
     */
    public void uploadBytes(byte[] bytes) throws IOException {
        String location = "s3://my-bucket/my-folder/my-file.txt";
        CisdiAbstractResource resource = ResourceUtils.getResourceFrom(resourceLoader, location);

        resource.setSelfInputStream(new java.io.ByteArrayInputStream(bytes));
        // 已自动关流
        resource.upload();
    }

    /**
     * 其他操作
     */
    public void otherOperations() {
        String location = "s3://my-bucket/my-folder/my-file.txt";
        CisdiAbstractResource resource = ResourceUtils.getResourceFrom(resourceLoader, location);

        // 资源是否存在
        resource.exists();
        // 流式下载
        resource.download();
        // 删除资源
        resource.delete(false);
    }
}
```

##### 5.10.4.2 Resource接口说明

**基础资源访问**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| exists() | boolean | 判断资源是否存在 | 异常情况下返回 false |
| getURI() | URI | 获取资源 URI | 资源唯一标识 |
| getURL() | URL | 获取资源 URL | 基于 URI 转换 |
| isFile() | boolean | 判断当前资源是否为文件 | 非文件系统语义 |
| getFilename() | String | 获取资源文件名 | 目录返回空字符串 |
| getSuffix() | String | 获取资源后缀名 | 基于文件名解析 |
| getDescription() | String | 获取资源描述信息 | 当前实现返回空字符串 |

**读取与下载能力**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| getInputStream() | InputStream | 获取资源输入流 | 委托给内部输入流 |
| download() | ResourceStream | 通过流方式下载资源 | 调用方负责关闭流 |
| readContent(skipLineNums, limit) | `List<String>` | 按行读取资源内容 | 适用于简单文本 |

**写入与上传能力**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| upload() | boolean | 上传资源内容 | 依赖 selfInputStream |
| writeContent(newContent) | boolean | 写入字符串内容并上传 | 覆盖原有内容 |
| getSelfInputStream() | InputStream | 获取内部维护的输入流 | 为空时返回空流 |

**分片上传（大文件）**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| createMultipartUpload() | String | 创建分片上传任务 | 返回 uploadId |
| uploadPart(uploadId, partNumber, inputStream, size) | CompletedPart | 上传单个分片（流方式） | 大文件上传 |
| uploadPart(uploadId, partNumber, partData) | CompletedPart | 上传单个分片（字节数组） | 支持断点续传 |
| completeMultipartUpload(uploadId, completedParts) | CompleteMultipartUploadResponse | 合并已上传分片 | completedParts 必须完整 |
| abortMultipartUpload(uploadId) | AbortMultipartUploadResponse | 终止分片上传 | 会清理已上传分片 |
| listMultipartUploadsOnProgress() | ListMultipartUploadsResponse | 查询进行中的分片上传任务 | 部分 S3 实现不可靠 |
| listPartsByUploadId(key, uploadId) | ListPartsResponse | 查询指定上传任务的分片信息 | key 与 uploadId 必须匹配 |

**目录与资源管理**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| mkdir() | boolean | 创建资源路径 | 目录语义 |
| listChildren(maxKeys, recursive) | `List<CisdiAbstractResource>` | 列出子资源 | 仅对目录有效 |
| delete(recursive) | boolean | 删除资源 | recursive=true 递归删除 |
| copyObject(targetKey, targetBucket) | boolean | 复制当前资源 | 是否跨桶由实现决定 |


**元数据与关联资源**  

| 方法 | 返回类型 | 说明 | 备注 |
|------|----------|------|------|
| getMetadata() | `Optional<ResourceMetadata>` | 获取资源元数据 | 由具体实现决定 |
| setRelatedResources(relatedResources) | void | 设置关联资源集合 | scheme 必须一致 |
| close() | void | 关闭资源及关联资源 | 会级联关闭 |


#### 5.10.5 扩展starter

暂不支持扩展。  
