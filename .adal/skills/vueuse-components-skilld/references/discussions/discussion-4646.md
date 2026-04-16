---
number: 4646
title: Can `useFetch` be used to read stream data.
category: Q&A
created: 2025-03-05
url: "https://github.com/vueuse/vueuse/discussions/4646"
upvotes: 1
comments: 1
answered: false
---

# Can `useFetch` be used to read stream data.

Can `useFetch` be used to read stream data. 

How to use it.

---

## Top Comments

**@dosubot** (+1):


Hey @ngd-b! I'm here to help you with any questions or issues you have. Let's tackle this together!


`useFetch` in vueuse does not natively support streaming responses. However, you can manually process the response stream by using the `afterFetch` option. This allows you to define a custom function to handle the response data after the fetch request is completed.

Here's an example of how you might use `afterFetch` to manually process a response stream:

```javascript
import { useFetch } from '@vueuse/core'

const { data, execute } = useFetch('https://api.example.com/data', {
  afterFetch(ctx) {
    // Manually process the response stream
    const processedData = processResponseStream(ctx.response)
    return { data: processedData }
  }
})

function processResponseStream(response) {
  // Custom logic to process the response stream
  // For example, parsing JSON or handling text data
  return response.json() // or any other processing logic
}

...