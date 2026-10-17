"""Checks that the rule set is total, deterministic and matches the expected demo outcomes.

Run: python3 -I evals/run_evals.py  (from the repo root)
"""
from __future__ import annotations

import itertools
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rules.tier import ProductEvidence, Signal, overall, tier  # noqa: E402
from rules.route import DRI, Entry, route_event  # noqa: E402

RUN = date(2026, 10, 16)
FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


# 1. Totality: every combination of signal states yields exactly one tier, for every product.
states = ["supported", "contradicted", "mixed", "unknown"]
variants = [Signal(s, newest_date=d, external=x, dated=d is not None)
            for s in states for d in (None, date(2026, 1, 1), date(2020, 1, 1)) for x in (False, True)]
count = 0
for product in ("Gen Cap", "Fund", "DI Angel Investment"):
    for c1, c2, b, x in itertools.product(variants, variants, variants[:12], variants[:12]):
        t = tier(ProductEvidence(product, c1, c2, b, x), RUN)
        assert t in ("Tier A", "Tier B", "Tier C", "Needs Review", "Irrelevant")
        count += 1
check("tier function total over signal space", True, f"{count} combinations")

# 2. Tier B and Tier C are disjoint and C is reachable (the demo-v1 defect).
one_core = ProductEvidence("Fund", Signal("supported", date(2026, 3, 1), True, True))
check("one core, no booster → Tier C", tier(one_core, RUN) == "Tier C")
one_core_boost = ProductEvidence("Fund", Signal("supported", date(2026, 3, 1), True, True),
                                 booster=Signal("supported", date(2026, 3, 1), True, True))
check("one core + recent booster → Tier B", tier(one_core_boost, RUN) == "Tier B")
stale = ProductEvidence("Gen Cap", Signal("supported", date(2021, 1, 1), True, True), Signal("supported", date(2021, 1, 1), True, True))
check("both core, stale → Tier B", tier(stale, RUN) == "Tier B")
csv_only = ProductEvidence("Gen Cap", Signal("supported", date(2026, 1, 1), False, True), Signal("supported", date(2026, 1, 1), False, True))
check("both core, pre-enrichment only → Tier B", tier(csv_only, RUN) == "Tier B")
fresh = ProductEvidence("Gen Cap", Signal("supported", date(2026, 1, 1), True, True), Signal("supported", date(2026, 3, 1), False, True))
check("both core, recent + external → Tier A", tier(fresh, RUN) == "Tier A")
contra_dated = ProductEvidence("Gen Cap", Signal("contradicted", date(2026, 1, 1), True, True), Signal("supported", date(2026, 1, 1), True, True))
check("dated contradiction of a core → Irrelevant", tier(contra_dated, RUN) == "Irrelevant")
contra_undated = ProductEvidence("Gen Cap", Signal("contradicted", None, True, False), Signal("supported", date(2026, 1, 1), True, True))
check("undated contradiction of a core → Needs Review", tier(contra_undated, RUN) == "Needs Review")
empty = ProductEvidence("Fund")
check("no evidence → Needs Review (unrated)", tier(empty, RUN) == "Needs Review")
di_small = ProductEvidence("DI Angel Investment", Signal("supported", date(2026, 1, 1), True, True), stated_ticket_eur=20_000)
check("DI one core + ticket 20k → stays Tier C (floor)", tier(di_small, RUN) == "Tier C")
di_small_a = ProductEvidence("DI Angel Investment", Signal("supported", date(2026, 1, 1), True, True), Signal("supported", date(2026, 1, 1), True, True), stated_ticket_eur=20_000)
check("DI Tier A + ticket 20k → Tier B", tier(di_small_a, RUN) == "Tier B")

# 3. Testperson 4 shape: Gen Cap A, DI B, Fund Irrelevant → overall A, ranked Gen Cap first.
tp4 = overall([
    ProductEvidence("Gen Cap", Signal("supported", date(2026, 1, 1), True, True), Signal("supported", date(2026, 2, 1), True, True), Signal("supported", date(2025, 6, 1), True, True)),
    ProductEvidence("DI Angel Investment", Signal("supported", date(2026, 1, 1), True, True)),
    ProductEvidence("Fund", exclusion=Signal("supported", date(2025, 1, 1), True, True)),
], RUN)
check("Testperson 4 → overall Tier A, Gen Cap ranked first", tp4["proposed_overall_tier"] == "Tier A" and tp4["ranked"][0] == "Gen Cap", str(tp4))
check("Testperson 4 DI → Tier C (one core, no booster)", tp4["tiers"]["DI Angel Investment"] == "Tier C", str(tp4["tiers"]))

