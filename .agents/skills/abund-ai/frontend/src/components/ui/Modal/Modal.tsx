import {
  forwardRef,
  useEffect,
  useRef,
  type ComponentPropsWithoutRef,
} from 'react'
import { cn } from '@/lib/utils'

export interface ModalProps extends ComponentPropsWithoutRef<'dialog'> {
  /** Whether the modal is open */
  open?: boolean
  /** Callback when modal should close */
  onClose?: () => void
  /** Modal size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  /** Title for the modal */
  title?: string
  /** Description for the modal */
  description?: string
}

const sizeStyles = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-4xl',
} as const

/**
 * Modal dialog component with backdrop and focus trap
 *
 * @example
 * ```tsx
 * <Modal
 *   open={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Confirm Action"
 * >
 *   <p>Are you sure?</p>
 * </Modal>
 * ```
 */
export const Modal = forwardRef<HTMLDialogElement, ModalProps>(
  (
    {
      open = false,
      onClose,
      size = 'md',
      title,
      description,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const internalRef = useRef<HTMLDialogElement>(null)
    // Use the forwarded ref if provided, otherwise use internal ref
    const dialogRefObject =
      typeof ref === 'function' ? internalRef : (ref ?? internalRef)
    const resolvedRef = dialogRefObject

    useEffect(() => {
      const dialog = resolvedRef.current
      if (dialog === null) return

      if (open) {
        dialog.showModal()
        document.body.style.overflow = 'hidden'
      } else {
        dialog.close()
        document.body.style.overflow = ''
      }

      return () => {
        document.body.style.overflow = ''
      }
    }, [open, resolvedRef])

    useEffect(() => {
      const dialog = resolvedRef.current
      if (dialog === null) return

      const handleClose = () => {
        onClose?.()
      }

      dialog.addEventListener('close', handleClose)
      return () => {
        dialog.removeEventListener('close', handleClose)
      }
    }, [onClose, resolvedRef])

    const handleBackdropClick = (e: React.MouseEvent) => {
      if (e.target === resolvedRef.current) {
        onClose?.()
      }
    }

    return (
      <dialog
        ref={resolvedRef}
        onClick={handleBackdropClick}
        className={cn(
          // Reset dialog styles
          'm-0 border-0 p-0',
          // Backdrop
          'backdrop:bg-black/50 backdrop:backdrop-blur-sm',
          // Positioning
          'fixed inset-0',
          'flex items-center justify-center',
          // Animation
          'opacity-0 open:opacity-100',
          'transition-opacity duration-200',
          className
        )}
        aria-labelledby={title ? 'modal-title' : undefined}
        aria-describedby={description ? 'modal-description' : undefined}
        {...props}
      >
        <div
          className={cn(
            'relative mx-4 my-8 w-full',
            'bg-[var(--bg-surface)]',
            'rounded-xl shadow-xl',
            'max-h-[calc(100vh-4rem)] overflow-auto',
            sizeStyles[size]
          )}
          onClick={(e) => {
            e.stopPropagation()
          }}
        >
          {/* Header */}
          {(title ?? onClose) && (
            <div className="flex items-start justify-between p-6 pb-0">
              <div>
                {title && (
                  <h2
                    id="modal-title"
                    className="text-lg font-semibold text-[var(--text-primary)]"
                  >
                    {title}
                  </h2>
                )}
                {description && (
                  <p
                    id="modal-description"
                    className="mt-1 text-sm text-[var(--text-muted)]"
                  >
                    {description}
                  </p>
                )}
              </div>
              {onClose && (
                <button
                  type="button"
                  onClick={onClose}
                  className={cn(
                    '-mr-2 -mt-2 rounded-lg p-2',
                    'text-[var(--text-muted)] hover:text-[var(--text-primary)]',
                    'hover:bg-[var(--bg-hover)]',
                    'transition-colors',
                    'focus:ring-primary-500 focus:outline-none focus:ring-2'
                  )}
                  aria-label="Close modal"
                >
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="p-6">{children}</div>
        </div>
      </dialog>
    )
  }
)
Modal.displayName = 'Modal'

/**
 * Modal footer for action buttons
 */
export const ModalFooter = forwardRef<
  HTMLDivElement,
  ComponentPropsWithoutRef<'div'>
>(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center justify-end gap-3 pt-4',
      'border-t border-[var(--border-subtle)]',
      '-mx-6 -mb-6 px-6 py-4',
      'rounded-b-xl bg-[var(--bg-elevated)]',
      className
    )}
    {...props}
  >
    {children}
  </div>
))
ModalFooter.displayName = 'ModalFooter'
