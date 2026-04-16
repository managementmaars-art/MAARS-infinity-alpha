# Use Case Templates

Ready-to-copy templates for the most common patterns. Replace `Foo` / `foo` with your entity and domain names.

---

## Interface — operator auth, mutating

```ts
import { IUseCase } from "@workspace/lib";
import { Result } from "@workspace/lib/monad";
import IFoo from "~/dto/IFoo.js";
import NotFoundError from "~/errors/NotFoundError.js";
import NotLoggedError from "~/errors/NotLoggedError.js";
import { WithOperatorAuth } from "~/service/IOperatorAuthService.js";

type ICreateFoo = IUseCase<
  WithOperatorAuth<{
    name: string;
    description?: string;
  }>,
  Result<IFoo, NotLoggedError>
>;

export default ICreateFoo;
```

---

## Interface — business entity auth

```ts
import { IUseCase } from "@workspace/lib";
import { Result } from "@workspace/lib/monad";
import IFoo from "~/dto/IFoo.js";
import NotFoundError from "~/errors/NotFoundError.js";
import NotLoggedError from "~/errors/NotLoggedError.js";
import { WithImpresaAuth } from "~/service/IImpresaAuthService.js";

type IGetSelfFoo = IUseCase<
  WithImpresaAuth,
  Result<IFoo, NotLoggedError | NotFoundError>
>;

export default IGetSelfFoo;
```

---

## Interface — dual auth (either actor can call)

```ts
import { IUseCase } from "@workspace/lib";
import { Result } from "@workspace/lib/monad";
import IFoo from "~/dto/IFoo.js";
import NotFoundError from "~/errors/NotFoundError.js";
import { WithDualAuth } from "~/service/IDualAuthService.js";

type ISearchFoo = IUseCase<
  WithDualAuth<{
    name?: string;
    include_deleted?: boolean;
  }>,
  Result<IFoo[], NotFoundError>
>;

export default ISearchFoo;
```

---

## Interface — no auth (public operation)

```ts
import { IUseCase } from "@workspace/lib";
import { Result } from "@workspace/lib/monad";
import IFoo from "~/dto/IFoo.js";
import NotFoundError from "~/errors/NotFoundError.js";

type IGetPublicFoo = IUseCase<
  { slug: string },
  Result<IFoo, NotFoundError>
>;

export default IGetPublicFoo;
```

---

## Implementation — CREATE (with audit + transaction)

```ts
import { Result } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import audit from "~/decorator/audit.js";
import withTransaction from "~/decorator/withTransaction.js";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import type IFooRepo from "~/repo/IFooRepo.js";
import type IOperatorAuthService from "~/service/IOperatorAuthService.js";
import { WithOperatorAuth } from "~/service/IOperatorAuthService.js";
import ICreateFoo from "../ICreateFoo.js";

@injectable()
@withTransaction<ICreateFoo>()
@audit<ICreateFoo>({
  entity: Foo,
  title: "New Foo",
  verb: "CREATE",
  onOutput: (output, context) => {
    if (output.isSuccess()) context.setEntityId(output.data._id);
  },
})
export default class CreateFoo implements ICreateFoo {
  readonly name = this.constructor.name;

  constructor(
    @inject(Symbols.Repo.FooRepo) readonly repo: IFooRepo,
    @inject(Symbols.DomainService.OperatorAuthService) readonly auth: IOperatorAuthService,
  ) {}

  async execute(input: WithOperatorAuth<{ name: string; description?: string }>) {
    return this.auth.flatRun(async () => {
      const foo = Foo.create({ name: input.name, description: input.description });
      await this.repo.save(foo);
      return Result.ok(foo.toDTO());
    }, input);
  }
}
```

---

## Implementation — UPDATE (load → mutate → save)

```ts
import { Result } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import audit from "~/decorator/audit.js";
import withTransaction from "~/decorator/withTransaction.js";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import type IFooRepo from "~/repo/IFooRepo.js";
import type IOperatorAuthService from "~/service/IOperatorAuthService.js";
import { WithOperatorAuth } from "~/service/IOperatorAuthService.js";
import NotFoundError from "~/errors/NotFoundError.js";
import IUpdateFoo from "../IUpdateFoo.js";

@injectable()
@withTransaction<IUpdateFoo>()
@audit<IUpdateFoo>({
  entity: Foo,
  title: "Update Foo",
  verb: "UPDATE",
  onInput: (input, context) => {
    context.setEntityId(input._id);
  },
})
export default class UpdateFoo implements IUpdateFoo {
  readonly name = this.constructor.name;

  constructor(
    @inject(Symbols.Repo.FooRepo) readonly repo: IFooRepo,
    @inject(Symbols.DomainService.OperatorAuthService) readonly auth: IOperatorAuthService,
  ) {}

  async execute(input: WithOperatorAuth<{ _id: string; data: Partial<{ name: string }> }>) {
    return this.auth.flatRun(async () => {
      const maybe = await this.repo.get(input._id);
      if (!maybe.isSome()) return Result.err(new NotFoundError(Foo));

      maybe.data.update(input.data);
      await this.repo.save(maybe.data);
      return Result.ok(maybe.data.toDTO());
    }, input);
  }
}
```

