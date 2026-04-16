---
number: 4958
title: `useElementAttrs` | v-bind for elements outside the vue app
type: other
state: open
created: 2025-08-13
url: "https://github.com/vueuse/vueuse/issues/4958"
reactions: 1
comments: 6
---

# `useElementAttrs` | v-bind for elements outside the vue app

### Clear and concise description of the problem

Hi  
I use Vue with Inertia, so the root template is rendered in PHP.
Here is the template:
```html
<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}"> 
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title inertia>{{ config('app.name', 'Laravel') }}</title>

        @routes
        @vite(['resources/js/app.ts', "resources/js/pages/{$page['component']}.vue"])
        @inertiaHead
    </head>
    <body class="font-sans antialiased">
        @inertia
    </body>
</html>
```

...