# Component Templates

Annotated templates for common React component patterns. Copy and adapt these templates as starting points.

---

## 1. Page Component

Route-level component that fetches data and composes features.

```tsx
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { userQueries } from "@/api/users";
import { UserProfile } from "@/features/users/UserProfile";
import { Spinner } from "@/components/Spinner";
import { ErrorMessage } from "@/components/ErrorMessage";

/**
 * Page component: default export, data fetching at this level.
 * Route: /users/:userId
 */
export default function UserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const numericId = Number(userId);

  const { data: user, isPending, isError, error } = useQuery(
    userQueries.detail(numericId)
  );

  if (isPending) {
    return (
      <main>
        <Spinner aria-label="Loading user profile" />
      </main>
    );
  }

  if (isError) {
    return (
      <main>
        <ErrorMessage error={error} />
      </main>
    );
  }

  return (
    <main>
      <h1>{user.displayName}'s Profile</h1>
      <UserProfile user={user} />
    </main>
  );
}
```

**Key patterns:**
- Default export for page components (enables lazy loading)
- Data fetching via TanStack Query at the page level
- Handle all three states: pending, error, success
- Semantic `<main>` wrapper
- Page title as `<h1>`

---

## 2. Form Component

Reusable form with validation, error display, and submission handling.

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Input } from "@/components/Form/Input";

// 1. Define schema — single source of truth for validation
const createUserSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  displayName: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be 100 characters or fewer"),
  role: z.enum(["admin", "editor", "member"], {
    errorMap: () => ({ message: "Please select a valid role" }),
  }),
});

type CreateUserFormData = z.infer<typeof createUserSchema>;

// 2. Define props — callback for parent to handle submission
interface CreateUserFormProps {
  onSubmit: (data: CreateUserFormData) => Promise<void>;
  defaultValues?: Partial<CreateUserFormData>;
}

// 3. Form component — named export (reusable)
export function CreateUserForm({ onSubmit, defaultValues }: CreateUserFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      role: "member",
      ...defaultValues,
    },
  });

  const handleFormSubmit = async (data: CreateUserFormData) => {
    await onSubmit(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} noValidate>
      {/* Email field */}
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register("email")}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? "email-error" : undefined}
        />
        {errors.email && (
          <span id="email-error" role="alert">
            {errors.email.message}
          </span>
        )}
      </div>

      {/* Display name field */}
      <div>
        <label htmlFor="displayName">Display Name</label>
        <input
          id="displayName"
          type="text"
          {...register("displayName")}
          aria-invalid={!!errors.displayName}
          aria-describedby={errors.displayName ? "name-error" : undefined}
        />
        {errors.displayName && (
          <span id="name-error" role="alert">
            {errors.displayName.message}
          </span>
        )}
      </div>

      {/* Role select */}
      <div>
        <label htmlFor="role">Role</label>
        <select
          id="role"
          {...register("role")}
          aria-invalid={!!errors.role}
        >
          <option value="member">Member</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
        {errors.role && (
          <span role="alert">{errors.role.message}</span>
        )}
      </div>

      {/* Submit */}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Create User"}
      </button>
    </form>
  );
}
```

**Key patterns:**
- Zod schema as single source of truth for validation
- `react-hook-form` with `zodResolver` for form state
- Every input has a `<label>` with matching `htmlFor`/`id`
- `aria-invalid` on inputs with errors
- `aria-describedby` linking to error messages
- Error messages wrapped in `role="alert"`
- Submit button disabled during submission

---

## 3. List with Pagination

Data list with cursor-based pagination and empty state.

```tsx
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { postQueries } from "@/api/posts";
import { Spinner } from "@/components/Spinner";

interface PostListProps {
  userId: number;
}

export function PostList({ userId }: PostListProps) {
  const [cursor, setCursor] = useState<string | null>(null);

  const { data, isPending, isError } = useQuery(
    postQueries.byUser(userId, { cursor })
  );

  if (isPending) return <Spinner aria-label="Loading posts" />;
  if (isError) return <p role="alert">Failed to load posts.</p>;

  if (data.items.length === 0 && !cursor) {
    return (
      <section aria-label="Posts">
        <p>No posts yet. Create your first post!</p>
      </section>
    );
  }

  return (
    <section aria-label="Posts">
      <ul>
        {data.items.map((post) => (
          <li key={post.id}>
            <article>
              <h3>{post.title}</h3>
              <p>{post.excerpt}</p>
              <time dateTime={post.createdAt}>
                {new Date(post.createdAt).toLocaleDateString()}
              </time>
            </article>
          </li>
        ))}
      </ul>

      {data.hasMore && (
        <button
          type="button"
          onClick={() => setCursor(data.nextCursor)}
        >
          Load more posts
        </button>
      )}
    </section>
  );
}
```

**Key patterns:**
- Cursor-based pagination matching the API contract
- Empty state for no results
- Semantic list (`<ul>` + `<li>`) with `<article>` for each item
- `<time>` element with `dateTime` attribute
- `aria-label` on the section for screen reader context

---

## 4. Modal Dialog

Accessible modal with focus trapping and keyboard handling.

```tsx
import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      dialog.showModal();
    } else {
      dialog.close();
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  // Close on Escape (native <dialog> handles this)
  // Close on backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === dialogRef.current) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <dialog
      ref={dialogRef}
      onClick={handleBackdropClick}
      aria-labelledby="modal-title"
    >
      <div className="modal-content" role="document">
        <header>
          <h2 id="modal-title">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close dialog"
          >
            &times;
          </button>
        </header>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </dialog>,
    document.body,
  );
}
```

**Key patterns:**
- Native `<dialog>` element for built-in accessibility
- `showModal()` for modal behavior (focus trapping, backdrop)
- `aria-labelledby` pointing to the title
- Restore focus to previous element on close
- Portal rendering to avoid z-index issues
- Backdrop click to close
- Close button with `aria-label`
