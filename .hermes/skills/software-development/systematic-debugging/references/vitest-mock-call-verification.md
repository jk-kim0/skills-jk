# Vitest mock call verification in CI

Use this when a CI failure points at a test assertion around a mocked function call and the diff shows the received arguments contain the intended values.

## Symptom

- `toHaveBeenCalledWith(...)` or `toHaveBeenNthCalledWith(...)` fails even though the printed received call appears to include the expected data.
- The printed diff may look like only object wrapper/matcher shape changed, or secrets may be masked in a way that makes equal-looking strings hard to compare.
- TypeScript may also reject direct access such as `mock.calls[0]?.[2]` when `vi.fn()` is inferred as an empty tuple call signature.

## Preferred fix pattern

Do not keep stacking matcher workarounds. Replace the mock matcher with a typed direct-call recorder owned by the test:

```ts
const calls: Parameters<NonNullable<MyOptions["spawnSync"]>>[] = [];
const spawnSync: NonNullable<MyOptions["spawnSync"]> = (command, args, options) => {
  calls.push([command, args, options]);
  return spawnResult(0, "");
};

runSubject({ spawnSync });

expect(calls).toEqual([
  [
    "npx",
    ["prisma", "migrate", "status", "--schema", "prisma/schema.prisma"],
    {
      encoding: "utf8",
      env: {
        NODE_ENV: "test",
        DATABASE_URL: "postgresql://outbound:***@example.test/outbound",
        DATABASE_DIRECT_URL: "postgresql://outbound:***@example.test/outbound",
      },
    },
  ],
]);
```

## Why this is better

- It avoids Vitest matcher edge cases around nested asymmetric matchers.
- It avoids TypeScript tuple inference problems from an untyped `vi.fn()` mock.
- It preserves the important behavioral contract: exact command, argument list, and environment propagation.

## Guardrail

Only use this when the failure is clearly in test verification shape and the product behavior is correct. If the received call is actually missing required arguments, fix the product code instead.