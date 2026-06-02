# Schema and source contract tests for product-surface changes

Use this reference when a user requests a data-model or UI-surface requirement that can be verified from source before implementation.

## Durable pattern

1. Write a focused contract/source test before editing production files.
2. Assert the exact policy that must become true, not just that files changed.
3. Run only the focused test and confirm RED for the expected reason.
4. Implement the smallest schema/service/UI change.
5. Re-run the focused test, then the repository's standard lightweight verification.

## Useful assertions

### Required schema fields

When a data-model field must be non-null, assert both the positive and negative forms so nullable regressions are clear:

```ts
expect(schema).toContain("profileImageKey String");
expect(schema).not.toContain("profileImageKey String?");
```

### Existing-row-safe migrations

For adding a required column to a table that may already contain rows, assert the safe migration sequence:

```ts
expect(migration).toContain('ADD COLUMN "profileImageKey" TEXT');
expect(migration).toContain('UPDATE "Team" SET "profileImageKey" =');
expect(migration).toContain('ALTER COLUMN "profileImageKey" SET NOT NULL');
```

This catches the common bug of adding a Not Null column directly and breaking existing databases.

### Random default assignment

When new records must receive a random default from a registry, test boundaries by stubbing the random source:

```ts
vi.spyOn(Math, "random").mockReturnValue(0);
expect(pickRandomKey()).toBe(options[0].key);

vi.spyOn(Math, "random").mockReturnValue(0.999999);
expect(pickRandomKey()).toBe(options.at(-1)?.key);
```

Also assert the creation service writes the generated value, not only that the helper exists.

### Required fields and alternate creation paths

When an existing model field becomes required, search for direct ORM creation/upsert paths in seeds, fixtures, bootstrap helpers, and tests, not only the user-facing service.
A common CI-only failure is that `prisma generate` updates create-input types, then `tsc` catches a `profileImageKey`/required-field omission in seed or scenario helper files that focused feature tests did not compile.
Prefer putting a stable default on the shared seed/foundation builder, then override it in the user-facing creation service when the product requires random or context-specific defaults.

If the repository has a migration-artifact allowlist or schema-contract test that enumerates migration directories, update that contract together with the new migration; otherwise the full unit suite can fail even after focused tests, typecheck, and build logic are correct.

### Built-in assets before custom upload

When custom uploads are explicitly out of scope, assert the current contract:

```ts
expect(options.length).toBeGreaterThanOrEqual(30);
expect(source).not.toMatch(/upload|custom image/i);
```

## Pitfalls

- Do not treat migration validation failures from a local package-manager/node setup as a durable rule. Record the verification command and the exact local environment issue in the PR, then rely on CI/fresh-install validation when available.
- Avoid source tests that only assert broad strings like a component name. Pair them with data-flow assertions: form field name, save action input, create-service assignment, or migration DDL.
