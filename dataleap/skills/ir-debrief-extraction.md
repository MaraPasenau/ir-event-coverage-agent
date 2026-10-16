---
name: IR Debrief Extraction
description: How to turn a DRI's post-conversation note (text or confirmed transcript) into a structured proposal draft. Use in the debrief step.
---

# IR Debrief Extraction

## Input
`post_event_note`: the raw text reply in the briefing thread, or the transcript confirmed by the DRI. Never extract from an unconfirmed transcript.

## Output schema (agent DB table `proposals`, status `draft`)
```
{
  coverage_entry_id,
  products: [ { product: Fund | DI Angel Investment | Gen Cap,
                polarity: interested | declined | not_mentioned } ],
  investing_context: personal | organisation | unknown,
  ticket: { min, max, currency } | null,
  timing: text | null,
  concerns: [text],
  requested_materials: [text],
  next_step: text | null,
  owner: dri_code | null,
  source_message_ts
}
```

## Rules
- A typical or usual ticket ("usually does 100k") is `ticket`, not a commitment. Never write `final_commitment_amount`.
- "No interest in funds", "not doing funds", "only direct" → Fund `declined`.
- No number plus currency → `ticket = null`. Never estimate.
- A product not mentioned stays `not_mentioned`; it is not `declined`.
- Investing context: personal if the DRI reports the person investing their own money; organisation if on behalf of a family office, fund or company; else unknown.
- Ambiguous attendee (name matches more than one entry in the event) → ask once in the thread which one, then continue.
- `conversation_outcome` mapping: no conversation happened → No Conversation; explicit no → No Fit; vague or "later" → Nurture; concrete interest without commitment → Potential Investor; explicit interest with a stated next step → Interest Confirmed.

## Conversation note (always, before any proposal)
Every debrief produces one Attio note on the Person (see IR Attio Contract, Notes), regardless of outcome or later approval. Body fields: event, coverage DRI, conversation date, source (text | voice, message ts), summary (2–3 sentences), topics, interest per product (Interested | Declined | Not discussed | Unclear), ticket indication with currency or "not stated", next step, follow-up owner. The raw text or confirmed transcript is appended verbatim. A rejected proposal never removes this note.

## Ticket vs commitment
- A typical or usual ticket → coverage `ticket_size_indication` + `ticket_currency_code` only.
- `expected_commitment_min/max` + `currency_code` on an opportunity only when the DRI reports an amount the person said they would consider for this specific product.

## Proposal construction (consumed by step 6.8)
Produce a numbered change list, each item `object create|update {field: value, …}`. Cases:

A. At least one product `interested`:
1. Investor entity: create if absent (lookup by `integration_key`, then name), else reference.
2. Opportunity: one per product with polarity `interested`, `route` = that product. If an open opportunity exists for the same `investor_entity` + `route`, propose an update instead.
3. Coverage entry: `selected_product` (the product with the strongest evidence), `conversation_outcome`.
4. Task: one per opportunity, content from `next_step`, assignee = owner, deadline from `timing`; if timing is vague ("next week"), resolve as the next Monday plus 7 days and state the rule in the proposal.

B. No product `interested` but a concrete `next_step`:
1. Coverage entry: `conversation_outcome`.
2. Task: linked to the Person, content from `next_step`, same deadline rule.

C. No interest, no next step: coverage `conversation_outcome` only. No proposal message; post "Note saved, no CRM changes proposed." in the thread.

End A and B with: "React :+1: to approve or :-1: to reject."
