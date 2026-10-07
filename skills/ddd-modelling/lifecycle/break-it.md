# Trying to break the code

`ddd-review` (its break-it pass) and `secure-by-design-review` (its abuse attempts) run their attempts the same way. Each skill says what to attempt and what an outcome means for its findings.

- **One attempt, one file, one run.** A compile error stops the compiler, so several attempts in one file hide each other. Write each attempt in its own file and compile it separately.
- **Where the files go.** Somewhere the toolchain sees them and that is never committed:
  - Go: a new package directory inside the module, such as `internal/zz_breakit/<attempt>/`, one directory per attempt. A file outside the module cannot import the domain package.
  - TypeScript: a new directory covered by the project's `tsconfig.json`, such as `src/zz_breakit/`, one file per attempt, and run `tsc --noEmit` once per file's presence.
  - An attempt that needs unexported access goes in a `_test.go` file inside the package under test, or the equivalent for TypeScript.
- **Clean up and prove it.** Delete the directories, run `git status --porcelain`, and confirm in the report that nothing you created remains.

Record each outcome as one of:

- **compile**: does not compile
- **lint**: compiles, fails lint
- **runtime**: rejected by a constructor, decision function or parser, with a test proving it
- **test**: a rule was removed and a test failed
- **not prevented**: nothing stops it
