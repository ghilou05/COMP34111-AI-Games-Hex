# Hex extensions 3 / 4 / 5 vs base #1 — five-week delivery plan

**Audience:** COMP34111 group of 4, committed to **#1** (MCTS + two-distance + tactics + time).  
**Constraint added:** ~**5 calendar weeks** to working submission (proforma ~27 Nov; **pre-check 14 Dec 14:00**; **final 18 Dec 14:00**).  
**Marking:** 40 games vs last year’s bots; win 75% / speed 25%; 5 min clock; 8 CPUs; no GPU; paused on opponent turn; human-written code.

**Research companion:** [2026-11-26-hex-agent-approaches.md](./2026-11-26-hex-agent-approaches.md)  
**Deep dive (semester / post–#1 framing, papers, MoHex rollouts note):** [2026-11-26-hex-extensions-3-4-5.md](./2026-11-26-hex-extensions-3-4-5.md) — from [global-research Hex extensions](23b32825-5446-48e1-b37f-972007e277ba).

---

## Executive summary (5-week reality)

| Extension | What it is | Feasible as *late* add-on (week 4–5)? | Dominate-class upside | Verdict |
|-----------|------------|--------------------------------------|------------------------|---------|
| **3 — Opening book + swap** | Fixed Red responses; Blue turn-2 swap policy ([HexWiki swap](https://www.hexwiki.net/index.php/Swap_rule)) | **Yes** — can start week 1 | **High ROI** for 40-game pool (both colours) | **Do this** — weave into #1, not a separate project |
| **4 — VC / inferior / patterns** | Full MoHex knowledge ([Arneson et al. 2010](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)); **lite** = bridges, root win/block, ~5–10 dead patterns, optional 1-ply mustplay | **Full: no.** **Lite: yes** if started week 1–2 with eval owner | Full: huge if finished (unlikely). Lite: medium, stabilises MCTS | **Lite-4 only** — same person as tactics; **no H-search** |
| **5 — CNN + PUCT MCTS** | AlphaZero-style ([Gao et al. move prediction](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)) | **No** for train+integrate in 5 weeks | High ceiling, many teams ship **slower weaker** bots | **Defer**; mention in proforma as out-of-scope unless bot stable **before 7 Dec** |

**Recommendation to dominate in 5 weeks:**  
**#1 + extension 3 + extension 4 (lite only).** Do **not** treat 3 or lite-4 as something you add after “MCTS is done” — there is no time. **Reject extension 5** unless one member already has a trained CPU-small net and PUCT stub by week 3.

Effective capacity: 4 people × 5 weeks ≈ **20 person-weeks**, but ~**12–14 person-weeks** after labs/other modules. Base #1 alone needs **~9–11**; that leaves **~2–3 person-weeks** for a *real* extension — exactly one of **(3 deeply)** or **(4-lite deeply)**, not both heavy and not #5.

**Best combo:** #1 includes **lite-4 from day 1** (bridges, win/block, simple dead cells); **extension 3** in parallel from week 2 (openings/swap). That is one integrated bot, not three sequential projects.

---

## Comparison table (extensions after #1 — academic + course framing)

| | **Ext 3: openings + swap** | **Ext 4: VC / patterns** | **Ext 5: neural + PUCT** |
|--|---------------------------|-----------------------------|---------------------------|
| **Effort (person-weeks)** | **0.5–1.5** | **Full: 6–12+** · **Lite: 1.5–3** | **5–10+** (train + integrate) |
| **Risk** | Low | Full: **very high** · Lite: medium | **High** (speed, bugs, init time) |
| **Win upside vs #1-only** | **+3–8 games** class pool (illustrative); both colours matter | Full: MoHex-scale · Lite: fewer blunders, tighter move list | Only if net + MCTS beat heuristics ([MoHex 2.0](https://sites.ualberta.ca/~hayward/papers/m2.pdf) needed *patterns + search*) |
| **Speed impact** | **Positive** (instant early moves) | Lite: slight + if pruning works; full VC: can be **slow** | Often **negative** (CPU inference every node) |
| **Approach-mark story** | Pie rule, opening theory, testing swap thresholds | MoHex / inferior cells literature | AlphaZero, Gao CNN — strong if ablated |
| **5-week fit** | **Excellent** | **Lite only** | **Poor** |

*Win upside is qualitative — run your own round-robin vs NaiveAgent and sample `Group998`-style bots.*

---

## Extension 3 — Opening book + swap heuristics

### Strength gain

- **Red:** Unbalanced openings get punished by swap; balanced 11×11 openings avoid gifting colour ([HexWiki strategy](https://www.hexwiki.net/index.php/Basic_(strategy_guide))).
- **Blue:** Turn-2 swap decision is a **one-shot optimisation** — cheap vs 1000 MCTS sims.
- Literature: Opening books yielded **~85 Elo on 9×9** in Hex program comparisons (Lincke / Wolve family — see Benzene ecosystem); on 11×11 with pie rule, gains concentrate in **first 2–4 plies**.

### Depends on #1

- Legal `Move(-1,-1)` on turn 2 only; colour flip handled by engine.
- Optional: 50–200 rollout MCTS to estimate whether swap beats playing as Blue.

### Work breakdown

| Task | Owner | Time |
|------|-------|------|
| Pick 3–8 Red openings (near centre / “balanced” family) | D | 2–4 h |
| Encode book (dict turn → move or policy weights) | D + A | 2–4 h |
| Swap heuristic: accept if opponent opening “too strong” | D | 4–8 h |
| Log swap rate / win% in batch games | D | ongoing |
| Fall back to MCTS when out of book | B | 2 h |

**Total: ~0.5–1.5 person-weeks** (mostly D, parallel to MCTS).

### Risks

- Wrong book → losses vs swap-savvy bots (mitigate: short MCTS backup).
- **Speed:** book moves are **fast** — helps speed rank.

### Integrity

- Human-authored tables/heuristics; cite HexWiki + papers in journal.

---

## Extension 4 — VC / inferior cells / patterns (full vs lite)

### Full scope (MoHex-class)

H-search VCs, mustplay from winning SC, inferior-cell database, MoHex 2.0 pattern priors ([Huang et al.](https://sites.ualberta.ac.uk/~hayward/papers/m2.pdf)).

- **Strength:** Large — MoHex’s edge is largely **knowledge**, not raw MCTS.
- **Effort:** **6–12+ person-weeks** — wrong for 5-week calendar.
- **Do NOT build:** AND/OR VC complete set, DFPN solver, FastVC port, pattern tables from self-play mining.

### Lite scope (recommended)

| Feature | Purpose | Effort |
|---------|---------|--------|
| Root **win in 1** / **block loss in 1** | Mandatory | (in #1) |
| **Bridge** template in playouts + don’t break own bridges | MoHex savebridge idea | 0.3 pw |
| **5–15 local dead/vulnerable patterns** ([Henderson thesis](https://sites.ualberta.ca/~hayward/theses/ph.pdf) Ch. 2.9 subset) | Shrink move list | 0.5–1 pw |
| Optional: **mustplay** only when opponent has **immediate** connection threat (BFS), not full SC | Avoid obvious throws | 0.5–1 pw |

**Lite total: 1.5–3 person-weeks**, overlaps **#1 tactics** — assign to **Member C**, not a separate “extension phase.”

### Risks (lite)

- Over-pruning → illegal *thinking* you’re safe; unit-test positions from Benzene/Henderson examples offline (do not ship Benzene).
- **Apply lite-4 at root move gen / selection first**, not in random playouts until ablated — MoHex reports inferior patterns inside rollouts often **hurt** ([extensions memo](./2026-11-26-hex-extensions-3-4-5.md)).

### Role shift

- **C** owns pattern table + integration in `generate_moves()` and rollout policy.
- **B** consumes filtered move list in MCTS.

---

## Extension 5 — CNN / AlphaZero-style + MCTS

### Strength gain

- Gao et al.: CNN move prediction + search beats eval-only; **MoHex 2.0** shows **learned pattern priors** help MCTS a lot.
- Under course limits: net is **CPU inference**, no GPU at mark time — batch size 1, latency per expansion.

### Depends on #1

- Working MCTS, board tensor encoding, stable agent before touching PUCT.

### Work breakdown (full #5)

| Task | Person-weeks |
|------|----------------|
| Self-play pipeline (swap + odd turns) | 1.5–2 |
| Net train (off-machine GPU) | 2–4 |
| PUCT integration + tune exploration | 1.5–2 |
| Size/load in `__init__` (<3 min), amd64 | 0.5–1 |
| Ablation for presentation | 0.5–1 |

**5–10 person-weeks**, **cannot** start week 4 and finish by 18 Dec with untested #1.

### Risks

- **FAILED_LOAD** / slow `__init__`; **TIMEOUT** from inference; wins **below** #1+3+lite-4 if training thin.
- **Approach mark:** good story only if net ablation shows gain.

### 5-week verdict

**Reject as primary extension.** Optional **stretch** only if by **7 Dec**: #1 wins >70% vs Naive in batch, one member adds **inference-only** tiny policy (no retrain).

---

## Choosing among 3, 4, 5 (decision tree)

```
5 weeks to submit
├─ Bot unstable by 7 Dec? → ONLY #1 + lite-4 (already in tactics) + minimal book (1 Red, swap rule-of-thumb)
├─ Bot stable by 7 Dec?
│   ├─ Want dominate + low risk? → **Extension 3** (deep book + swap tuning) + **lite-4 already in #1**
│   ├─ Strong C++ dev + love theory? → **More lite-4 patterns**, NOT full VC
│   └─ ML hobbyist + GPU access + bot fast? → **5-lite** (prior at root only), keep heuristics
└─ Full VC or full AlphaZero? → **No** for this deadline
```

**If forced to pick exactly one extension label for proforma:** say **Extension 3**, with **MoHex-inspired tactical pruning (lite-4)** described inside base #1.

---

## Five-week calendar (integrated plan)

Assume week 1 starts **~26 Nov**.

| Week | Dates (approx) | Goal | Everyone |
|------|----------------|------|----------|
| **1** | 26 Nov – 2 Dec | Agent shell, BFS/UF win, win/block, time clock, Docker unittest | A leads; all play `Hex.py` |
| **2** | 2 – 9 Dec | **MCTS** (UCT), random+bridge playouts, **lite-4** bridges | B + C |
| **3** | 9 – 14 Dec | **Two-distance**, parallel root (8 workers), **Ext 3** book + swap v1 | B/C/D; **14 Dec: pre-check submit** |
| **4** | 14 – 18 Dec | Tune budgets; batch vs reference bots; fix crash/timeout; `check_submission.py` | D + A |
| **5** | *buffer* | Presentation prep, journal ablations, final tar **18 Dec** | All |

*If your “5 weeks” means only until 18 Dec, weeks 4–5 are polish — no new extension code after **11 Dec**.*

---

## Workload split (4 members)

### Base roles (weeks 1–5)

| Member | Core #1 | + Ext **3** | + Ext **4 lite** | + Ext **5** (not advised) |
|--------|---------|------------|------------------|---------------------------|
| **A — Infra** | Agent, time, `cmd.txt`, tests, Docker amd64 | Wire book lookup in `make_move` | Hook pattern filter in move gen | Load `weights.pt` in `__init__` |
| **B — Search** | MCTS, parallel root, transpositions? | Use book for first ply only | Search on filtered children | PUCT formula |
| **C — Eval/tactics** | Two-distance, rollout bias | — | **Pattern table, bridges, dead cells** | Board → tensor |
| **D — Tournament** | Baselines, logs | **Openings research, swap tuning, stats** | Regression positions for patterns | Self-play (drops everything else) |

### Recommended ownership (dominate, 5 weeks)

- **A:** Integration + submission oracle (pre-check owner).
- **B:** MCTS + parallelism (critical path).
- **C:** Two-distance + **lite-4** (same stream).
- **D:** **Extension 3** + benchmarking + presentation plots.

No fifth stream for neural unless **D is replaced** by ML specialist and bot was stable week 2.

---

## Phased integration (not “finish #1 then extend”)

| When | Integrate |
|------|-----------|
| Week 1 | win/block (proto lite-4) |
| Week 2 | bridges in playouts + MCTS |
| Week 2–3 | opening book + swap (ext 3) **in parallel** with two-distance |
| Week 3 | parallel MCTS; freeze features after 11 Dec |
| Week 4+ | parameters only (sim count, C, time fractions) |

---

## Proforma wording (extension choice)

> Base: parallel MCTS with two-distance evaluation and tactical rules (MoHex-inspired). **Extension:** balanced **opening repertoire** and **pie-rule swap policy** (Extension 3). **Tactical pruning** via bridges and a small inferior-cell pattern set (lite Extension 4, not a full VC engine). **Extension 5 (neural MCTS)** is out of scope for our five-week delivery; we may revisit only if the bot passes pre-check with margin.

---

## Sources

- [MoHex MCTS (Arneson, Hayward, Henderson, 2010)](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)
- [MoHex 2.0 patterns](https://sites.ualberta.ca/~hayward/papers/m2.pdf)
- [Henderson PhD — inferior cells](https://sites.ualberta.ca/~hayward/theses/ph.pdf)
- [Gao et al. — CNN move prediction](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)
- [HexWiki: Swap rule](https://www.hexwiki.net/index.php/Swap_rule)
- [HexWiki: Basic strategy / openings](https://www.hexwiki.net/index.php/Basic_(strategy_guide))
- Course: `docs/GAME.md` in this repository