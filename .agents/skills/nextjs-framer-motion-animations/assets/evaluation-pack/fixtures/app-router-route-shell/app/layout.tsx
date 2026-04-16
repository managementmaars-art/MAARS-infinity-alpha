import type { ReactNode } from "react"

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-zinc-950 text-white">
          <header className="border-b border-white/10 px-6 py-4">Dashboard</header>
          <main className="px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  )
}
