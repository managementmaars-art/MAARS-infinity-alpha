---
number: 4336
title: "How to useTransition to animate  props in obj, such as:  let obj=ref({age:10,count:0});"
category: Q&A
created: 2024-11-11
url: "https://github.com/vueuse/vueuse/discussions/4336"
upvotes: 1
comments: 1
answered: true
---

# How to useTransition to animate  props in obj, such as:  let obj=ref({age:10,count:0});

I tried some code like that at blew:

const obj = ref({a:10,b:0,c:0})
const aTransition = useTransition(ref(obj.value.a), { duration: 500 })
 
watch(
  () => obj.value.a,
  (newVal) => { aTransition.value = newVal }
)
 
const transitionedValues = computed(() => ({
  a: aTransition
}))

const addProp=()=>{
 obj.value.a += 100
  obj.value.b += 255
  obj.value.c += 140

}

  <text>{{transitionedValues.a}},{{obj.a}}</text>
 <button @click="addProp">addProp</button>

But, can not work.

---

## Accepted Answer

It doesn't work. A better approach is to avoid using  an map data structure.