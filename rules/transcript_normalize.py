"""Deterministic post-ASR normalization for debrief transcripts (IR Debrief Extraction, Transcript correction).

Replaces tokens that do not match any known word but are phonetically or lexically close to a glossary
term (products, fixed terms) or to an attendee / DRI name supplied by the caller. Returns the corrected
text and the list of substitutions so the Slack message can show "Changed: a → b".

Usage: normalize(text, names=["Testperson 4", "Anna Müller"]) -> (corrected_text, changes)
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

try:
    from rapidfuzz import fuzz
    import jellyfish
except ImportError as e:  # pragma: no cover
    raise SystemExit("pip install rapidfuzz jellyfish") from e

GLOSSARY = json.loads((Path(__file__).parent / "glossary.json").read_text())
FUZZ_MIN = 80          # rapidfuzz ratio 0–100
MAX_NGRAM = 3
MIN_FUZZY_LEN = 4      # tokens shorter than this are only matched exactly
METAPHONE_MIN_LEN = 5  # phonetic matching needs at least this many letters
STOP = set("""und oder aber mit ohne für von vor nach bei zu zum zur in im am an auf aus das der die den dem des ein eine einen
einem einer ist sind war hat haben wir ihr sie er es ich du man nicht noch auch mal dann wenn weil dass was wie wo
the and or but with without for of from to at in on by a an is are was has have we you they he she it not also then if because
that what how where will would could should ähm äh hm genau also so ja nein ok okay kein keine keinen keiner no never nie none""".split())


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.casefold().replace("-", " ").replace("'", "")
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _candidates(names: list[str]) -> dict[str, str]:
    """alias (normalized) -> canonical"""
    out: dict[str, str] = {}
    for group in ("products", "terms"):
        for canon, aliases in GLOSSARY[group].items():
            out[_norm(canon)] = canon
            for a in aliases:
                out[_norm(a)] = canon
    for n in names:
        out[_norm(n)] = n          # full names only; partial names are left to the LLM resolver
    return out


def _match(span: str, cands: dict[str, str]) -> str | None:
    key = _norm(span)
    if not key or key.isdigit():
        return None
    if key in cands:
        return cands[key]
    words = key.split()
    if any(w in STOP for w in words) or len(key.replace(" ", "")) < MIN_FUZZY_LEN:
        return None
    best, best_score = None, 0.0
    span_m = jellyfish.metaphone(key)
    for alias, canon in cands.items():
        if len(alias.split()) != len(words):
            continue
        score = fuzz.ratio(key, alias)
        # phonetic shortcut only for longer spans and only when the spelling is not far off:
        # "take" and "deck" share a metaphone but are different words
        if span_m and len(key.replace(" ", "")) >= METAPHONE_MIN_LEN and score >= 60 and span_m == jellyfish.metaphone(alias):
            score = max(score, 88)
        if score > best_score:
            best, best_score = canon, score
    return best if best_score >= FUZZ_MIN else None


def normalize(text: str, names: list[str] | None = None) -> tuple[str, list[tuple[str, str]]]:
    cands = _candidates(names or [])
    canon_norms = {_norm(c) for c in cands.values()}
    tokens = re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text, flags=re.UNICODE)
    out: list[str] = []
    changes: list[tuple[str, str]] = []
    i = 0
    while i < len(tokens):
        hit = None
        for n in range(min(MAX_NGRAM, len(tokens) - i), 0, -1):
            span_tokens = tokens[i:i + n]
            if any(not re.match(r"\w", t) for t in span_tokens):
                continue
            span = " ".join(span_tokens)
            if _norm(span) in canon_norms:          # already canonical
                hit = (span, span, n)
                break
            m = _match(span, cands)
            if m:
                hit = (span, m, n)
                break
        if hit:
            span, canon, n = hit
            if _norm(span) == _norm(canon):
                out.append(span)            # keep the speaker's surface form
            else:
                changes.append((span, canon))
                out.append(canon)
            i += n
        else:
            out.append(tokens[i])
            i += 1
    # collapse a canonical term that was produced twice in a row ("DI" + "DI co-invest")
    dedup: list[str] = []
    for t in out:
        if dedup and t == dedup[-1] and _norm(t) in canon_norms:
            continue
        dedup.append(t)
    corrected = re.sub(r"\s+([.,;:!?])", r"\1", " ".join(dedup))
    return corrected, changes


if __name__ == "__main__":
    sample = ("Ähm. Ich habe mit Testperson 4 gesprochen, sehr interessiert. Jinka will nächste Woche einen "
              "Intro-Call machen und, ähm, genau, Fun-Themen haben wir derweil nicht besprochen.")
    txt, ch = normalize(sample, names=["Testperson 4"])
    print(txt)
    print("Changed:", ", ".join(f"{a} → {b}" for a, b in ch))
