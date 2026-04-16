# Go Backend Review FAQ

## Q: 为什么不推荐全局依赖和具体结构体？理论上 mock 一个方法也可以？

不是"完全不能 mock"，而是 **Go 原生不支持对具体类型/函数打桩**，只能靠 unsafe 库绕过去，这在生产项目中是不可接受的。

### 全局函数调用难 mock

```go
// ❌ 函数内部直接调用包级函数
func (s *Service) DoSomething() {
    rc := config.GetRuntimeConfig()  // 包级函数调用
    maxCount := rc.GetMaxMemorySpaceCount()
}
```

`config.GetRuntimeConfig()` 是包级函数，Go 中无法在测试时替换它（除非用 `gomonkey` 这类基于 unsafe 的 hack 库）。测试时被迫依赖真实的 config 初始化，或搞全局变量替换，既脆弱又不安全。

注入后：

```go
// ✅ 通过接口字段调用
func (s *Service) DoSomething() {
    maxCount := s.runtimeConfigProvider.GetMaxMemorySpaceCount()
}
```

测试时直接传一个 mock 实现即可，零 hack。

### 具体结构体难 mock

```go
// ❌ 接受具体结构体指针
func NewService(repo *UserRepository) *Service
```

`*UserRepository` 是具体类型，测试时**只能传 `UserRepository` 的真实实例**。Go 不支持给 struct 的方法打桩（不像 Java 的 Mockito 可以 spy 具体类）。所以你必须：

- 连接真实数据库，或
- 用 `gomonkey` 做方法级 patch（依赖平台、不稳定）

```go
// ✅ 接受接口
func NewService(repo UserRepository) *Service
```

`UserRepository` 如果是接口，可以直接写 mock：

```go
type mockRepo struct{}
func (m *mockRepo) FindByID(id int) (*User, error) {
    return &User{Name: "test"}, nil
}

// 测试中直接注入
svc := NewService(&mockRepo{})
```

### 对比总结

| 方式 | 能否 mock | 手段 | 代价 |
|---|---|---|---|
| 包级函数 `config.GetXxx()` | 勉强能 | `gomonkey` / 全局变量替换 | unsafe、平台相关、CI 不稳定 |
| 具体结构体 `*UserRepository` | 勉强能 | `gomonkey` patch 方法 | 同上 |
| 接口注入 | 原生支持 | 写一个 mock struct | 零成本、类型安全 |

**结论：接口注入是 Go 惯用的、零代价的解法。**
