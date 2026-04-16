'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home, Search, FolderOpen, Star, Users2,
  Settings, Clock, ChevronDown, ChevronRight,
  Check, PanelLeftOpen, Plus,
} from 'lucide-react'
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup,
  SidebarGroupLabel, SidebarHeader, SidebarMenu,
  SidebarMenuButton, SidebarMenuItem, SidebarMenuSub,
  SidebarMenuSubItem, SidebarMenuSubButton,
  SidebarRail, SidebarSeparator,
  useSidebar,
} from '@/components/ui/sidebar'
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible'

// =============================================================================
// WORKSPACE SWITCHER
// =============================================================================

/**
 * Shows current workspace with popover to switch.
 * NO Tooltip wrapper — Tooltip inside PopoverTrigger breaks click handling.
 * Avatar has group-hover/sidebar:hidden when collapsed → replaced by ExpandButton on hover.
 */
function WorkspaceSwitcher() {
  const { state } = useSidebar()
  const [open, setOpen] = useState(false)
  const collapsed = state === 'collapsed'

  // Replace with your own workspace/team data
  const workspace = { name: 'Acme Inc', plan: 'Pro' }
  const initial = workspace.name.charAt(0).toUpperCase()

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <SidebarMenuButton size="lg" className={cn("w-full cursor-pointer", collapsed && "justify-center")}>
          {/* Workspace avatar — hides on sidebar hover when collapsed (replaced by expand btn) */}
          <div className={cn(
            "flex items-center justify-center h-7 w-7 rounded-md bg-primary text-primary-foreground text-xs font-bold shrink-0",
            collapsed && "group-hover/sidebar:hidden"
          )}>
            {initial}
          </div>
          {!collapsed && (
            <>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-semibold truncate leading-tight">{workspace.name}</p>
                <p className="text-[10px] text-muted-foreground leading-tight">{workspace.plan} plan</p>
              </div>
              <ChevronDown className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            </>
          )}
        </SidebarMenuButton>
      </PopoverTrigger>
      <PopoverContent align="start" side={collapsed ? 'right' : 'bottom'} sideOffset={4} className="w-60 p-1">
        {/* Replace with your workspace list */}
        <button className="flex items-center gap-2 rounded-md px-2 py-1.5 text-left hover:bg-accent transition-colors w-full cursor-pointer text-sm">
          <div className="flex items-center justify-center h-6 w-6 rounded bg-primary/10 text-primary text-[10px] font-bold shrink-0">A</div>
          <span className="flex-1 truncate font-medium">Acme Inc</span>
          <Check className="h-3.5 w-3.5 shrink-0 text-primary" />
        </button>
        <SidebarSeparator className="my-1" />
        <Link href="/settings" onClick={() => setOpen(false)} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors cursor-pointer">
          <Settings className="h-3.5 w-3.5" /> Settings
        </Link>
        <button className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors cursor-pointer w-full">
          <Plus className="h-3.5 w-3.5" /> New workspace
        </button>
      </PopoverContent>
    </Popover>
  )
}

// =============================================================================
// NAV ITEM
// =============================================================================

/**
 * Navigation item using SidebarMenuButton with built-in tooltip.
 * Tooltip auto-shows only when collapsed + desktop — no manual wrapping needed.
 */
function NavItem({ href, label, icon: Icon, badge, onClick }: {
  href?: string; label: string; icon: React.ComponentType<{ className?: string }>
  badge?: string; onClick?: () => void
}) {
  const pathname = usePathname()
  const isActive = href ? pathname === href : false

  const content = (
    <>
      <Icon className="h-4 w-4" />
      <span>{label}</span>
      {badge && (
        <span className="ml-auto flex items-center gap-0.5 text-[10px] text-muted-foreground/50">
          <kbd className="inline-flex h-5 items-center rounded border border-border/50 bg-muted/50 px-1 font-mono text-[10px] font-medium">⌘</kbd>
          <kbd className="inline-flex h-5 items-center rounded border border-border/50 bg-muted/50 px-1 font-mono text-[10px] font-medium">{badge}</kbd>
        </span>
      )}
    </>
  )

  if (onClick) {
    return (
      <SidebarMenuItem>
        <SidebarMenuButton isActive={isActive} tooltip={label} onClick={onClick} className="cursor-pointer">
          {content}
        </SidebarMenuButton>
      </SidebarMenuItem>
    )
  }

  return (
    <SidebarMenuItem>
      <SidebarMenuButton asChild isActive={isActive} tooltip={label}>
        <Link href={href!}>{content}</Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  )
}

// =============================================================================
// COLLAPSIBLE SECTION (e.g. Recent Projects)
// =============================================================================

/**
 * Collapsible nav section with sub-items.
 * SidebarMenuSub auto-hides when collapsed via group-data-[collapsible=icon]:hidden.
 */
