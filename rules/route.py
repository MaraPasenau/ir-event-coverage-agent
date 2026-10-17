"""Reference implementation of IR DRI Routing (dataleap/skills/ir-dri-routing.md).

Pure function: same input, same assignment. Used to prove determinism and the R2 iteration
over rank_products(); the Dataleap agent applies the skill text.
"""
from __future__ import annotations

from dataclasses import dataclass, field

VERTICAL_MAP = {"Deep Tech": "Industrial Tech", "Quantum": "AI", "Sustainability": "ESG"}
IGNORED_VERTICALS = {"Other", "Unknown"}
TIER_SORT = {"Tier A": 0, "Tier B": 1, "Tier C": 2, "Needs Review": 3}


@dataclass(frozen=True)
class DRI:
    dri_code: str
    product_focus: frozenset[str]
    vertical_expertise: frozenset[str]
    capacity: int = 10
    slack_user_id: str | None = None
    profile_status: str = "Confirmed"
    attending: bool = True
    relationship_people: frozenset[str] = frozenset()

    def eligible(self) -> bool:
        return (self.profile_status == "Confirmed" and bool(self.product_focus)
                and bool(self.vertical_expertise) and bool(self.slack_user_id))

    def mapped_verticals(self) -> frozenset[str]:
        return frozenset(VERTICAL_MAP.get(v, v) for v in self.vertical_expertise) - IGNORED_VERTICALS


@dataclass(frozen=True)
class Entry:
    luma_attendee_id: str
    person_id: str
    overall_tier: str                 # Tier A/B/C/Needs Review/Irrelevant
    ranked_products: tuple[str, ...]  # relevant products in rank_products() order
    preferred_verticals: frozenset[str] = frozenset()
    identity_conflict: bool = False
    assignment_state: str = "Unassigned"


@dataclass
class Assignment:
    dri_code: str | None
    state: str
    reason: str
    candidates: tuple[str, ...] = ()


def _overlap(entry: Entry, dri: DRI) -> int:
    return len((entry.preferred_verticals - IGNORED_VERTICALS) & dri.mapped_verticals())


def route_event(entries: list[Entry], dris: list[DRI], existing_counts: dict[str, int] | None = None) -> dict[str, Assignment]:
    counts: dict[str, int] = dict(existing_counts or {})
    eligible = sorted((d for d in dris if d.eligible()), key=lambda d: d.dri_code)
    out: dict[str, Assignment] = {}

    order = sorted(entries, key=lambda e: (TIER_SORT.get(e.overall_tier, 9), e.luma_attendee_id))
    for e in order:
        if e.assignment_state == "Confirmed":
            continue
        if e.identity_conflict or e.overall_tier == "Irrelevant":
            out[e.luma_attendee_id] = Assignment(None, "Unassigned", "not routable")
            continue

        def candidates() -> list[DRI]:
            return [d for d in eligible if d.attending and counts.get(d.dri_code, 0) < d.capacity]

        def pick(cands: list[DRI]) -> DRI:
            return sorted(cands, key=lambda d: (counts.get(d.dri_code, 0), -_overlap(e, d), d.dri_code))[0]

        cands = candidates()
        if not cands:
            out[e.luma_attendee_id] = Assignment(None, "Escalated", "R4 no attendee", tuple(d.dri_code for d in eligible))
            continue

        chosen: DRI | None = None
        reason = ""
        if e.overall_tier in ("Tier A", "Tier B", "Tier C"):
            r1 = [d for d in cands if e.person_id in d.relationship_people]
            if r1:
                chosen, reason = pick(r1), "R1 relationship"
            if chosen is None:
                for product in e.ranked_products:
                    r2 = [d for d in cands if product in d.product_focus]
                    if r2:
                        chosen, reason = pick(r2), f"R2 product {product}"
                        break
            if chosen is None:
                r3 = [d for d in cands if _overlap(e, d) >= 1]
                if r3:
                    chosen = pick(r3)
                    reason = "R3 vertical " + ",".join(sorted((e.preferred_verticals - IGNORED_VERTICALS) & chosen.mapped_verticals()))
            if chosen is None:
                chosen, reason = pick(cands), "R4 attendance"
        else:  # Needs Review without conflict → unrated, R4 only
            chosen, reason = pick(cands), "R4 unrated"

        counts[chosen.dri_code] = counts.get(chosen.dri_code, 0) + 1
        out[e.luma_attendee_id] = Assignment(chosen.dri_code, "Suggested", reason)
    return out
