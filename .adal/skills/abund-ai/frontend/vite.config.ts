import { defineConfig, loadEnv, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

/**
 * Custom plugin to inject analytics scripts in production builds only.
 * Reads from environment variables so IDs never need to be committed to the repo.
 * Set VITE_GA_MEASUREMENT_ID and VITE_CLARITY_PROJECT_ID in .env.production.local
 */
function analyticsPlugin(env: Record<string, string>): Plugin {
  return {
    name: 'inject-analytics',
    transformIndexHtml(html, ctx) {
      // Only inject in production builds
      if (ctx.server) return html

      const gaId = env.VITE_GA_MEASUREMENT_ID
      const clarityId = env.VITE_CLARITY_PROJECT_ID

      let scripts = ''

      if (gaId) {
        scripts += `
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=${gaId}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${gaId}');
  </script>`
      }

      if (clarityId) {
        scripts += `
  <!-- Microsoft Clarity -->
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "${clarityId}");
  </script>`
      }

      if (scripts) {
        // Inject before closing </head>
        return html.replace('</head>', `${scripts}\n</head>`)
      }

      return html
    },
  }
}

export default defineConfig(({ mode }) => {
  // Load env file based on mode (e.g., .env.production.local for production builds)
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react(), tailwindcss(), analyticsPlugin(env)],
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      strictPort: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8787',
          changeOrigin: true,
        },
      },
    },
    build: {
      target: 'esnext',
      minify: 'esbuild',
      sourcemap: true,
      rollupOptions: {
        output: {
          manualChunks: {
            // React core
            'vendor-react': ['react', 'react-dom', 'react-router-dom'],
            // Markdown rendering (heavy)
            'vendor-markdown': ['marked', 'highlight.js', 'dompurify'],
            // Animation
            'vendor-motion': ['motion'],
            // i18n
            'vendor-i18n': ['i18next', 'react-i18next'],
            // Date utilities
            'vendor-date': ['date-fns'],
          },
        },
      },
    },
  }
})
