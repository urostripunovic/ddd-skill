# TypeScript

How the kit's patterns are written in TypeScript. Read this once before writing TypeScript domain code, then the example files in this directory for the cards the task needs.

## Idioms

- Domain primitive: branded type plus a `parse...` function returning `Result`.
- Sum type: discriminated union, handled with a `switch` ending in `assertNever`.
- Every field and array is `readonly`.
- Types do not exist at runtime. Every boundary parses from `unknown`.
- Failures are a `Result` with a discriminated union of errors. Do not throw for business outcomes.

## Checks

- Compile: `tsc --noEmit`, with the compiler options of `tools/lint/tsconfig.json`.
- Lint: ESLint, with the rules of `tools/lint/eslint.config.mjs` in the repository's config: no `any`, no `as`, exhaustive switches; no `throw`, clock or randomness in the domain directories.
- Property tests: `fast-check` if the repository has it.

## Never, to make a check pass

- `as`, `any`, `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, non-null `!`
- a `default` clause that swallows variants

Exceptions: the single brand cast inside a parser after validation, and a throw for a bug (`assertNever`, corrupt history, or attempted secret serialisation). Each needs a local disable comment naming the rule and explaining why. Never use these exceptions for an expected business failure.
