---
name: vue-nuxt
description: Vue 3 Composition API, Nuxt 4, Pinia, composables, SSR, Nuxt modules, TypeScript
---

# Vue 3 + Nuxt 4

Full-stack Vue development using the Composition API, Nuxt 4 for SSR/SSG, Pinia for state management, typed composables, and custom Nuxt modules.

## Nuxt 4 Project Structure

```
├── app/
│   ├── components/
│   │   ├── ui/               # Base UI components
│   │   └── feature/          # Feature-specific components
│   ├── composables/          # Auto-imported composables
│   ├── layouts/              # Page layouts
│   ├── middleware/           # Route middleware
│   ├── pages/                # File-based routing
│   ├── plugins/              # Nuxt plugins
│   └── stores/               # Pinia stores
├── server/
│   ├── api/                  # Nitro API routes
│   ├── middleware/           # Server middleware
│   └── utils/                # Server-only utilities
├── nuxt.config.ts
└── app.config.ts
```

## nuxt.config.ts

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  future: { compatibilityVersion: 4 },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxt/image',
    '@nuxtjs/color-mode',
    '@vueuse/nuxt',
    'nuxt-icon',
  ],

  runtimeConfig: {
    // Server-only (not exposed to client)
    databaseUrl: process.env.DATABASE_URL,
    jwtSecret: process.env.JWT_SECRET,
    // Public (exposed to both)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      appName: 'MyApp',
    },
  },

  typescript: {
    strict: true,
    typeCheck: true,
  },

  nitro: {
    preset: 'node-server',
    compressPublicAssets: true,
  },

  experimental: {
    payloadExtraction: true,
    renderJsonPayloads: true,
  },
})
```

## Composition API Components

```vue
<!-- app/components/feature/UserProfile.vue -->
<script setup lang="ts">
interface Props {
  userId: string
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  updated: [user: User]
  deleted: [id: string]
}>()

// Composable for data fetching (SSR-aware)
const { data: user, pending, error, refresh } = await useAsyncData(
  `user-${props.userId}`,
  () => $fetch<User>(`/api/users/${props.userId}`),
  { watch: [() => props.userId] }
)

// Form state
const form = reactive({
  name: '',
  email: '',
})

watchEffect(() => {
  if (user.value) {
    form.name = user.value.name
    form.email = user.value.email
  }
})

// Mutations
const { execute: updateUser, status } = useAsyncState(
  async () => {
    const updated = await $fetch<User>(`/api/users/${props.userId}`, {
      method: 'PUT',
      body: form,
    })
    emit('updated', updated)
    return updated
  },
  null,
  { immediate: false }
)

const isSubmitting = computed(() => status.value === 'loading')

// Composable from VueUse
const { copy, copied } = useClipboard({ source: user.value?.email })
</script>

<template>
  <div v-if="pending" class="animate-pulse">
    <USkeleton class="h-24 w-full" />
  </div>

  <UAlert v-else-if="error" color="red" :description="error.message" />

  <UCard v-else-if="user">
    <template #header>
      <div class="flex items-center gap-4">
        <NuxtImg
          :src="user.avatarUrl"
          :alt="user.name"
          width="64"
          height="64"
          class="rounded-full"
        />
        <div>
          <h2 class="text-xl font-semibold">{{ user.name }}</h2>
          <button @click="copy(user.email)" class="text-sm text-gray-500 hover:text-blue-500">
            {{ user.email }}
            <span v-if="copied" class="text-green-500 ml-1">Copied!</span>
          </button>
        </div>
      </div>
    </template>

    <form v-if="editable" @submit.prevent="updateUser">
      <UFormGroup label="Name" name="name">
        <UInput v-model="form.name" required />
      </UFormGroup>
      <UFormGroup label="Email" name="email" class="mt-4">
        <UInput v-model="form.email" type="email" required />
      </UFormGroup>
      <UButton type="submit" :loading="isSubmitting" class="mt-6">
        Save Changes
      </UButton>
    </form>
  </UCard>
