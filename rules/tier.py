"""Reference implementation of IR Product Rules demo-v2 (dataleap/skills/ir-product-rules.md).

The Dataleap agent applies the skill text; this module exists to prove the tier function is
total and deterministic and to check the agent's output (T17). Pure functions, no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Literal, Optional

RULES_VERSION = "demo-v2"
State = Literal["supported", "contradicted", "mixed", "unknown"]
Tier = Literal["Tier A", "Tier B", "Tier C", "Needs Review", "Irrelevant"]

TIER_ORDER: dict[str, int] = {"Tier A": 4, "Tier B": 3, "Tier C": 2, "Needs Review": 1, "Irrelevant": 0}
PRODUCT_PRECEDENCE: dict[str, int] = {"Gen Cap": 2, "DI Angel Investment": 1, "Fund": 0}
RECENT_MONTHS = 24
DI_TICKET_FLOOR_EUR = 50_000


@dataclass(frozen=True)
class Signal:
    state: State = "unknown"
    newest_date: Optional[date] = None   # max source_date of supporting (or contradicting) claims
    external: bool = False               # any supporting claim not tagged pre-enrichment
    dated: bool = False                  # any claim addressing this signal carries a date

    def recent(self, run_date: date) -> bool:
        if self.newest_date is None:
            return False
        months = (run_date.year - self.newest_date.year) * 12 + (run_date.month - self.newest_date.month)
        if run_date.day < self.newest_date.day:
            months -= 1
        return months <= RECENT_MONTHS


@dataclass(frozen=True)
class ProductEvidence:
    product: str
    c1: Signal = Signal()
    c2: Signal = Signal()
    booster: Signal = Signal()
    exclusion: Signal = Signal()
    stated_ticket_eur: Optional[int] = None  # DI only; None = unknown


def tier(ev: ProductEvidence, run_date: date, identity_conflict: bool = False) -> Tier:
    """Tier function, lines 1–6 of the skill, then the DI modifier."""
    sigs = (ev.c1, ev.c2, ev.booster, ev.exclusion)
    cores = (ev.c1, ev.c2)

    # 1. Needs Review
    if identity_conflict or any(s.state == "mixed" for s in sigs):
        return "Needs Review"
    if any(s.state == "contradicted" and not s.dated for s in cores):
        return "Needs Review"
    # 2. Irrelevant
    if ev.exclusion.state == "supported" and ev.exclusion.dated:
        return "Irrelevant"
    if any(s.state == "contradicted" and s.dated for s in cores):
        return "Irrelevant"

    supported = [s for s in cores if s.state == "supported"]
    n = len(supported)
    result: Tier
    # 3. Tier A
    if n == 2 and any(s.recent(run_date) for s in cores) and any(s.external for s in cores):
        result = "Tier A"
    # 4. Tier B
    elif n == 2:
        result = "Tier B"
    elif n == 1 and ev.booster.state == "supported" and ev.booster.recent(run_date):
        result = "Tier B"
    # 5. Tier C
    elif n == 1:
        result = "Tier C"
    # 6. no core supported
    else:
        result = "Needs Review"

    # DI modifier: stated ticket below floor lowers one step, floor Tier C
    if ev.product == "DI Angel Investment" and ev.stated_ticket_eur is not None \
            and ev.stated_ticket_eur < DI_TICKET_FLOOR_EUR and result in ("Tier A", "Tier B"):
        result = "Tier B" if result == "Tier A" else "Tier C"
    return result


def supported_count(ev: ProductEvidence) -> int:
    return sum(1 for s in (ev.c1, ev.c2, ev.booster) if s.state == "supported")


def rank_products(items: Iterable[tuple[ProductEvidence, Tier]]) -> list[tuple[ProductEvidence, Tier]]:
    """rank_products(): tier, then supported signal count, then Gen Cap > DI > Fund."""
    return sorted(
        items,
        key=lambda it: (TIER_ORDER[it[1]], supported_count(it[0]), PRODUCT_PRECEDENCE[it[0].product]),
        reverse=True,
    )


def overall(evs: list[ProductEvidence], run_date: date, identity_conflict: bool = False) -> dict:
    tiered = [(ev, tier(ev, run_date, identity_conflict)) for ev in evs]
    ranked = rank_products(tiered)
    return {
        "rules_version": RULES_VERSION,
        "tiers": {ev.product: t for ev, t in tiered},
        "proposed_overall_tier": ranked[0][1],
        "relevant_products": [ev.product for ev, t in ranked if t in ("Tier A", "Tier B", "Tier C")],
        "ranked": [ev.product for ev, _ in ranked],
    }