function RecentItems() {
  const [open, setOpen] = useState(true)

  // Replace with your own data fetching
  const items = [
    { id: '1', name: 'Project Alpha', href: '/project/alpha' },
    { id: '2', name: 'Project Beta', href: '/project/beta' },
    { id: '3', name: 'Project Gamma', href: '/project/gamma' },
  ]

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <SidebarMenuItem>
        <CollapsibleTrigger asChild>
          <SidebarMenuButton className="cursor-pointer" tooltip="Recent">
            <Clock className="h-4 w-4" />
            <span>Recent</span>
            <ChevronRight className={cn(
              "ml-auto h-3.5 w-3.5 shrink-0 text-muted-foreground/50 transition-transform duration-200",
              open && "rotate-90"
            )} />
          </SidebarMenuButton>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <SidebarMenuSub>
            {items.map((item) => (
              <SidebarMenuSubItem key={item.id}>
                <SidebarMenuSubButton asChild>
                  <Link href={item.href}>
                    <span className="truncate">{item.name}</span>
                  </Link>
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            ))}
            <SidebarMenuSubItem>
              <SidebarMenuSubButton asChild className="text-muted-foreground">
                <Link href="/projects">View all</Link>
              </SidebarMenuSubButton>
            </SidebarMenuSubItem>
          </SidebarMenuSub>
        </CollapsibleContent>
      </SidebarMenuItem>
    </Collapsible>
  )
}

// =============================================================================
// EXPAND BUTTON (shown on hover when collapsed)
// =============================================================================

/**
 * Hidden by default. Shows on sidebar hover when collapsed.
 * Replaces the workspace avatar (which has group-hover/sidebar:hidden).
 * Both are h-7 w-7 for zero layout shift on swap.
 */
function ExpandButton() {
  const { toggleSidebar, state } = useSidebar()
  if (state !== 'collapsed') return null

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          onClick={(e) => { e.stopPropagation(); toggleSidebar() }}
          className="hidden group-hover/sidebar:flex items-center justify-center h-7 w-7 rounded-md bg-accent text-foreground cursor-pointer hover:bg-accent/80 transition-colors shrink-0"
        >
          <PanelLeftOpen className="h-4 w-4" />
        </button>
      </TooltipTrigger>
      <TooltipContent side="right" align="center">Expand sidebar</TooltipContent>
    </Tooltip>
  )
}

// =============================================================================
// COLLAPSE TOGGLE (shown in header when expanded)
// =============================================================================

/**
 * Uses same PanelLeftOpen icon rotated 180° for visual consistency.
 * Subtle styling — muted color that intensifies on hover.
 */
function CollapseToggle() {
  const { toggleSidebar, state } = useSidebar()
  if (state !== 'expanded') return null

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          onClick={toggleSidebar}
          className="h-7 w-7 flex items-center justify-center rounded-md text-muted-foreground/50 hover:text-muted-foreground hover:bg-accent transition-colors cursor-pointer shrink-0"
        >
          <PanelLeftOpen className="h-4 w-4 rotate-180" />
        </button>
      </TooltipTrigger>
      <TooltipContent side="right">Close sidebar</TooltipContent>
    </Tooltip>
  )
}

// =============================================================================
// USER ROW (footer)
// =============================================================================

/**
 * Simple user row that links to settings.
 * Uses SidebarMenuButton tooltip for auto-tooltip when collapsed.
 */
function UserRow() {
  const { state } = useSidebar()
  const collapsed = state === 'collapsed'

  // Replace with your own user data
  const user = { name: 'John Doe', photo: null as string | null }
  const initial = user.name.charAt(0).toUpperCase()

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton asChild tooltip={user.name} className={cn(collapsed && "flex items-center justify-center")}>
          <Link href="/settings?tab=profile" className="flex items-center gap-2 cursor-pointer">
            <Avatar className="h-6 w-6 shrink-0">
              {user.photo && <AvatarImage src={user.photo} alt={user.name} />}
              <AvatarFallback className="text-[10px] bg-muted">{initial}</AvatarFallback>
            </Avatar>
            {!collapsed && (
              <>
                <span className="truncate text-sm font-medium">{user.name}</span>
                <Settings className="ml-auto h-3.5 w-3.5 shrink-0 text-muted-foreground/50 hover:text-muted-foreground transition-colors" />
              </>
            )}
          </Link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}

// =============================================================================
// MAIN SIDEBAR
// =============================================================================

/**
 * Main sidebar component.
 *
 * Key patterns:
 * - collapsible="icon" → shrinks to icon-only mode (3rem / 48px)
 * - group/sidebar → enables hover detection for ExpandButton
 * - SidebarRail → invisible edge hover area for quick toggle
 * - Keyboard shortcut ⌘B/Ctrl+B → built into SidebarProvider
 */
export function AppSidebar() {
  return (
    <Sidebar collapsible="icon" className="border-r group/sidebar">
      <SidebarHeader className="pb-0">
        <SidebarMenu>
          <SidebarMenuItem className="flex items-center gap-1">
            <ExpandButton />
            <WorkspaceSwitcher />
            <CollapseToggle />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup className="py-1">
          <SidebarMenu>
            <NavItem href="/" label="Home" icon={Home} />
            <NavItem label="Search" icon={Search} badge="K" onClick={() => {/* open search modal */}} />
          </SidebarMenu>
        </SidebarGroup>

        <SidebarGroup className="py-1">
          <SidebarGroupLabel className="text-[10px] uppercase tracking-wider text-muted-foreground/60 font-medium">
            Projects
          </SidebarGroupLabel>
          <SidebarMenu>
            <RecentItems />
            <NavItem href="/projects" label="All projects" icon={FolderOpen} />
            <NavItem href="/starred" label="Starred" icon={Star} />
            <NavItem href="/shared" label="Shared with me" icon={Users2} />
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="gap-0.5 pb-2">
        <SidebarSeparator />
        <UserRow />
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