</template>
```

## Pinia Store with Persistence

```typescript
// app/stores/auth.ts
import { defineStore } from 'pinia'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    isLoading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    displayName: (state) => state.user?.name ?? 'Guest',
  },

  actions: {
    async login(email: string, password: string) {
      this.isLoading = true
      try {
        const response = await $fetch<{ user: User; token: string }>('/api/auth/login', {
          method: 'POST',
          body: { email, password },
        })
        this.user = response.user
        this.token = response.token

        // Sync cookie for SSR
        const tokenCookie = useCookie('auth_token', {
          maxAge: 60 * 60 * 24 * 7, // 7 days
          secure: true,
          sameSite: 'strict',
        })
        tokenCookie.value = response.token

        navigateTo('/dashboard')
      } catch (error: any) {
        throw createError({ statusCode: 401, message: error.data?.message || 'Login failed' })
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      await $fetch('/api/auth/logout', { method: 'POST' }).catch(() => {})
      this.$reset()
      useCookie('auth_token').value = null
      navigateTo('/login')
    },

    async fetchCurrentUser() {
      if (!this.token) return
      this.user = await $fetch<User>('/api/auth/me')
    },
  },

  persist: {
    storage: piniaPluginPersistedstate.cookies({ sameSite: 'strict' }),
    pick: ['token'],
  },
})
```

## Typed Composables

```typescript
// app/composables/useInfiniteScroll.ts
export function useInfiniteScroll<T>(
  fetchFn: (page: number, pageSize: number) => Promise<{ data: T[]; total: number }>,
  options: { pageSize?: number } = {}
) {
  const { pageSize = 20 } = options

  const items = ref<T[]>([]) as Ref<T[]>
  const page = ref(1)
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  const hasMore = computed(() => items.value.length < total.value)

  async function loadMore() {
    if (isLoading.value || !hasMore.value) return
    isLoading.value = true
    error.value = null
    try {
      const result = await fetchFn(page.value, pageSize)
      items.value.push(...result.data)
      total.value = result.total
      page.value++
    } catch (e) {
      error.value = e instanceof Error ? e : new Error('Failed to load')
    } finally {
      isLoading.value = false
    }
  }

  async function reset() {
    items.value = []
    page.value = 1
    total.value = 0
    error.value = null
    await loadMore()
  }

  // Intersection observer for auto-loading
  const sentinel = ref<HTMLElement | null>(null)
  const { stop } = useIntersectionObserver(sentinel, ([entry]) => {
    if (entry.isIntersecting) loadMore()
  })

  onUnmounted(stop)

  return { items, isLoading, error, hasMore, loadMore, reset, sentinel }
}
```

## Nitro API Routes (Server)

```typescript
// server/api/users/[id].get.ts
import { z } from 'zod'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id) throw createError({ statusCode: 400, message: 'ID required' })

  // Auth check via server middleware
  const user = event.context.user
  if (!user) throw createError({ statusCode: 401, message: 'Unauthorized' })

  const db = useDatabase()
  const targetUser = await db.query.users.findFirst({
    where: eq(users.id, id),
    columns: { passwordHash: false },
  })

  if (!targetUser) throw createError({ statusCode: 404, message: 'User not found' })

  return targetUser
})

// server/api/users/index.post.ts
const CreateUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  role: z.enum(['user', 'admin']).default('user'),
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, CreateUserSchema.parse)
  const db = useDatabase()

  const existing = await db.query.users.findFirst({
    where: eq(users.email, body.email),
  })
  if (existing) throw createError({ statusCode: 409, message: 'Email already in use' })

  const [created] = await db.insert(users).values({
    id: crypto.randomUUID(),
    ...body,
    createdAt: new Date(),
  }).returning()

  setResponseStatus(event, 201)
  return created
})
```

## Route Middleware

```typescript
// app/middleware/auth.ts
export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  const token = useCookie('auth_token')

  if (!auth.isAuthenticated && token.value) {
    try {
      await auth.fetchCurrentUser()
    } catch {
      return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
    }
  }

  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (to.meta.role && !auth.user?.roles?.includes(to.meta.role as string)) {
    throw createError({ statusCode: 403, message: 'Forbidden' })
  }
})
```

## Best Practices

- Use `useAsyncData` / `useFetch` for SSR data — never `onMounted` + `fetch` (causes hydration mismatches)
- Prefix server-only environment variables with `NUXT_` to auto-load; public ones with `NUXT_PUBLIC_`
- Keep stores small; use composables for complex shared logic
- Use `definePageMeta({ middleware: 'auth', layout: 'dashboard' })` for page-level config
- Use `<NuxtImg>` instead of `<img>` for automatic optimization with `@nuxt/image`
- Validate server API inputs with `readValidatedBody(event, schema.parse)` using Zod
- Use `$fetch` in components (client-side) and `useAsyncData` for SSR-aware requests
- Use `useHead` / `useSeoMeta` for SEO — not raw `<head>` manipulation
- Enable `payloadExtraction` to avoid re-fetching data on client hydration
- Use Nuxt DevTools for performance profiling and component inspection

## Models to Use

- **Default**: `claude-sonnet-4-5` — Composition API, Pinia, SSR patterns
- **Architecture / module authoring**: `claude-opus-4-5` — custom Nuxt modules, complex SSR flows
- **Quick snippets**: `claude-haiku-3-5` — simple composables, utility functions, store actions
