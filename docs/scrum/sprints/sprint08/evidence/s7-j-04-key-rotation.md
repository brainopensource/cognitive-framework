# S7-J-04 — Leaked OpenRouter key: exposure and rotation

**Date:** 2026-08-17 · **Status:** `[TODO]` — **blocked on the CTO, not on engineering**
**No secret value appears in this file, and none will.**

## The one thing that must happen first

**Rotate the key in the OpenRouter dashboard: revoke the old key, issue a new one.**

I cannot do this and will not attempt to. It requires authenticated access to the OpenRouter
account console. That is the CTO's action. Everything else on this page is secondary — a history
rewrite on an unrotated key buys nothing, because the key is already disclosed to anyone who cloned
the repository at any point.

**Order matters and is not negotiable:** revoke → reissue → update local `.env` → *then*
consider the history rewrite. Rewriting first leaves a live credential in circulation while
consuming the evidence of where it went.

## Exposure, measured

| Probe | Result |
|---|---|
| `tools/scan_secrets.py` (tree) | **PASS** — nothing in the working tree |
| `.env` tracked by git? | **No** — `git ls-files .env` → no match |
| `.env` in `.gitignore`? | **Yes**, line 5 (plus `.env.local`, line 7) |
| `.env` blobs reachable in history | **1** |
| `refs/original/**` backup refs | **21** |
| Remote branches on `origin` | **3** |

So the working tree is clean and re-leaking is prevented. **The disclosure is historical and
remains reachable**, including from `refs/original/**` left behind by an earlier rewrite — those
refs are precisely what keeps the old objects alive after a `filter-branch`.

## What the CTO does

1. **Revoke** the exposed key in the OpenRouter dashboard. Do not wait for anything below.
2. **Issue** a replacement; put it in local `.env` only (already gitignored).
3. **Check usage/billing** on the old key for activity that is not ours. This is the only step that
   tells us whether the leak was exploited, and the window closes as logs age out.

## What Engineering does, and only on written sign-off

Sprint 7 stop condition 4 stands: *a history rewrite touching a ref whose owner cannot be
identified is not an engineering decision.* With 21 `refs/original/**` and 3 remote branches, this
rewrite changes published history and every clone must be re-cloned.

- [ ] Written owner sign-off, per affected ref
- [ ] Delete `refs/original/**` (21 refs) — otherwise the objects survive any rewrite
- [ ] Rewrite to drop the `.env` blob; expire reflog; `gc --prune=now`
- [ ] `tools/scan_secrets.py --all-refs` → PASS
- [ ] Force-push; notify every clone holder to re-clone

**This does not block Sprint 8 or Sprint 9 coding.** It never did. It blocks the release receipt.

## Standing state

Rotation: **not done** (CTO). Rewrite: **not started**, correctly — it is gated on rotation and on
sign-off, neither of which has happened.