# 4. Routing
dris = [
    DRI("Testperson 1", frozenset({"DI Angel Investment"}), frozenset({"Deep Tech", "AI", "Quantum", "Defense"}), slack_user_id=None),
    DRI("Testperson 2", frozenset({"Fund"}), frozenset({"ESG", "Sustainability", "Energy", "Climate"}), slack_user_id="U0C9LBXNZSS"),
    DRI("Testperson 3", frozenset({"Gen Cap"}), frozenset({"Consumer"}), slack_user_id="U0C9G3X7ZS7"),
]
entries = [
    Entry("luma-0001", "p4", "Tier A", ("Gen Cap", "DI Angel Investment"), frozenset({"Consumer"})),
    Entry("luma-0004", "p7", "Tier A", ("DI Angel Investment",), frozenset({"Defense"})),
    Entry("luma-0008", "p11", "Tier B", ("DI Angel Investment",), frozenset({"Energy"})),
    Entry("luma-0009", "p12", "Needs Review", (), frozenset()),
    Entry("luma-0012", "anna", "Needs Review", (), frozenset(), identity_conflict=True),
]
r = route_event(entries, dris)
check("Mara without slack_user_id is not eligible → luma-0004 not to Testperson 1", r["luma-0004"].dri_code != "Testperson 1", str(r["luma-0004"]))
check("luma-0004 (DI, Defense, no vertical match) → R4 attendance", r["luma-0004"].reason == "R4 attendance", str(r["luma-0004"]))
check("luma-0008 (DI, Energy) → R3 vertical Energy → Leonie", r["luma-0008"].dri_code == "Testperson 2" and r["luma-0008"].reason.startswith("R3"), str(r["luma-0008"]))
check("luma-0001 → R2 product Gen Cap → Tara", r["luma-0001"].dri_code == "Testperson 3" and r["luma-0001"].reason == "R2 product Gen Cap", str(r["luma-0001"]))
check("unrated → R4 unrated, has a DRI", r["luma-0009"].reason == "R4 unrated" and r["luma-0009"].dri_code is not None, str(r["luma-0009"]))
check("conflict → Unassigned", r["luma-0012"].state == "Unassigned")
r2 = route_event(list(reversed(entries)), dris)
check("determinism: reversed input order → identical assignments", {k: (v.dri_code, v.reason) for k, v in r.items()} == {k: (v.dri_code, v.reason) for k, v in r2.items()})

# R2 iteration: Tara absent → Testperson 4 goes to the DI DRI (when Mara is mapped), not to R3.
dris_mapped = [DRI("Testperson 1", frozenset({"DI Angel Investment"}), frozenset({"AI"}), slack_user_id="U_MARA"),
               DRI("Testperson 2", frozenset({"Fund"}), frozenset({"ESG"}), slack_user_id="U0C9LBXNZSS"),
               DRI("Testperson 3", frozenset({"Gen Cap"}), frozenset({"Consumer"}), slack_user_id="U0C9G3X7ZS7", attending=False)]
r3 = route_event([entries[0]], dris_mapped)
check("R2 iterates to second product when top-product DRI is absent", r3["luma-0001"].dri_code == "Testperson 1" and r3["luma-0001"].reason == "R2 product DI Angel Investment", str(r3["luma-0001"]))

# Capacity: Tara capacity 1, two Gen Cap rows → second goes elsewhere.
dris_cap = [DRI("Testperson 2", frozenset({"Fund"}), frozenset({"ESG"}), slack_user_id="U2"),
            DRI("Testperson 3", frozenset({"Gen Cap"}), frozenset({"Consumer"}), capacity=1, slack_user_id="U3")]
r4 = route_event([Entry("l1", "a", "Tier A", ("Gen Cap",)), Entry("l2", "b", "Tier A", ("Gen Cap",))], dris_cap)
check("capacity 1 → second Gen Cap row not to Tara", r4["l1"].dri_code == "Testperson 3" and r4["l2"].dri_code == "Testperson 2", str(r4))

# No attendee → Escalated
r5 = route_event([entries[0]], [DRI("Testperson 3", frozenset({"Gen Cap"}), frozenset({"Consumer"}), slack_user_id="U3", attending=False)])
check("no attending DRI → Escalated", r5["luma-0001"].state == "Escalated")

print(f"\n{len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
