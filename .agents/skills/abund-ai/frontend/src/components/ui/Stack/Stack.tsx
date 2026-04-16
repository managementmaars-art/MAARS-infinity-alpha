import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { cn } from '@/lib/utils'

type SpacingValue = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '8' | '10' | '12'

const spacingStyles: Record<SpacingValue, string> = {
  '0': 'gap-0',
  '1': 'gap-1',
  '2': 'gap-2',
  '3': 'gap-3',
  '4': 'gap-4',
  '5': 'gap-5',
  '6': 'gap-6',
  '8': 'gap-8',
  '10': 'gap-10',
  '12': 'gap-12',
} as const

export interface StackProps extends ComponentPropsWithoutRef<'div'> {
  /** Direction of the stack */
  direction?: 'row' | 'col'
  /** Gap between items */
  gap?: SpacingValue
  /** Alignment on cross axis */
  align?: 'start' | 'center' | 'end' | 'stretch' | 'baseline'
  /** Justification on main axis */
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly'
  /** Whether items should wrap */
  wrap?: boolean
  /** Render as different element */
  as?: 'div' | 'section' | 'article' | 'nav' | 'aside' | 'main'
}

const alignStyles = {
  start: 'items-start',
  center: 'items-center',
  end: 'items-end',
  stretch: 'items-stretch',
  baseline: 'items-baseline',
} as const

const justifyStyles = {
  start: 'justify-start',
  center: 'justify-center',
  end: 'justify-end',
  between: 'justify-between',
  around: 'justify-around',
  evenly: 'justify-evenly',
} as const

/**
 * Flexbox stack component for layout
 *
 * @example
 * ```tsx
 * <Stack direction="col" gap="4" align="center">
 *   <Avatar />
 *   <p>Agent Name</p>
 * </Stack>
 * ```
 */
export const Stack = forwardRef<HTMLDivElement, StackProps>(
  (
    {
      direction = 'col',
      gap = '4',
      align = 'stretch',
      justify = 'start',
      wrap = false,
      as: Component = 'div',
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <Component
        ref={ref}
        className={cn(
          'flex',
          direction === 'row' ? 'flex-row' : 'flex-col',
          spacingStyles[gap],
          alignStyles[align],
          justifyStyles[justify],
          wrap && 'flex-wrap',
          className
        )}
        {...props}
      >
        {children}
      </Component>
    )
  }
)
Stack.displayName = 'Stack'

/**
 * Horizontal stack (convenience wrapper)
 */
export const HStack = forwardRef<HTMLDivElement, Omit<StackProps, 'direction'>>(
  (props, ref) => <Stack ref={ref} direction="row" {...props} />
)
HStack.displayName = 'HStack'

/**
 * Vertical stack (convenience wrapper)
 */
export const VStack = forwardRef<HTMLDivElement, Omit<StackProps, 'direction'>>(
  (props, ref) => <Stack ref={ref} direction="col" {...props} />
)
VStack.displayName = 'VStack'
