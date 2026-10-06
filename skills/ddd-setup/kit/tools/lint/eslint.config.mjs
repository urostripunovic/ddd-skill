import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      // Casts are how a value skips its parser. The few legitimate ones need a visible disable comment.
      "@typescript-eslint/consistent-type-assertions": ["error", { assertionStyle: "never" }],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/switch-exhaustiveness-check": [
        "error",
        // A default clause would otherwise hide a variant added later.
        { considerDefaultExhaustiveForUnions: false },
      ],
    },
  },
  {
    // DOMAIN-PATHS: the globs of this repository's domain code, set in the repository's own config.
    // tools/check-cards.sh points them at the card examples itself; keep this marker line.
    files: ["src/domain/**/*.ts"],
    rules: {
      "no-console": "error",
      "no-restricted-imports": [
        "error",
        {
          // Node's I/O modules also load without the node: prefix, so they are named here as well.
          paths: [
            "child_process", "cluster", "dgram", "dns", "dns/promises", "fs", "fs/promises", "http", "http2",
            "https", "net", "os", "process", "readline", "tls", "worker_threads",
          ].map((name) => ({
            name,
            message: "The domain does no I/O. Declare the contract here and implement it outside the domain.",
          })),
          patterns: [
            {
              group: ["node:*"],
              message: "The domain does no I/O. Declare the contract here and implement it outside the domain.",
            },
          ],
        },
      ],
      "no-restricted-globals": [
        "error",
        { name: "fetch", message: "The domain does no I/O. The workflow or an adapter calls other systems." },
        { name: "process", message: "Configuration is read at the boundary and passed in as values." },
      ],
      "no-restricted-syntax": [
        "error",
        {
          selector: "ThrowStatement",
          message:
            "A business failure is returned as a Result. A throw that marks a bug (assertNever, corrupt history) needs a disable comment saying so.",
        },
        {
          selector: "NewExpression[callee.name='Date'][arguments.length=0]",
          message: "A decision takes the time as a parameter, so it stays pure and testable.",
        },
        {
          selector: "CallExpression[callee.object.name='Date'][callee.property.name='now']",
          message: "A decision takes the time as a parameter, so it stays pure and testable.",
        },
        {
          selector: "CallExpression[callee.object.name='Math'][callee.property.name='random']",
          message: "A decision takes generated values as parameters.",
        },
        {
          selector: "CallExpression[callee.property.name='randomUUID']",
          message: "A decision takes generated IDs as parameters.",
        },
      ],
    },
  },
);
