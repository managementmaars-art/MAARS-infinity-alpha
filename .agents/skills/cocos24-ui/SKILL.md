---
name: cocos24-ui
description: 根据 UI 截图生成 Cocos Creator 2.4.x 的 UI 控制类和 Model 类代码
---

# Cocos Creator 2.4.x 最佳实践

## 目录结构

```
cocos/
├── SKILL.md          # 技能说明文档
├── LoadAsset.ts      # [可复用] 资源引用管理器组件
├── LoadSprite.ts     # [可复用] 动态图片加载组件
├── ModelValue.ts     # [可复用] 可监听数值类型
├── UIManager.ts      # [可复用] UI 弹窗管理器
├── UIState.ts        # [可复用] UI 状态管理
├── UIExample.ts      # [示例] UI 控制类
└── UIModelExample.ts # [示例] UI Model 类
```

**说明**：
- `[可复用]` - 最佳实践代码，可直接复制到项目中使用
- `[示例]` - 参考规范，新建 UI 时按此结构编写

## 适用场景

用户提供 UI 截图，生成对应的 TypeScript 代码（UI 控制类 + Model 类）。

**执行流程**：
1. 检查项目中是否存在可复用组件，没有则先复制到项目
2. 分析 UI 截图结构，识别元素类型（Label、Button、Sprite 等）
3. 按照 UI 控制类规范生成代码

---

## 可复用组件

生成 UI 代码前，检查以下组件是否存在于项目中，不存在则复制：

| 文件 | 说明 |
|------|------|
| `LoadAsset.ts` | 资源引用管理器，统一管理动态加载资源的引用计数，防止内存泄漏 |
| `LoadSprite.ts` | 动态图片加载组件，配合 LoadAsset 使用 |
| `ModelValue.ts` | 可监听数值类型，解决网络延迟下的即时反馈与数据一致性问题 |
| `UIManager.ts` | UI 弹窗管理器，单例模式管理弹窗生命周期 |
| `UIState.ts` | UI 状态管理，配合 UIManager 使用 |

---

## UI 开发规范

每个 UI 需要配套一个 Model 类，定义该 UI 所需的所有数据。UI 控制类通过 `setData(model)` 接收数据。

### UI Model 类规范

使用 TypeScript class 定义数据模型，包含 UI 需要展示的所有字段：

```typescript
/** UI 数据模型示例 */
export class UIModel {
    /** 唯一标识 */
    id: number;
    /** 标题文本 */
    title: string = '';
    /** 是否解锁 */
    isUnlock: boolean = false;
    /** 可监听的数值类型 */
    value: ModelValue;
    /** 最大值 */
    maxValue: number = 100;
    /** 嵌套子模型 */
    items: SubModel[] = [];
}
```

**要点**：
- 类名以 `Model` 结尾
- 属性带类型注解和默认值
- 可嵌套其他 Model 类或数组
- 需要监听变化的数值使用 `ModelValue` 类型

示例: `UIModelExample.ts`

---

### UI 控制类规范

创建新的 UI 控制类时，遵循以下结构：

#### 1. 声明引用的组件

使用 `@property` 装饰器声明所有需要在编辑器中绑定的组件引用：

```typescript
@property(cc.Label)
label_name: cc.Label = null;

@property(cc.Node)
node_name: cc.Node = null;

@property(I18nLabel)  // 自定义组件
custom_component: CustomComponent = null;
```

#### 2. setData 方法

统一使用 `setData(data)` 作为 UI 初始化入口：

```typescript
data: DataModel = null;

setData(data: DataModel) {
    this.data = data;
    this.initListen();        // 初始化事件监听
    this.updateUI();          // 更新 UI 显示
}
```

#### 3. click 统一处理点击事件

在节点上绑定 click 事件，通过 `currentTarget.name` 分发处理：

```typescript
click(target: cc.Event.EventTouch) {
    switch (target.currentTarget.name) {
        case 'btn_name_1':
            // 处理按钮1点击
            break;
        case 'btn_name_2':
            // 处理按钮2点击
            break;
        default:
            break;
    }
}
```

#### 4. 事件监听管理

配对使用 `initListen()` 和 `onDestroy()` 管理事件订阅，防止内存泄漏：

```typescript
isListening: boolean = false;

initListen() {
    if (this.isListening) return;
    this.isListening = true;
    this.data.property.on('valueChanged', this.onValueChanged, this);
}

onDestroy() {
    if (!this.isListening) return;
    this.isListening = false;
    this.data.property.off('valueChanged', this.onValueChanged, this);
}
```

示例: `UIExample.ts`