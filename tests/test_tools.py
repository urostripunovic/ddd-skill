"""Tool regressions: python3 -m unittest discover -s tests -v.

Uses temporary repositories; no installed project or sibling eval is changed.
Language compilation and lint are checked separately with check-cards.sh.
"""
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
KIT = ROOT / "skills/ddd-setup/kit"
TOOLS = KIT / "tools"

MODEL = """# Context: Ordering

Status: draft
Depth: standard

## The flow

1. A customer starts an order (`StartOrder`) and places it (`PlaceOrder`).

## Domain primitives

None.

## Aggregate: Order

### States
```
type Order = DraftOrder | PlacedOrder
terminal PlacedOrder
DraftOrder = {}
PlacedOrder = {}
```

### Commands
```
StartOrder : () -> DraftOrder
PlaceOrder : DraftOrder -> PlacedOrder
```
| Command | Issued by | Notes |
|---|---|---|
| StartOrder | customer | |
| PlaceOrder | customer | |

### Command × state matrix
| State | PlaceOrder |
|---|---|
| DraftOrder | yes |
| PlacedOrder | no: already placed |

### Events
None.

### Invariants
None.

### Failures
None.

### Use-case failures
| Failure | Raised when |
|---|---|
| OrderNotDraft | PlaceOrder for an order that is not a draft |

### Examples
| # | Covers | Given | When | Then |
|---|---|---|---|---|
| 1 | StartOrder | no order | StartOrder | DraftOrder |
| 2 | PlaceOrder | DraftOrder | PlaceOrder | PlacedOrder |

### Races
None.

### Facts from outside
None.

## Rules across aggregates
None.

## Policies
None.

## Decisions
None.

## Open questions
None.
"""


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = pathlib.Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.model = self.repo / "docs/domain/contexts/ordering.md"
        self.model.parent.mkdir(parents=True)
        self.model.write_text(MODEL)
        (self.repo / "GLOSSARY.md").write_text(
            "# Ordering\n\n## Language\n\n"
            "**Order**:\nAn order.\n\n"
            "**Draft order**:\nAn editable order.\n\n"
            "**Placed order**:\nA committed order.\n"
        )

    def run_tool(self, name, *args):
        command = [str(TOOLS / name), *map(str, args)]
        if name.endswith(".py"):
            command.insert(0, "python3")
        return subprocess.run(command, cwd=self.repo, capture_output=True, text=True)

    def hash_model(self):
        result = self.run_tool("model-hash.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_existing_hash_is_preserved(self):
        # The valid original format keeps its approval hash after a tool upgrade.
        expected = subprocess.run(
            ["git", "hash-object", "--stdin"],
            input=MODEL.replace("Status: draft\n", ""),
            text=True, capture_output=True, check=True,
        ).stdout.strip()[:12]
        self.assertEqual(self.hash_model(), expected)

    def test_status_and_trailing_notes_do_not_change_hash(self):
        before = self.hash_model()
        self.model.write_text(MODEL.replace("Status: draft", "Status: approved by test")
                              + "\n## Migration\n1. Move storage.\n\n## Amendments\nA finding.\n")
        self.assertEqual(self.hash_model(), before)
        self.model.write_text(self.model.read_text().replace("A finding.", "A different finding."))
        self.assertEqual(self.hash_model(), before)

    def test_approved_body_edit_is_detected(self):
        for word in ("approved", "Approved", "APPROVED"):
            with self.subTest(word=word):
                self.model.write_text(MODEL)
                approved = MODEL.replace("Status: draft", f"Status: {word} by test, model-hash {self.hash_model()}")
                self.model.write_text(approved.replace("already placed", "placing is final"))
                result = self.run_tool("check-model.sh", self.model)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("edited after approval", result.stdout)

    def test_model_sections_cannot_follow_notes(self):
        for heading in ("Migration", "Amendments"):
            with self.subTest(heading=heading):
                self.model.write_text(MODEL.replace("## Aggregate:", f"## {heading}\nNotes.\n\n## Aggregate:"))
                result = self.run_tool("model-hash.sh", self.model)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("model section after", result.stderr)
                check = self.run_tool("check-model.sh", self.model)
                self.assertNotEqual(check.returncode, 0)
                self.assertIn("model hash failed", check.stdout)

    def test_similar_heading_is_not_an_exclusion(self):
        self.model.write_text(MODEL + "\n## Migration rules\nKeep historical prices.\n")
        before = self.hash_model()
        self.model.write_text(self.model.read_text().replace("historical prices", "historical quantities"))
        self.assertNotEqual(self.hash_model(), before)

    def test_comment_and_code_headings_do_not_start_notes(self):
        for example in ("<!--\n## Migration\n-->", "```md\n## Amendments\n```", "~~~md\n## Migration\n~~~"):
            with self.subTest(example=example):
                self.model.write_text(MODEL.replace("## Aggregate:", example + "\n\n## Aggregate:"))
                before = self.hash_model()
                self.model.write_text(self.model.read_text().replace("already placed", "placing is final"))
                self.assertNotEqual(self.hash_model(), before)

    def test_code_in_notes_may_contain_model_headings(self):
        before = self.hash_model()
        self.model.write_text(MODEL + "\n## Amendments\n```md\n## Aggregate: Order\n```\n")
        self.assertEqual(self.hash_model(), before)

    def test_valid_strict_override(self):
        self.model.write_text(MODEL.replace("Depth: standard", "Depth: standard\nStrict commands: PlaceOrder"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("strict scope for PlaceOrder: examples 2", result.stdout)

    def test_strict_scope_lists_the_rows_that_name_the_command(self):
        model = (MODEL.replace("Depth: standard", "Depth: standard\nStrict commands: PlaceOrder")
                 .replace("## Domain primitives\n\nNone.",
                          "## Domain primitives\n\n| Name | Underlying type | Rules | Why | Sensitive? |\n|---|---|---|---|---|\n"
                          "| Amount | integer | 1..100 | (assumed) | no |\n| Note | string | 1..20 | (assumed) | no |")
                 .replace("DraftOrder = {}", "DraftOrder = { note: Note }")
                 .replace("PlacedOrder = {}", "PlacedOrder = { note: Note, amount: Amount }")
                 .replace("### Invariants\nNone.",
                          "### Invariants\n| # | Invariant | Enforced by | Commands that could break it |\n|---|---|---|---|\n"
                          "| 1 | paid | decision function PlaceOrder | PlaceOrder |")
                 .replace("### Races\nNone.",
                          "### Races\n| Commands | Who wins | What the other gets |\n|---|---|---|\n| PlaceOrder twice | first | OrderNotDraft |"))
        self.model.write_text(model)
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = next(l for l in result.stdout.splitlines() if "strict scope for PlaceOrder" in l)
        self.assertIn("invariants 1", line)
        self.assertIn("races PlaceOrder twice", line)
        self.assertIn("primitives it adds Amount", line)
        self.assertNotIn("Note", line)

    def test_missing_template_sections_are_errors(self):
        for section in ("### Invariants\nNone.\n", "### Facts from outside\nNone.\n", "## Decisions\nNone.\n"):
            with self.subTest(section=section):
                self.model.write_text(MODEL.replace(section, ""))
                result = self.run_tool("check-model.sh", self.model)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(section.split("\n")[0].lstrip("# "), result.stdout)
        self.model.write_text(MODEL.replace("1. A customer", "A customer"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertIn("no numbered steps", result.stdout)

    def test_example_numbers_are_unique(self):
        self.model.write_text(MODEL.replace("| 2 | PlaceOrder |", "| 1 | PlaceOrder |"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("example number 1 is used twice", result.stdout)

    def test_refused_command_without_use_case_failure_warns(self):
        self.model.write_text(MODEL.replace("| OrderNotDraft | PlaceOrder for an order that is not a draft |", "| OrderNotFound | no order |"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning: aggregate Order: the matrix refuses PlaceOrder in PlacedOrder", result.stdout)

    def test_unknown_strict_override(self):
        self.model.write_text(MODEL.replace("Depth: standard", "Depth: standard\nStrict commands: RefundPayment"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RefundPayment", result.stdout)
        self.assertIn("no command signature", result.stdout)

    def test_ambiguous_strict_overrides_are_rejected(self):
        for value in ("PlaceOrder,", "PlaceOrder\nStrict commands: StartOrder", ""):
            with self.subTest(value=value):
                self.model.write_text(MODEL.replace("Depth: standard", f"Depth: standard\nStrict commands: {value}"))
                result = self.run_tool("check-model.sh", self.model)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Strict commands", result.stdout)

    def test_card_extraction_reaches_reference_domain_paths(self):
        out = self.repo / "examples"
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards", out)
        self.assertEqual(result.returncode, 0, result.stderr)
        for lang, path, suffix in (("go", "internal", "x.go"), ("ts", "src", "*.ts")):
            base = out / lang / path
            self.assertEqual(len(list(base.rglob(suffix))), 20)
            self.assertTrue(list((base / "domain").rglob(suffix)))
            self.assertTrue(list((base / "boundary").rglob(suffix)))
        self.assertTrue((out / "ts/src/domain/11_decider.ts").is_file())
        self.assertTrue((out / "go/internal/boundary/c07_parse_at_the_boundary/x.go").is_file())

    def test_card_check_keeps_domain_rules_when_the_team_set_its_own_paths(self):
        lint = self.repo / "lint"
        lint.mkdir()
        go = (TOOLS / "lint/.golangci.yml").read_text()
        go = go.replace('- "**/internal/domain/**"', '- "**/internal/ordering/**"\n            - "**/internal/billing/**"')
        go = go.replace("path-except: internal/domain/", "path-except: internal/(ordering|billing)/")
        (lint / ".golangci.yml").write_text(go)
        ts = (TOOLS / "lint/eslint.config.mjs").read_text().replace("src/domain/**/*.ts", "src/ordering/**/*.ts")
        (lint / "eslint.config.mjs").write_text(ts)
        out = self.repo / "examples"
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards", out, lint)
        self.assertEqual(result.returncode, 0, result.stderr)
        pinned_go = (out / "go/.golangci.yml").read_text()
        self.assertIn('- "**/internal/domain/**"', pinned_go)
        self.assertIn("path-except: internal/domain/", pinned_go)
        self.assertNotIn("ordering", pinned_go)
        self.assertIn('files: ["src/domain/**/*.ts"]', (out / "ts/eslint.config.mjs").read_text())

    def test_card_check_needs_the_domain_path_markers(self):
        lint = self.repo / "lint"
        lint.mkdir()
        (lint / ".golangci.yml").write_text((TOOLS / "lint/.golangci.yml").read_text().replace("DOMAIN-PATHS", "paths"))
        (lint / "eslint.config.mjs").write_text((TOOLS / "lint/eslint.config.mjs").read_text())
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards", self.repo / "examples", lint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DOMAIN-PATHS", result.stderr)

    def test_unknown_card_role_is_rejected(self):
        cards = self.repo / "cards"
        (cards / "ts").mkdir(parents=True)
        (cards / "01-test.md").write_text("# Test\n")
        for role in ("domian", "", "domain\nCheck as: boundary"):
            with self.subTest(role=role):
                (cards / "ts/01-test.md").write_text(f"Check as: {role}\n```ts\nexport {{}};\n```\n")
                result = self.run_tool("extract_cards.py", cards, self.repo / "out")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("invalid Check as role", result.stderr)

    def install(self, *args, target=None):
        script = ROOT / "skills/ddd-setup/install.sh"
        return subprocess.run(["bash", str(script), *map(str, args)], cwd=target or self.repo, capture_output=True, text=True)

    def test_install_accepts_options_after_the_repository(self):
        repo = self.repo / "target"
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "tsconfig.json").write_text("{}")
        result = self.install(repo, "--model-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("model only", result.stdout)
        self.assertFalse((repo / "docs/ddd/cards").exists())

    def test_install_rejects_unknown_or_conflicting_options(self):
        for args in (["--modelonly"], ["--lang", "python"], ["--lang"], ["--model-only", "--lang", "go"], [".", "other"],
                     ["--lang", "ts", "--lang", "go"], ["--lang", "go,none"]):
            with self.subTest(args=args):
                result = self.install(*args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse((self.repo / "tools/check_model.py").exists())

    def test_install_rejects_a_subdirectory(self):
        sub = self.repo / "sub"
        sub.mkdir()
        result = self.install("--lang", "none", target=sub)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("not the repository root", result.stderr)
        self.assertFalse((sub / "tools").exists())

    def test_install_keeps_last_gitignore_line_intact(self):
        (self.repo / ".gitignore").write_text("node_modules/")
        result = self.install("--lang", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.repo / ".gitignore").read_text(), "node_modules/\n.cards-check/\n")


if __name__ == "__main__":
    unittest.main()
