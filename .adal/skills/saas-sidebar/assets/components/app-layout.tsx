'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { AppSidebar } from './app-sidebar'
import { useAuth } from '@/contexts/AuthContext'

// =============================================================================
// CONSTANTS
// =============================================================================

const SIDEBAR_KEY = 'sidebar_state'

// =============================================================================
// LOADING SKELETON (matches sidebar width for zero layout shift)
// =============================================================================

function AuthLoadingSkeleton() {
  return (
    <div className="flex min-h-screen">
      <div className="w-64 shrink-0 border-r bg-sidebar p-3 space-y-4">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-muted animate-pulse" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3 w-28 rounded bg-muted animate-pulse" />
            <div className="h-2 w-16 rounded bg-muted animate-pulse" />
          </div>
        </div>
        <div className="space-y-1 pt-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-8 rounded-md bg-muted/50 animate-pulse" />
          ))}
        </div>
      </div>
      <div className="flex-1 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
      </div>
    </div>
  )
}

// =============================================================================
// APP LAYOUT
// =============================================================================

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const wasAuthedRef = useRef(false)
  if (user) wasAuthedRef.current = true

  // Redirect to sign-in if not authenticated
  useEffect(() => {
    if (!authLoading && !user && !wasAuthedRef.current) {
      router.replace(`/sign-in?redirect=${encodeURIComponent(pathname)}`)
    }
  }, [user, authLoading, router, pathname])

  // Sidebar state with localStorage persistence
  const [open, setOpen] = useState(() => {
    if (typeof window === 'undefined') return true
    const stored = localStorage.getItem(SIDEBAR_KEY)
    return stored === null ? true : stored === 'true'
  })

  const handleOpenChange = (value: boolean) => {
    setOpen(value)
    localStorage.setItem(SIDEBAR_KEY, String(value))
  }

  if (authLoading || !user) return <AuthLoadingSkeleton />

  return (
    <SidebarProvider open={open} onOpenChange={handleOpenChange}>
      <AppSidebar />
      <SidebarInset className="overflow-y-auto h-dvh">
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}
