---
name: IR Product Rules demo-v1
description: Signals and tier rules for Gen Cap, Fund and DI Angel Investment. Tiers express coverage priority and investment potential, not eligibility. Use in the fit-and-tier step.
---

# IR Product Rules (version demo-v1)

## Purpose
The tiers rank who is worth a conversation at the event and why. They measure potential and evidence strength. They do not require proof of capacity, ticket size or a prior commitment. Always evaluate all three products for every person, independently; a person can be Tier A for more than one product.

## Scoring
Score every signal from `evidence_records` as `supported`, `contradicted` or `unknown`. `unknown` never counts against a person.

## Signals per product

### Gen Cap
Core: G1 organisation is a family office, single-family investment vehicle or a founding family's holding; G2 person holds an investment, principal or decision-making role there.
Booster: G3 documented venture or fund activity by that vehicle.
Exclusion: a dated source stating the organisation does not invest in venture or external managers.

### Fund
Core: F1 documented fund commitments, allocator role, or stated interest in fund investing; F2 person or organisation acts as an allocator (family office, foundation, pension, fund-of-funds, HNW investor), not solely an operating-company employee.
Booster: F3 fund commitments in venture specifically.
Exclusion: a dated statement of no fund investing, or a mandate that excludes venture.

### DI Angel Investment
Core: D1 investment potential — any of: documented angel or direct investments; a founder or executive with a documented exit or Series A+ fundraise; a stated intention to angel-invest; membership in an angel syndicate; D2 relevant sector expertise.
Booster: D3 typical ticket ≥ 50,000 EUR when stated with a currency. Unknown ticket is neutral. A stated ticket below 50k lowers the tier by one step but never produces Irrelevant.
Exclusion: a dated statement of not investing directly.

## Tier per product
- Tier A: all core signals `supported`, newest evidence ≤ 24 months old, no exclusion. Boosters strengthen the reasoning but are not required.
- Tier B: all but one core signal `supported`, the remaining one `unknown`; or all core supported but only on evidence older than 24 months.
- Tier C: at least one core signal `supported`, none `contradicted`, the rest `unknown`.
- Needs Review: `identity_review_state = Conflict`, or a signal both `supported` and `contradicted` across sources, or fewer than 2 sourced claims in total.
- Irrelevant: an exclusion `supported` by a dated source. Never from empty results, missing ticket, missing investments or tool failure.

## Derived fields
- `proposed_overall_tier` = highest tier across products (A > B > C > Needs Review > Irrelevant).
- `relevant_products` = products at Tier A, B or C.
- `product_fit_reasons` = one line per product: `Gen Cap: G1=supported (website 2026-01), G2=supported (…), G3=unknown`.
- `data_gaps` = the `unknown` core signals, phrased as questions the DRI can ask.
- `conversation_talking_points` = 2–3 openers tied to supported signals, plus the one question that resolves the highest-value `unknown`.

## Separate concepts, never merged
1. Investment potential (this skill, pre-event).
2. Evidence confidence (`enrichment_status`, source dates).
3. Expressed interest (debrief, per product: Interested / Declined / Not discussed / Unclear).
4. Confirmed commitment (opportunity fields set by humans).

## Hard limits
- Never infer wealth, personality or protected traits.
- Never derive a ticket from employer size, a company's funding round or a job title.
- Thresholds here are the only approved ones; do not invent others.
