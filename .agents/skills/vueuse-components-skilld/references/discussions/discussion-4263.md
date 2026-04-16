---
number: 4263
title: Mock different responses with vueuse/integrations/useAxios composable
category: Q&A
created: 2024-09-30
url: "https://github.com/vueuse/vueuse/discussions/4263"
upvotes: 1
comments: 1
answered: false
---

# Mock different responses with vueuse/integrations/useAxios composable

I'm using vuejs with vitest in order to test my application. I have a simple useAxios call and I need to create some unit tests that covers all the possible branches.

In particolar, I have this code:
`
const res = await useAxios(`url`, { method: 'GET', }, http)
const temp= 'key' in res.data.value ? X() : Y()`
 `   
Is there a way to mock multiple responses in different tests?

With the following code, it works but I can define just one response for all the tests, while I need different responses.
searching on google, it's not recommended to use multiple vi.mock(), so I tried to use vi.mocked() or useAxios: vi.fn(), but with no luck.

Does someone know how to solve it?

` vi.mock('@vueuse/integrations/useAxios', () => {
      return {
        useAxios() {
          return ...

---

## Top Comments

**@dosubot** (+1):


Hey @agaudino-altec! How's it going? I'm here to help you with any bugs or questions you have. Let's work together to solve the issue you're facing.


To mock multiple responses in different tests using the `vueuse/integrations/useAxios` composable in a Vue.js application with Vitest, you can use the `vi.mock` function from Vitest to mock the Axios instance. Here is an example of how you can achieve this:

...