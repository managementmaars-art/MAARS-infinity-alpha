import { forwardRef, type ComponentPropsWithoutRef } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { cn } from '@/lib/utils'
import {
  ICON_MAP,
  colorStyles,
  sizeStyles,
  type IconName,
  type IconColor,
  type IconSize,
} from './icons'

export interface IconProps extends Omit<
  ComponentPropsWithoutRef<'span'>,
  'children'
> {
  /** Semantic icon name */
  name: IconName
  /** Icon size */
  size?: IconSize
  /** Icon color variant */
  color?: IconColor
  /** Accessible label (required for meaningful icons) */
  label?: string
}

/**
 * Icon component wrapping Font Awesome for consistent usage
 *
 * @example
 * ```tsx
 * <Icon name="feed" size="md" />
 * <Icon name="heart" color="heart" label="Likes" />
 * <Icon name="verified" color="verified" size="sm" />
 * ```
 */
export const Icon = forwardRef<HTMLSpanElement, IconProps>(
  (
    { name, size = 'md', color = 'inherit', label, className, ...props },
    ref
  ) => {
    const icon: IconDefinition = ICON_MAP[name]

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          sizeStyles[size],
          colorStyles[color],
          className
        )}
        role={label ? 'img' : 'presentation'}
        aria-label={label}
        aria-hidden={!label}
        {...props}
      >
        <FontAwesomeIcon icon={icon} />
      </span>
    )
  }
)
Icon.displayName = 'Icon'
