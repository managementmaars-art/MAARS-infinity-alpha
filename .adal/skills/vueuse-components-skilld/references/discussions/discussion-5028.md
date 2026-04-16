---
number: 5028
title: BUG | `useTimeoutFn` | 组件卸载后不会清除
category: Q&A
created: 2025-09-10
url: "https://github.com/vueuse/vueuse/discussions/5028"
upvotes: 1
comments: 1
answered: false
---

# BUG | `useTimeoutFn` | 组件卸载后不会清除

### Describe the bug

组件卸载后不会清除 `setTimeout` ，虽然里面调用了 `tryOnScopeDispose(stop)`，但是组件卸载后依旧存在。

可以打开控制查看日志信息，隐藏后依旧会继续输出日志。

<img width="1902" height="895" alt="Image" src="https://github.com/user-attachments/assets/cbb1aa30-a345-44d0-88d4-d17108f6cbd1" />

### Reproduction

https://playground.vueuse.org/#eNqFU81u00AQfpVlL3HUYJfAqXKilqpIIASolJsvxpk4bte71v6ESJbPcEFwA3FEPAUH3oYCb8Hsbuw4UpIeLHnn+2bm+2Zna3pWVeHSAD2hscpkUWmiQJuKsJTnk4RqldBpwouyElKTmuiiBKXTshoRo+B5qvT5Apkwc+crRM9yQRoyl6Ikg1OsjOEoExIGXZVzUVZrQhjZgxWwgWuiFilj4t0lzLtKnpHwTHClScEro8mkRwy0NDBMeBx5F6gZDxrKiqUa8ERI/NZoLTg5zViR3aC3tso994M+f394f/vx++3XX39+/Pz37fPfL5/iyCf5Ak748n4xb5MTSiKE4qjXiI5waChzXuThtRIcJ1vb7IRmmF4wkC8rXaCNhJ4Qh1jM+XjmYtbJqI1nC8hudsSv1crGEvpKggK5hIR2mE5lDqjNwhevX8AK/zuwFDPDkH0AvAQlmLEaPe2x4TOU3eM5tU/ddRU8v1IXKw1ctaasUMts...

---

## Top Comments

**@OrbisK** [maintainer]:

I think the problem is that you cant use a composable like this. The `useTimeoutFn(()=>useTimeoutFn(...), 1000)` call does not execute the inner useTimeoutFn on the setup level. So it is not disposed