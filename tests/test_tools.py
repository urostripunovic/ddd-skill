"""Tool regressions: python3 -m unittest discover -s tests -v.

Uses temporary repositories; no installed project or sibling eval is changed.
Language compilation and lint are checked separately with check-cards.sh.
"""
import pathlib
import re
import shutil
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
        (self.repo / "CONTEXT.md").write_text(
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
        self.assertIn("strict scope for PlaceOrder: issued by: customer; matrix column PlaceOrder; examples 2", result.stdout)

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
        self.assertIn("use-case failures OrderNotDraft", line)
        # A primitive already in the starting state is in scope too: the command reads it.
        self.assertIn("primitives Amount, Note", line)

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

    def test_unconfirmed_core_is_rejected(self):
        invariants = ("### Invariants\n| # | Invariant | Enforced by | Commands that could break it |\n|---|---|---|---|\n"
                      "| 1 | {} | decision function PlaceOrder | PlaceOrder |")
        facts = ("### Facts from outside\n| Fact | Used by | Source | Believed when | If not, or no answer | May it be stale? |\n"
                 "|---|---|---|---|---|---|\n| Requester | PlaceOrder | the sign-in token | {} | NotAuthenticated | no |")
        cases = {
            "assumed issuer": MODEL.replace("| PlaceOrder | customer |", "| PlaceOrder | anyone (assumed) |"),
            "placeholder issuer": MODEL.replace("| PlaceOrder | customer |", "| PlaceOrder | TBD |"),
            "question issuer": MODEL.replace("| PlaceOrder | customer |", "| PlaceOrder | ? |"),
            "assumed invariant": MODEL.replace("### Invariants\nNone.", invariants.format("at most 10 orders a day (assumed)")),
            "placeholder invariant": MODEL.replace("### Invariants\nNone.", invariants.format("to be decided")),
            "assumed trust": MODEL.replace("### Facts from outside\nNone.", facts.format("the token signature is checked (assumed)")),
            "placeholder trust": MODEL.replace("### Facts from outside\nNone.", facts.format("TBD")),
        }
        for name, model in cases.items():
            with self.subTest(name=name):
                self.model.write_text(model)
                result = self.run_tool("check-model.sh", self.model)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("is not confirmed", result.stdout)

    def test_guessed_trust_rule_blocks_approval_but_not_an_earlier_one(self):
        facts = ("### Facts from outside\n| Fact | Used by | Source | Believed when | If not, or no answer | May it be stale? |\n"
                 "|---|---|---|---|---|---|\n| Requester | PlaceOrder | the sign-in token | the signature is checked (assumed) | NotAuthenticated | no |")
        self.model.write_text(MODEL.replace("### Facts from outside\nNone.", facts))
        glossary = self.repo / "CONTEXT.md"
        glossary.write_text(glossary.read_text() + "\n**Requester**:\nWho sent the request.\n")
        refused = self.stamp("approve", "Ann")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("'Believed when' is not confirmed", refused.stdout)
        self.assertIn("Status: draft\n", self.model.read_text())
        # A model approved before trust rules joined the core keeps working, with a warning.
        hashed = self.run_tool("model-hash.sh", self.model).stdout.strip()
        self.model.write_text(self.model.read_text().replace("Status: draft", f"Status: approved by Ann on 2026-10-01, model-hash {hashed}"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning:", result.stdout)
        self.assertIn("at the next change", result.stdout)
        # The same for a model written before the template had the column.
        old = MODEL.replace("### Facts from outside\nNone.", "### Facts from outside\n| Fact | Used by | Source | May it be stale? |\n"
                            "|---|---|---|---|\n| Requester | PlaceOrder | the sign-in token | no |")
        self.model.write_text(old)
        self.assertNotEqual(self.stamp("approve", "Ann").returncode, 0)
        hashed = self.run_tool("model-hash.sh", self.model).stdout.strip()
        self.model.write_text(old.replace("Status: draft", f"Status: approved by Ann on 2026-10-01, model-hash {hashed}"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("'Believed when' is missing", result.stdout)

    def test_confirmed_trust_rule_passes(self):
        facts = ("### Facts from outside\n| Fact | Used by | Source | Believed when | If not, or no answer | May it be stale? |\n"
                 "|---|---|---|---|---|---|\n| Requester | PlaceOrder | the sign-in token | signature, issuer, audience and expiry are checked | NotAuthenticated | no |")
        self.model.write_text(MODEL.replace("### Facts from outside\nNone.", facts))
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotIn("Believed when", result.stdout)

    def test_assumed_rest_still_only_warns(self):
        self.model.write_text(MODEL.replace("no: already placed", "no: already placed (assumed)")
                              .replace("| PlaceOrder | customer |", "| PlaceOrder | the customer who opened the order |"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("1 assumption(s)", result.stdout)

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
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards/functional", out)
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
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards/functional", out, lint)
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
        result = self.run_tool("extract_cards.py", KIT / "docs/ddd/cards/functional", self.repo / "examples", lint)
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

    def stamp(self, *args):
        return self.run_tool("stamp-model.sh", args[0], self.model, *args[1:])

    def test_strict_scope_includes_inputs_events_and_existing_values(self):
        model = (MODEL.replace("Depth: standard", "Depth: standard\nStrict commands: PlaceOrder")
                 .replace("## Domain primitives\n\nNone.",
                          "## Domain primitives\n\n| Name | Underlying type | Rules | Why | Sensitive? |\n|---|---|---|---|---|\n"
                          "| Amount | integer | 1..100 | cap | no |\n| Coupon | string | 1..20 | codes | no |")
                 .replace("DraftOrder = {}", "DraftOrder = { amount: Amount }")
                 .replace("PlacedOrder = {}", "PlacedOrder = { amount: Amount }")
                 .replace("PlaceOrder : DraftOrder -> PlacedOrder", "PlaceOrder : DraftOrder -> PlacedOrder + [OrderPlaced]")
                 .replace("| Command | Issued by | Notes |\n|---|---|---|\n| StartOrder | customer | |\n| PlaceOrder | customer | |",
                          "| Command | Issued by | Input | Notes |\n|---|---|---|---|\n| StartOrder | customer | none | |\n"
                          "| PlaceOrder | customer | coupon: Coupon | |")
                 .replace("### Events\nNone.", "### Events\n| Event | Carries | Consumed by |\n|---|---|---|\n| OrderPlaced | id | Billing |"))
        self.model.write_text(model)
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        line = next(l for l in result.stdout.splitlines() if "strict scope for PlaceOrder" in l)
        self.assertIn("events OrderPlaced", line)
        self.assertIn("primitives Amount, Coupon", line)
        self.model.write_text(model.replace("coupon: Coupon", "coupon: Voucher"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("takes Voucher, which is neither a primitive nor a defined type", result.stdout)

    def test_approvers_line_limits_who_may_approve(self):
        (self.repo / "CLAUDE.md").write_text("## Domain code\n\nApprovers: Ann, Bo\n")
        self.model.write_text(MODEL)
        refused = self.stamp("approve", "Mallory")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("not on the Approvers line", refused.stderr + refused.stdout)
        self.assertIn("Status: draft\n", self.model.read_text())
        approved = self.stamp("approve", "ann")
        self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
        self.assertIn("Status: approved by ann on", self.model.read_text())

    def test_status_line_in_the_older_form_still_reads(self):
        # Models stamped before the hashes moved into a comment keep their approval, and a new stamp shortens the line.
        hashed = self.run_tool("model-hash.sh", self.model).stdout.strip()
        self.model.write_text(MODEL.replace("Status: draft", f"Status: approved by Ann on 2026-10-01, model-hash {hashed}"))
        self.assertEqual(self.run_tool("check-model.sh", self.model).returncode, 0)
        self.assertEqual(self.stamp("review").returncode, 0)
        self.assertRegex(self.model.read_text(), rf"Status: approved by Ann on 2026-10-01, reviewed \S+ <!-- model-hash {hashed}, reviewed at {hashed} -->\n")
        self.assertEqual(self.run_tool("check-model.sh", self.model).returncode, 0)
        self.model.write_text(self.model.read_text().replace("already placed", "placing is final"))
        self.assertIn("edited after approval", self.run_tool("check-model.sh", self.model).stdout)

    def test_approved_without_hash_is_an_error(self):
        self.model.write_text(MODEL.replace("Status: draft", "Status: approved by test on 2026-10-06"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approved without a model-hash", result.stdout)

    def test_strict_approval_needs_a_current_review(self):
        self.model.write_text(MODEL.replace("Depth: standard", "Depth: strict"))
        refused = self.stamp("approve", "Ann")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("without a review", refused.stdout)
        self.assertIn("Status: draft\n", self.model.read_text())
        self.assertEqual(self.stamp("review").returncode, 0)
        approved = self.stamp("approve", "Ann")
        self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
        self.assertRegex(self.model.read_text(), r"Status: approved by Ann on \S+, reviewed \S+ <!-- model-hash [0-9a-f]+, reviewed at [0-9a-f]+ -->\n")
        self.model.write_text(self.model.read_text().replace("already placed", "placing is final"))
        self.assertEqual(self.stamp("draft").returncode, 0)
        self.assertRegex(self.model.read_text(), r"Status: draft, reviewed \S+ <!-- reviewed at [0-9a-f]+ -->\n")
        draft = self.run_tool("check-model.sh", self.model)
        self.assertIn("the model has changed since", draft.stdout)
        refused = self.stamp("approve", "Ann")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("the review is of model-hash", refused.stdout)

    def test_strict_approval_refuses_what_is_not_confirmed(self):
        cases = {
            "(assumed) marker": MODEL.replace("no: already placed", "no: already placed (assumed)"),
            "open questions": MODEL.replace("## Open questions\nNone.", "## Open questions\n- Can a customer place twice?"),
            "amendment row": MODEL + "\n## Amendments\n\n| Date | Section | The model said | What was learned, and what the code does |\n"
                                     "|---|---|---|---|\n| 2026-10-06 | Examples | nothing | a rule |\n",
        }
        for name, model in cases.items():
            with self.subTest(name=name):
                self.model.write_text(model.replace("Depth: standard", "Depth: strict"))
                self.stamp("review")
                result = self.stamp("approve", "Ann")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("strict depth", result.stdout)

    def test_strict_scope_in_a_standard_context_must_be_confirmed(self):
        base = MODEL.replace("Depth: standard", "Depth: standard\nStrict commands: PlaceOrder")
        self.model.write_text(base)
        self.assertNotEqual(self.stamp("approve", "Ann").returncode, 0)
        cases = {
            "assumed": base.replace("no: already placed", "no: already placed (assumed)"),
            "amendment": base + "\n## Amendments\n\n| Date | Section | The model said | What was learned, and what the code does |\n"
                                "|---|---|---|---|\n| 2026-10-06 | Commands | PlaceOrder by anyone | only staff |\n",
        }
        for name, model in cases.items():
            with self.subTest(name=name):
                self.model.write_text(model)
                self.stamp("review")
                result = self.stamp("approve", "Ann")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("strict scope of PlaceOrder", result.stdout)
        self.model.write_text(base)
        self.stamp("review")
        result = self.stamp("approve", "Ann")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pending_is_outside_the_hash(self):
        before = self.hash_model()
        pending = "\n## Pending\n\n| Date | Command | The gap, and the question for the user | Found while |\n|---|---|---|---|\n| 2026-10-06 | PlaceOrder | rounding? | example 2 |\n"
        self.model.write_text(MODEL + pending)
        self.assertEqual(self.hash_model(), before)
        self.model.write_text(MODEL.replace("Status: draft", f"Status: approved by test, model-hash {before}") + pending)
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("1 gap(s) under Pending", result.stdout)

    def test_domain_paths_must_hold_code_and_be_linted(self):
        (self.repo / "internal/ordering").mkdir(parents=True)
        (self.repo / "internal/ordering/order.go").write_text("package ordering\n")
        (self.repo / "internal/empty").mkdir(parents=True)
        config = self.repo / ".golangci.yml"
        cases = [
            ("Domain paths: internal/ordering", '- "**/internal/ordering/**"\n', False),
            ("Domain paths: internal/ordering", '- "**/internal/ordering/**"\n- path-except: internal/ordering/\n', True),
            ("Domain paths: internal/empty", "internal/empty internal/empty\n", False),
            ("Domain paths: none", "", True),
            ("No paths recorded", "", False),
        ]
        for line, lint, passes in cases:
            with self.subTest(line=line, lint=lint):
                (self.repo / "CLAUDE.md").write_text(f"## Domain code\n\n{line}\n")
                config.write_text(lint)
                result = self.run_tool("check-domain-paths.sh")
                self.assertEqual(result.returncode == 0, passes, result.stdout + result.stderr)

    def status(self):
        result = self.run_tool("ddd-status.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_status_before_setup(self):
        self.model.unlink()
        self.model.parent.rmdir()
        (self.repo / "docs/domain").rmdir()
        self.assertIn("setup: not done", self.status())

    def test_status_matches_tests_to_example_rows(self):
        test = self.repo / "internal/ordering/order_test.go"
        test.parent.mkdir(parents=True)
        test.write_text('func TestExample1StartOrder(t *testing.T) {}\n')
        out = self.status()
        self.assertIn("examples: 2 rows; with a test: 1; without: 2 (commands: PlaceOrder)", out)
        test.write_text('func TestExamples1And2(t *testing.T) {}\n')
        self.assertIn("examples: 2 rows; with a test: 1-2\n", self.status())

    def test_status_leaves_no_files_behind(self):
        # The status script imports check_model; in an installed repository, a __pycache__ beside it is an untracked change.
        tools = self.repo / "tools"
        shutil.copytree(TOOLS, tools, ignore=shutil.ignore_patterns("__pycache__"))
        result = subprocess.run([str(tools / "ddd-status.sh")], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((tools / "__pycache__").exists())

    def test_status_reports_model_state_and_next_migration_step(self):
        self.model.write_text(MODEL.replace("## Open questions\nNone.", "## Open questions\n- Who may cancel?\n- Is there a limit?")
                              + "\n## Migration\n\n1. Pin current behaviour. (done 2026-10-01)\n2. Introduce OrderId.\n")
        out = self.status()
        self.assertIn("status: draft", out)
        self.assertIn("depth: standard", out)
        self.assertIn("open questions: 2", out)
        self.assertIn("migration: 1 of 2 steps done; next: step 2: Introduce OrderId.", out)

    def test_glossary_under_its_earlier_name_still_reads_with_a_warning(self):
        # Earlier versions wrote GLOSSARY.md; an approved model there keeps passing, and the status names the rename.
        (self.repo / "CONTEXT.md").rename(self.repo / "GLOSSARY.md")
        # The kit's own context map must not pass for CONTEXT-MAP.md on a case-insensitive file system.
        (self.repo / "docs/domain/context-map.md").write_text("# Context map\n")
        self.model.write_text(MODEL.replace("Status: draft", f"Status: approved by test, model-hash {self.hash_model()}"))
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("warning: GLOSSARY.md is the glossary's earlier name; rename it to CONTEXT.md", result.stdout)
        self.assertIn("glossary: earlier name, GLOSSARY.md; it belongs in CONTEXT.md", self.status())
        (self.repo / "GLOSSARY.md").rename(self.repo / "CONTEXT.md")
        result = self.run_tool("check-model.sh", self.model)
        self.assertNotIn("warning", result.stdout)
        self.assertIn("glossary: CONTEXT.md\n", self.status())

    def test_glossary_per_context_through_a_context_map(self):
        glossary = self.repo / "src/ordering/CONTEXT.md"
        glossary.parent.mkdir(parents=True)
        (self.repo / "CONTEXT.md").rename(glossary)
        (self.repo / "CONTEXT-MAP.md").write_text("# Context Map\n\n- [Ordering](./src/ordering/CONTEXT.md): takes orders\n")
        result = self.run_tool("check-model.sh", self.model)
        self.assertEqual(result.returncode, 0, result.stdout)
        (self.repo / "CONTEXT-MAP.md").write_text("# Context Map\n\n- [Billing](./src/billing/CONTEXT.md): bills\n")
        result = self.run_tool("check-model.sh", self.model)
        self.assertIn("no glossary found: expected CONTEXT.md", result.stdout)

    def test_status_reports_edit_after_approval(self):
        self.model.write_text(MODEL.replace("Status: draft", f"Status: approved by test, model-hash {self.hash_model()}")
                              .replace("already placed", "placing is final"))
        self.assertIn("edited after approval, so it needs approving again", self.status())

    def test_status_ties_tests_to_contexts_when_there_are_several(self):
        (self.repo / "docs/domain/contexts/billing.md").write_text(MODEL.replace("Context: Ordering", "Context: Billing"))
        for path, text in [("src/ordering/order.test.ts", 'test("example 2: placing", () => {})'),
                           ("test/misc.test.ts", 'test("example 1", () => {})'),
                           ("test/billing.test.ts", '// docs/domain/contexts/billing.md\ntest("example 1", () => {})')]:
            (self.repo / path).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / path).write_text(text)
        out = self.status()
        billing, ordering = out.split("context billing")[1].split("context ordering")
        self.assertIn("with a test: 1;", billing)
        self.assertIn("with a test: 2;", ordering)
        self.assertIn("tied to no context: test/misc.test.ts", out)

    def install(self, *args, target=None):
        script = ROOT / "skills/ddd-setup/install.sh"
        return subprocess.run(["bash", str(script), *map(str, args)], cwd=target or self.repo, capture_output=True, text=True)

    def test_install_puts_cards_in_their_style_and_strategic_cards_everywhere(self):
        for args, cards in ((["--lang", "ts"], True), (["--model-only"], False)):
            with self.subTest(args=args):
                repo = self.repo / args[-1].strip("-")
                subprocess.run(["git", "init", "-q", str(repo)], check=True)
                result = self.install(*args, target=repo)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((repo / "docs/ddd/strategic/06-anticorruption-layer.md").exists())
                self.assertEqual((repo / "docs/ddd/cards/functional/ts/03-states-as-types.md").exists(), cards)
                self.assertEqual((repo / "docs/ddd/cards/README.md").exists(), cards)
                self.assertFalse((repo / "docs/ddd/cards/functional/go").exists())

    def test_install_reports_the_earlier_card_layout(self):
        old = self.repo / "docs/ddd/cards/03-states-as-types.md"
        old.parent.mkdir(parents=True)
        old.write_text("# States as types\n\n## Corrections\n\n- 2026-01-01: a team correction\n")
        result = self.install("--lang", "none")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("earlier card layout", result.stdout)
        self.assertIn("a team correction", old.read_text())
        self.assertIn("cards: earlier layout", self.status())

    def test_status_names_the_installed_style(self):
        self.install("--lang", "ts")
        out = self.status()
        self.assertIn("cards: functional, examples for ts", out)
        self.assertNotIn("strategic cards: not installed", out)

    def test_relative_links_in_the_kit_and_skills_resolve(self):
        broken = []
        for doc in [*KIT.rglob("*.md"), *(ROOT / "skills").rglob("*.md"), ROOT / "README.md", ROOT / "REFERENCE.md"]:
            # Links inside code and comments are examples of what a user writes, not links of the kit.
            text = re.sub(r"```.*?```|<!--.*?-->|`[^`\n]*`", "", doc.read_text(), flags=re.S)
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
                if "://" not in target and not (doc.parent / target).exists():
                    broken.append(f"{doc.relative_to(ROOT)}: {target}")
        self.assertEqual(broken, [])

    def test_glossary_has_one_name(self):
        # The glossary is CONTEXT.md, the name Matt Pocock's skills read. GLOSSARY.md is named only where an earlier repository is upgraded.
        allowed = {"skills/ddd-setup/SKILL.md", "skills/ddd-setup/UPGRADING.md", "REFERENCE.md",
                   "skills/ddd-setup/kit/tools/check_model.py", "skills/ddd-setup/kit/tools/ddd_status.py"}
        tracked = subprocess.run(["git", "ls-files", "skills", "evals", "README.md", "REFERENCE.md"], cwd=ROOT,
                                 capture_output=True, text=True, check=True).stdout.split()
        found = {n for n in tracked if not n.startswith("evals/results/") and "GLOSSARY" in (ROOT / n).read_text(errors="ignore")}
        self.assertEqual(sorted(found - allowed), [], "the glossary is CONTEXT.md")

    def test_domain_decisions_and_adrs_have_one_split(self):
        # Domain decisions are Decisions rows under the approval hash; technical ones are ADRs. Both places say so.
        modelling = next(l for l in (ROOT / "skills/ddd-modelling/SKILL.md").read_text().splitlines() if l.startswith("- **Decisions**"))
        reference = next(l for l in (ROOT / "REFERENCE.md").read_text().splitlines() if "Domain decisions go in" in l)
        for line in (modelling, reference):
            self.assertIn("`docs/adr/`", line)
            self.assertRegex(line, r"approv(al hash|ing again)")

    def test_review_routing_with_code_review_is_the_same_everywhere(self):
        # Domain code goes to ddd-review-all, and it takes the place of Matt Pocock's implement -> /code-review step.
        for path in ("skills/ddd-review-all/SKILL.md", "skills/ddd-implementation/SKILL.md", "REFERENCE.md"):
            text = (ROOT / path).read_text()
            self.assertIn("takes the place of its `/code-review` step", text, path)

    def test_lifecycle_word_counts_match_the_files(self):
        # Counted as wc -w counts: runs of non-whitespace. Every rule file is listed.
        lifecycle = ROOT / "skills/ddd-modelling/lifecycle"
        listed = dict(re.findall(r"\]\(([\w-]+\.md)\) \| (\d+) \|", (lifecycle / "README.md").read_text()))
        actual = {f.name: str(len(f.read_text().split())) for f in lifecycle.glob("*.md") if f.name != "README.md"}
        self.assertEqual(listed, actual, "update the Words column in skills/ddd-modelling/lifecycle/README.md")

    def test_standard_review_names_sections_that_exist(self):
        # ddd-review-all's standard review applies named sections of secure-by-design-review; a renamed heading would silently drop one.
        review_all = (ROOT / "skills/ddd-review-all/SKILL.md").read_text()
        headings = set(re.findall(r"^### (.+)$", (ROOT / "skills/secure-by-design-review/SKILL.md").read_text(), re.M))
        line = next(l for l in review_all.splitlines() if l.startswith("Otherwise run the **standard** review"))
        named = re.findall(r"\*\*([^*]+)\*\*", line.split("applies three sections", 1)[1])
        self.assertEqual(len(named), 3, line)
        self.assertEqual([n for n in named if n not in headings], [], "a section the standard review names is not a heading in secure-by-design-review")
        prompt = next(l for l in review_all.splitlines() if l.startswith("- for the standard review:"))
        self.assertEqual(re.findall(r"\*\*([^*]+)\*\*", prompt), named, "the 1b list and the sub-agent prompt name different sections")

    def test_every_list_of_the_core_names_the_same_items(self):
        # depth.md defines the core. The safety rules repeat it inline on purpose, so a test keeps the copies together.
        items = {"states": r"\bstates?\b", "commands": r"\bcommands?\b", "who may issue": r"who may issue",
                 "trust": r"\btrusted\b", "invariants": r"\binvariants?\b", "aggregate boundaries": r"aggregate boundar",
                 "glossary": r"glossary|\bterms\b"}
        definition = set(items)
        stop = {"states", "commands", "who may issue", "trust", "invariants"}
        places = [
            ("skills/ddd-modelling/lifecycle/depth.md", "The **core** is", definition),
            ("skills/ddd-modelling/SKILL.md", "- Never mark the core (", definition),
            ("REFERENCE.md", "You confirm the **core**", definition),
            ("skills/ddd-modelling/lifecycle/gaps.md", "- **A gap in the core**", stop | {"aggregate boundaries"}),
            ("skills/ddd-implementation/SKILL.md", "- When the model is missing", stop),
            ("skills/ddd-model-review/SKILL.md", "- **A blocker is one of three things**", stop),
        ]
        missing = []
        for path, marker, required in places:
            line = next((l for l in (ROOT / path).read_text().splitlines() if marker in l), None)
            self.assertIsNotNone(line, f"{path}: no line with {marker!r}")
            missing += [f"{path}: {name}" for name in sorted(required) if not re.search(items[name], line, re.I)]
        self.assertEqual(missing, [], "the core is defined in depth.md; make these lists name the same items")

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
