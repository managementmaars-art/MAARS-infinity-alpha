---
name: fsm
description: Cocos Creator 有限状态机 (FSM) 实现，用于管理游戏对象的状态转换
---

# fsm

Cocos Creator 有限状态机 (FSM) 框架，用于简化游戏对象的状态管理。

## When to use

- 游戏角色状态管理 (例如: 待机、移动、攻击、受伤、死亡)
- UI 状态切换 (例如: 菜单、设置、结算界面)
- 任何需要状态转换逻辑的模块

## Instructions

### 1. 定义状态接口

状态类需要实现 `State` 接口:

```typescript
class 你的状态类 implements State<你的上下文类> {
    context: 你的上下文类
    
    onEnter(): void {
        // 进入状态时的逻辑
    }
    
    onUpdate(dt: number): void {
        // 每帧更新的逻辑
    }
    
    onExit(): void {
        // 退出状态时的逻辑
    }
}
```

### 2. 创建状态上下文

```typescript
export interface Context {
    state: State<Context>
    // 其他属性...
}
```

### 3. 使用 changeState 切换状态

```typescript
// 切换到新状态
changeState(context, 新状态类)

// 切换并设置属性
changeState(context, 新状态类, (state) => {
    state.属性 = 值
})
```

### 4. 在组件中更新状态

```typescript
update(dt: number) {
    if (this.context.state) {
        this.context.state.onUpdate(dt)
    }
}
```

## API 参考

### State<T>

状态接口:

```typescript
export interface State<T> {
    context: T
    onEnter(): void
    onUpdate(dt: number): void
    onExit(): void
}
```

### changeState<T>

改变状态函数:

```typescript
export function changeState<T extends State<Context>>(
    context: Context, 
    cls: { new(): T }, 
    call?: (state: T) => void
)
```

- `context`: 状态上下文
- `cls`: 新的状态类
- `call`: 可选，设置新状态的属性

### Context

状态上下文接口:

```typescript
export interface Context {
    state: State<Context>
}
```

## 使用示例

```typescript
// 定义上下文
class Player {
    state: PlayerState
    hp: number = 100
}

// 定义状态基类
class PlayerState implements State<Player> {
    context: Player
    
    onEnter(): void {}
    onUpdate(dt: number): void {}
    onExit(): void {}
}

// 待机状态
class IdleState extends PlayerState {
    onEnter(): void {
        console.log("进入待机")
    }
}

// 移动状态
class MoveState extends PlayerState {
    onEnter(): void {
        console.log("开始移动")
    }
}

// 使用
let player = new Player()
changeState(player, IdleState)

function update(dt: number) {
    if (player.state) {
        player.state.onUpdate(dt)
    }
}
```