---

## Implementation — DELETE (soft delete pattern)

```ts
import { Result } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import audit from "~/decorator/audit.js";
import withTransaction from "~/decorator/withTransaction.js";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import type IFooRepo from "~/repo/IFooRepo.js";
import type IOperatorAuthService from "~/service/IOperatorAuthService.js";
import { WithOperatorAuth } from "~/service/IOperatorAuthService.js";
import NotFoundError from "~/errors/NotFoundError.js";
import IDeleteFoo from "../IDeleteFoo.js";

@injectable()
@withTransaction<IDeleteFoo>()
@audit<IDeleteFoo>({
  entity: Foo,
  title: "Delete Foo",
  verb: "DELETE",
  onInput: (input, context) => {
    context.setEntityId(input._id);
  },
})
export default class DeleteFoo implements IDeleteFoo {
  readonly name = this.constructor.name;

  constructor(
    @inject(Symbols.Repo.FooRepo) readonly repo: IFooRepo,
    @inject(Symbols.DomainService.OperatorAuthService) readonly auth: IOperatorAuthService,
  ) {}

  async execute(input: WithOperatorAuth<{ _id: string }>) {
    return this.auth.flatRun(async () => {
      const maybe = await this.repo.get(input._id);
      if (!maybe.isSome()) return Result.err(new NotFoundError(Foo));

      maybe.data.delete(); // entity method marks deleted_at
      await this.repo.save(maybe.data);
      return Result.ok();
    }, input);
  }
}
```

---

## Implementation — GET (read-only, dual auth)

```ts
import { Result } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import type IFooRepo from "~/repo/IFooRepo.js";
import type IDualAuthService from "~/service/IDualAuthService.js";
import { WithDualAuth } from "~/service/IDualAuthService.js";
import NotFoundError from "~/errors/NotFoundError.js";
import IGetFoo from "../IGetFoo.js";

@injectable()
export default class GetFoo implements IGetFoo {
  readonly name = this.constructor.name;

  constructor(
    @inject(Symbols.Repo.FooRepo) readonly repo: IFooRepo,
    @inject(Symbols.DomainService.DualAuthService) readonly auth: IDualAuthService,
  ) {}

  async execute(input: WithDualAuth<{ _id: string }>) {
    return this.auth.flatRun(async () => {
      const maybe = await this.repo.get(input._id);
      if (!maybe.isSome()) return Result.err(new NotFoundError(Foo));
      return Result.ok(maybe.data.toDTO());
    }, input);
  }
}
```

---

## Implementation — SEARCH (read-only, operator auth)

```ts
import { Result } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import Symbols from "~/di/Symbols.js";
import type IFooRepo from "~/repo/IFooRepo.js";
import type IOperatorAuthService from "~/service/IOperatorAuthService.js";
import { WithOperatorAuth } from "~/service/IOperatorAuthService.js";
import ISearchFoo from "../ISearchFoo.js";

@injectable()
export default class SearchFoo implements ISearchFoo {
  readonly name = this.constructor.name;

  constructor(
    @inject(Symbols.Repo.FooRepo) readonly repo: IFooRepo,
    @inject(Symbols.DomainService.OperatorAuthService) readonly auth: IOperatorAuthService,
  ) {}

  async execute(input: WithOperatorAuth<{ name?: string; include_deleted?: boolean }>) {
    return this.auth.flatRun(async () => {
      const items = await this.repo.search({ name: input.name, include_deleted: input.include_deleted });
      return Result.ok(items.map(i => i.toDTO()));
    }, input);
  }
}
```

---

## Symbols.ts additions

```ts
// 1. Union type — add the new name:
type FooUC =
  | "CreateFoo"
  | "GetFoo"
  | "UpdateFoo"
  | "DeleteFoo"
  | "SearchFoo"; // ← new

// 2. Enum object — mirror exactly:
const FooUCEnum = {
  CreateFoo: "CreateFoo",
  GetFoo: "GetFoo",
  UpdateFoo: "UpdateFoo",
  DeleteFoo: "DeleteFoo",
  SearchFoo: "SearchFoo", // ← new
} as const;
```

---

## container.ts additions

```ts
// Top of file — import next to other foo use case imports:
import SearchFoo from "~/useCase/foo/impl/SearchFoo.js";

// In the bindings block — next to other foo bindings:
container.bind<ISearchFoo>(Symbols.UseCase.foo.SearchFoo).to(SearchFoo).inRequestScope();
```
