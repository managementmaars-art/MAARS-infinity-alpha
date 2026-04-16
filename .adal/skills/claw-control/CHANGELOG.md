# Changelog

All notable changes to Claw Control will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-06

### Added
- **Realtime feed polling**: Agent feed now auto-refreshes every 5 seconds for live updates
- **shadcn/ui integration**: Installed and configured shadcn/ui component library
  - Dark theme with coral accent color (#FF6B6B)
  - Components: Button, Card, Badge, Input, Dialog, DropdownMenu
  - CSS variables for consistent theming
  - Path aliases (`@/`) for cleaner imports
- **Utility library**: Added `cn()` utility function for className merging (clsx + tailwind-merge)

### Changed
- Updated Tailwind config with shadcn/ui CSS variables and animations
- Enhanced `useMessages` hook with 5-second polling interval
- Added duplicate message detection to prevent duplicates from polling + SSE

### Dependencies
- `@radix-ui/react-dialog` - Accessible dialog primitives
- `@radix-ui/react-dropdown-menu` - Accessible dropdown menu primitives
- `@radix-ui/react-slot` - Slot composition utility
- `class-variance-authority` - CSS variant management
- `clsx` - Conditional className construction
- `tailwind-merge` - Tailwind class deduplication
- `tailwindcss-animate` - Animation utilities for Tailwind

## [0.1.0] - 2026-02-04

### Added
- Initial Claw Control dashboard
- Agent monitoring panel
- Kanban board for task management
- Real-time SSE updates
- Responsive mobile layout with tab navigation
- Dark theme with coral accent colors
