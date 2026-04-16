# Loader / Action Templates

## Loader — by ID from URL param

```ts
import { container, IGetFoo, Symbols } from '@workspace/core';
import type { LoaderFunctionArgs } from 'react-router';
import z from 'zod';
import requireOperatorSessId from '~/shared/utils/requireOperatorSessId';

const params_validator = z.object({ _id: z.string().min(1) });

export async function loader(args: LoaderFunctionArgs) {
  const { _id } = params_validator.parse(args.params);
  const session_id = await requireOperatorSessId(args.request);

  const result = await container
    .get<IGetFoo>(Symbols.UseCase.foo.GetFoo)
    .execute({ session_id, _id });

  if (result.isFailure()) throw new Response('Not found', { status: 404 });
  return { foo: result.data };
}
```

---

## Loader — search / list from query string

```ts
import { container, ISearchFoo, Symbols } from '@workspace/core';
import type { LoaderFunctionArgs } from 'react-router';
import z from 'zod';
import requireOperatorSessId from '~/shared/utils/requireOperatorSessId';

const query_validator = z.object({
  search: z.string().optional(),
  page_n: z.coerce.number().int().min(1).optional().default(1),
  page_size: z.coerce.number().int().min(10).max(100).optional().default(25),
});

export async function loader(args: LoaderFunctionArgs) {
  const query = query_validator.parse(
    Object.fromEntries(new URL(args.request.url).searchParams),
  );
  const session_id = await requireOperatorSessId(args.request);

  const result = await container
    .get<ISearchFoo>(Symbols.UseCase.foo.SearchFoo)
    .execute({ session_id, ...query });

  const items = result.unwrapOrThrow();

  // pagination helpers
  const usp = new URL(args.request.url).searchParams;
  let next_link = '';
  if (items.length === query.page_size) {
    const p = new URLSearchParams(usp);
    p.set('page_n', String(query.page_n + 1));
    next_link = `?${p}`;
  }
  let prev_link = '';
  if (query.page_n > 1) {
    const p = new URLSearchParams(usp);
    p.set('page_n', String(query.page_n - 1));
    prev_link = `?${p}`;
  }

  return { items, next_link, prev_link, current_page: query.page_n };
}
```

---

## Action — single intent

```ts
import { container, ICreateFoo, Symbols } from '@workspace/core';
import { Toast } from '@workspace/lib/monad';
import type { ActionFunctionArgs } from 'react-router';
import z from 'zod';
import requireOperatorSessId from '~/shared/utils/requireOperatorSessId';

const body_validator = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional().transform(v => v === '' ? undefined : v),
});

export async function action(args: ActionFunctionArgs) {
  const session_id = await requireOperatorSessId(args.request);
  const body = body_validator.safeParse(Object.fromEntries(await args.request.formData()));
  if (!body.success) return Toast.err('Invalid input', body.error.flatten());

  const result = await container
    .get<ICreateFoo>(Symbols.UseCase.foo.CreateFoo)
    .execute({ session_id, ...body.data });

  return Toast.fromResult(result, 'Created successfully');
}
```

---

## Action — multiple intents (discriminated union)

```ts
import { container, ICreateFoo, IDeleteFoo, IUpdateFoo, Symbols } from '@workspace/core';
import { Toast } from '@workspace/lib/monad';
import type { ActionFunctionArgs } from 'react-router';
import z from 'zod';
import requireOperatorSessId from '~/shared/utils/requireOperatorSessId';

const body_validator = z.discriminatedUnion('intent', [
  z.object({ intent: z.literal('CREATE'), name: z.string().min(1) }),
  z.object({ intent: z.literal('UPDATE'), id: z.string(), name: z.string().min(1) }),
  z.object({ intent: z.literal('DELETE'), id: z.string() }),
]);

export async function action(args: ActionFunctionArgs) {
  const session_id = await requireOperatorSessId(args.request);
  const body = body_validator.safeParse(Object.fromEntries(await args.request.formData()));
  if (!body.success) return Toast.err('Invalid input', body.error.flatten());

  switch (body.data.intent) {
    case 'CREATE': {
      const result = await container
        .get<ICreateFoo>(Symbols.UseCase.foo.CreateFoo)
        .execute({ session_id, name: body.data.name });
      return Toast.fromResult(result, 'Created');
    }
    case 'UPDATE': {
      const result = await container
        .get<IUpdateFoo>(Symbols.UseCase.foo.UpdateFoo)
        .execute({ session_id, _id: body.data.id, name: body.data.name });
      return Toast.fromResult(result, 'Updated');
    }
    case 'DELETE': {
      const result = await container
        .get<IDeleteFoo>(Symbols.UseCase.foo.DeleteFoo)
        .execute({ session_id, _id: body.data.id });
      return Toast.fromResult(result, 'Deleted');
    }
    default:
      return Toast.err('Unknown action', {});
  }
}
```

---

## Action — with redirect after mutation

```ts
import { redirect } from 'react-router';
// ... other imports

export async function action(args: ActionFunctionArgs) {
  const session_id = await requireOperatorSessId(args.request);
  const body = body_validator.safeParse(Object.fromEntries(await args.request.formData()));
  if (!body.success) return Toast.err('Invalid input', body.error.flatten());

  const result = await container
    .get<ICreateFoo>(Symbols.UseCase.foo.CreateFoo)
    .execute({ session_id, ...body.data });

  if (result.isFailure()) return Toast.err('Failed to create', {});
  throw redirect(`/admin/foo/${result.data._id}`);
}
```
