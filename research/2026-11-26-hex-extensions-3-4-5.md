# Post–Approach-#1 Extensions: Opening Book, VC Lite, and Neural PUCT

**Purpose:** Help a COMP34111 Hex team choose **one** optional extension (or a bounded combo) after parallel MCTS + two-distance/tactics + time management is stable (weeks 8–14).

**Research question:** Among extensions **3** (opening book + swap), **4** (MoHex-style knowledge: full vs lite), and **5** (CNN / AlphaZero-style PUCT), which path best maximises the **course performance mark** (75% wins vs last year’s bots, 25% move speed) under **5 min/game, 8 CPU, no GPU, paused on opponent turn, human-written code**?

**Author context:** Team of four undergrads; base roles **A** = infrastructure, **B** = search, **C** = eval/tactics, **D** = tournament/benchmarks. Committed to approach #1 per [2026-11-26-hex-agent-approaches.md](./2026-11-26-hex-agent-approaches.md). Deadlines: **proforma ~Nov**, **pre-check 14 Dec 14:00**, **submit 18 Dec**.

**Date:** 2026-11-26

**Research verified:** Partial — academic Hex literature is strong; **course-specific win deltas are qualitative** (no published COMP34111 Elo table). Tier-4 GitHub anecdotes labelled explicitly.

> **5-week delivery override:** This memo assumes extensions begin after **#1 is stable (~week 8 of a semester)**. If your team has only **~5 calendar weeks** to **14 Dec pre-check / 18 Dec submit**, use the integrated plan in **[2026-11-26-hex-extensions-3-4-5-five-weeks.md](./2026-11-26-hex-extensions-3-4-5-five-weeks.md)** instead. There, **3 + lite-4 run in parallel with #1** from week 1; person-week figures below are **not additive** on that timeline.

---

## Executive Summary

After approach **#1** is stable, the extension choice is really a **deadline × speed-mark × integration-risk** problem, not “which algorithm is strongest in Olympiad conditions.”

| Path | Effort (extension only) | Risk | Win upside vs #1-only | Speed mark | Marking narrative |
|------|-------------------------|------|------------------------|------------|-------------------|
| **Ext 3** — opening book + swap heuristics | **4–6 person-weeks** | **Low** | **Moderate** (openings/swap; smaller midgame jump) | **Strong positive** (instant book moves) | Clear, easy to explain |
| **Ext 4 full** — VC engine + pattern priors (Benzene-class) | **20–35+ person-weeks** | **Very high** | **Very high if finished** | **Uncertain** (heavy per-node knowledge) | Excellent *if* done — unlikely in 6 weeks |
| **Ext 4 lite** — bridges + dead/fillin subset + optional shallow mustplay | **6–10 person-weeks** | **Medium** | **Moderate–high** (tactics + branching) | **Slight negative** if over-computed; **neutral** if root-only | Strong “MoHex-informed” story |
| **Ext 5** — train CNN + PUCT MCTS | **12–22 person-weeks** | **High** | **High ceiling** | **Often negative** (CPU inference) | Impressive when it works |
| **3 + lite-4** (recommended combo) | **8–12 person-weeks** | **Medium-low** | **Best balanced** | **Net positive** (book offsets search cost) | Coherent MoHex narrative without Benzene |
| **3 + 5-lite** (tiny policy prior only) | **10–16 person-weeks** | **High** | **Volatile** | **Risky** | “AlphaZero-inspired” — audit inference budget |

**Recommendation:** Adopt **Extension 3 + Extension 4 (lite scope only)** — not full VC / MoHex 2.0 pattern learning / DFPN. This pairing targets both **40 games × two colours** (Red book + Blue swap) and **deeper search per CPU-second** via root move pruning, without jeopardising the **Dec 14 build check** or **speed ranking**.

Pick **Extension 3 alone** if #1 is late stabilising (week 8 slips to week 9+): you still gain swap-aware strength and free speed points.

Pick **Extension 5** only if (i) one member already has a **working CPU inference path** by week 9, (ii) the net is **small** (&lt;5 MB, &lt;30 ms forward pass on x86-64 Docker), and (iii) the team accepts risking **32%/40%** marks if integration fails — do **not** pair with full VC.

---

## Landscape map (variants considered)

| ID | Variant | Who uses it | Relevance to COMP34111 extension choice |
|----|---------|-------------|----------------------------------------|
| 3a | Hand-curated opening lines (HexWiki balanced cells) | Student bots, Wolve hand-tweaks | Low build risk; swap maps are heuristic |
| 3b | Lincke drop-out opening book + offline search | MoHex (9×11 books in research) | 85 Elo on 9×9 in ~1 day **with strong search** — student scale-down |
| 3c | Swap via short MCTS / two-distance margin | Student default | Needed even with a book |
| 4a | **Full** H-search + ICE + fillin + mustplay + reduced-board rollouts | MoHex, MoHex 2.0 | Research gold standard; **not** a 6-week port |
| 4b | **Lite** — local dead/fillin patterns + bridges + root inferior pruning | Practical student step | Most of MoHex gain, fraction of complexity |
| 4c | **Lite+** — mustplay from opponent winning SC (partial VC) | MoHex root pruning | High value, highest lite risk |
| 4d | MoHex 2.0 **learned pattern priors** (MM on 35k games) | MoHex 2.0 | ~250 Elo over MoHex on 11×11 — **training pipeline**, not a port |
| 5a | Policy-only CNN prior in UCT/PUCT | MoHex-CNN | +62.5–73% vs MoHex 2.0 at matched sims (research) |
| 5b | Policy + value (AlphaZero / PV-MCTS) | Gao IJCAI’18, course forks | Stronger but slower per simulation |
| 5c | **5-lite** — frozen small net, policy prior only, no self-play loop in semester | Pragmatic student | Cuts training scope; still inference risk |

---

## Assumed baseline (#1) — dependencies all extensions share

Extensions assume **#1** already provides:

| Component | Owner | Why extensions need it |
|-----------|--------|-------------------------|
| Stable `AgentBase` API, time manager, Docker/`check_submission` | A | Book/NN loads in `__init__` (≤3 min); no paused CPU cheating |
| Parallel root MCTS + RAVE (or equivalent) | B | Book exits into search; PUCT replaces UCT; lite-4 prunes children |
| Two-distance (or resistance) eval + bridge/tactical win-block | C | Swap heuristics; pattern consistency; optional progressive bias |
| Tournament harness, last-year bot pool, logging | D | Measure +3/+4/+5 regressions |

Without **reliable win/block at root** and **per-move budgeting**, extensions add little or cause blunders.

---

## Extension 3: MCTS + opening book + swap heuristics

### Expected strength vs #1-only

| Evidence lens | Claim | Confidence |
|---------------|-------|------------|
| Research | MoHex without book: “opening play is weak / inconsistent” vs Six/Wolve ([MoHex paper](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)). Lincke-style 9×9 book ≈ **85 Elo** in ~1 day — **not** directly transferable to 11×11 undergrad effort, but shows opening structure is a real lever. | Medium |
| Swap theory | HexWiki: centre openings too strong → swap; edges too weak → no swap; **a3–a8, c2, c10** classed as relatively balanced on 11×11 ([HexWiki swap](https://www.hexwiki.net/index.php/Swap_rule)). | Medium (heuristic, unsolved opening) |
| Course field | Last-year bots often use **random or naive swap** (`NaiveAgent` swaps 50%). A disciplined Red repertoire + Blue swap table wins **opening-equivalent games** before MCTS depth matters. | Medium |
| **Qualitative vs #1-only** | **+50–120 Elo** equivalent in a typical class cohort if openings were a weakness; **+2–6 wins / 40** plausible if many opponents blunder swap or face unfamiliar lines. Midgame vs strong MCTS peers: **small** gain. | Low–medium |

Ext 3 does **not** replicate MoHex 2.0’s **+250 Elo** pattern priors — that is extension **4d/5**, not a book.

### Dependencies on #1

- Red: fixed **balanced** first move(s) + optional book to depth 4–8 plies.
- Blue: `make_move` on turn 2 — swap decision **before** book continuation.
- MCTS: clear handoff (`if in_book: book_move else: search`).
- Time manager: book moves should cost **≪1 ms** (helps speed mark).

### Work breakdown (4-person team)

| Task | Lead | Person-weeks |
|------|------|----------------|
| Curate 6–12 Red opens from HexWiki / self-play stats | D | 0.5 |
| Encode book (JSON/SGF-like DAG) + loader in `__init__` | A | 0.5 |
| Blue swap table + margin rules (optional 0.5s confirm MCTS) | D + C | 1.0 |
| Book walk + colour/swap branching tests | A | 0.5 |
| Integration with MCTS (exit conditions, logging) | B | 1.0 |
| Self-play opening regression (121 Red opens × swap) | D | 1.0 |
| Tournament polish + proforma write-up | All | 0.5 |
| **Total** | | **~4–5** (buffer **6** with coursework) |

### Risks, failure modes, speed impact

| Risk | Mitigation |
|------|------------|
| Book line refuted by opponent off-book | Keep lines **short**; exit to MCTS early in unknown positions |
| Wrong swap table → donate game on turn 2 | Unit tests for `Move(-1,-1)` legality; mirror HexWiki “never swap a1/b1” |
| Overfitting to Benzene openings | Generate **your** lines from #1 self-play at 1–2 s/move |
| **Speed** | **Positive** — early moves far below cohort median |

### Academic integrity / coursework fit

- Human-authored book data and swap logic: **excellent fit**.
- Copying MoHex’s binary book from Benzene: **avoid** (licensing + not your work).
- Using HexWiki **ideas** with citation: **fine**.

---

## Extension 4: Virtual connections, inferior cells, pattern priors (MoHex-style)

Scope as two **distinct** efforts:

### 4-full (deprioritise — see end)

MoHex stack: **H-search** → winning SC → **mustplay**; **ICE** (19+ local patterns, vulnerable/captured/reversible); **fillin** on reduced board; knowledge threshold in tree; optional DFPN ([MoHex paper](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf); [Henderson PhD](https://sites.ualberta.ca/~hayward/theses/ph.pdf)). MoHex 2.0 adds **learned pattern priors** (~**250 Elo** on 11×11 vs MoHex ([MoHex 2.0](https://sites.ualberta.ca/~hayward/papers/m2.pdf))).

**Expected vs #1-only if completed:** potentially **largest** research-aligned gain (MoHex: tree knowledge ≈ **2× effective simulations**; mustplay fixes tactical collapses). **For this team in weeks 8–14:** probability of **correct, tuned** full engine ≈ **low**.

### 4-lite (recommended slice)

| Feature | Included in lite | Elo/strength expectation vs #1 | Notes |
|---------|------------------|----------------------------------|-------|
| Bridge pattern (playout + avoid breaking) | Usually already in #1 | (baseline) | MoHex: bridge + AMAF ≈ **286 Elo** over naive UCT — **much already in #1** |
| **Local dead / fillin patterns** (subset of Fig. 2, Henderson) | **Yes** | **Moderate** — fewer blunders, shorter rollouts | Safe pruning if patterns are **sound** |
| **Captured-reversible** tiny subset | Optional | Low–moderate | More correctness burden |
| **Mustplay from opponent winning SC** | **Optional “lite+”** | **High when triggered** | Needs partial connection detection — main bug surface |
| Full H-search / FastVC | **No** | — | Months |
| MoHex 2.0 pattern MM learning | **No** | — | Training pipeline, not a port |
| DFPN parallel solver | **No** | — | Extension scope creep |

**Qualitative vs #1-only (lite, no mustplay):** **+30–80 Elo** — mainly branching and rollout quality.

**Qualitative (lite+ mustplay, if correct):** **+80–180 Elo** in tactical positions — comparable spirit to MoHex root pruning, but **easy to get wrong** (illegal pruning).

### Dependencies on #1

- Correct **connectivity / groups** on board (for pattern matching).
- MCTS: apply pruning at **root** (and optionally depth 1 only) first — matches MoHex’s heavy root ICE without tree threshold complexity.
- Shared `generate_legal_moves()` filtered by knowledge module.
- **Do not** port Benzene — reimplement **documented patterns** from papers/thesis figures.

### Work breakdown

**4-lite (target):**

| Task | Lead | Person-weeks |
|------|------|----------------|
| Pattern DSL + matcher (6-neighbour, rotations) | C | 1.5 |
| Implement 8–15 dead/fillin templates + tests | C | 2.0 |
| Root move filter hook in MCTS | B | 1.0 |
| Reduced-board rollouts (fillin only) | B + C | 1.5–2.5 |
| Fuzz tests vs brute win-checker on small boards | A | 1.0 |
| Benchmark vs #1 (nodes/sec, win%) | D | 1.0 |
| **Total 4-lite** | | **6–8** |

**Add lite+ mustplay:** +3–5 person-weeks (C-heavy), +**medium–high** correctness risk.

**4-full:** +15–25 person-weeks beyond lite — **out of window**.

### Risks, failure modes, speed impact

| Failure mode | Symptom | Mark impact |
|--------------|---------|-------------|
| **False inferior prune** | Illegal strong moves removed → loses won games | Win mark collapse |
| Mustplay without sound SC | Same | Critical |
| Pattern check every simulation | Throughput drop | Speed mark ↓ |
| Knowledge in rollouts (MoHex found negative for many patterns) | Weaker MCTS | Win ↓ |

MoHex explicitly notes inferior patterns in **rollouts** often **hurt** — keep lite knowledge in **tree / move gen**, not playout policy, until proven beneficial.

**Speed:** Run heavy patterns at **root only** each move; amortise &lt;50 ms → usually OK. Full tree threshold (MoHex 50–400 visits) is **4-full** territory.

### Academic integrity

- Implementing algorithms from **papers/thesis** with your own code: **intended learning outcome**.
- Copying Benzene VC source: **avoid** (LGPL + misconduct risk).
- MoHex 2.0 **pattern weights file**: not your training — **do not ship** as priors unless you regenerate data.

---

## Extension 5: CNN / AlphaZero-style policy (+ value) + PUCT

### Expected strength vs #1-only

| Source | Finding | Scale-down for course |
|--------|---------|------------------------|
| [Gao move-prediction CNN](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf) | Policy net alone ≈ **1-ply Wolve** strength; as MoHex 2.0 prior: **62.5–73%** vs MoHex 2.0 at matched settings | Needs **~1M+ positions** from strong teacher — your #1 is weaker than MoHex 2.0 |
| [IJCAI’18 three-head PV-MCTS](https://ijcai.org/proceedings/2018/523) | **73.5%** vs MoHex-CNN with 10 s/move | CPU sim **0.3 ms** (3H) vs **1.8 ms** (2H) — inference dominates |
| Tier-4 [Hex-Ultra](https://github.com/Ray7788/Hex-Ultra) | Claims top class performance with staged MCTS → AlphaZero | **Anecdotal**; verify locally |
| Tier-4 course forks (2025–26) | Full AlphaZero + C++ self-play + GPU train, CPU tournament agent | **Systems thesis-level** — illustrates ceiling, not median outcome |

**Qualitative vs #1-only:**

- **5-full (self-play + ResNet + value head):** **+100–300 Elo** *if* training converges — **low probability** by Dec 18 without prior pipeline.
- **5-lite (small CNN, policy prior only, teacher = #1 self-play):** **+40–120 Elo** plausible; **+0–10 wins / 40** if peers are search-heavy.
- **Floor:** broken `torch` load, inference &gt;200 ms/move → timeouts + speed penalty → **40–32%** band.

### Dependencies on #1

- Strong **self-play** or teacher games (thousands) — generated **off** marking hardware OK; **no network** in tournament.
- MCTS: **PUCT** with `c_puct`, prior normalization over legal moves.
- Optional value head for leaf eval — only if leaf expansion budget proves net-positive on CPU.
- `build.sh` / wheel: **no GPU** in Docker play image; `torch` CPU only; weights via `dirname(__file__)`.

### Work breakdown

| Task | Lead | Person-weeks |
|------|------|----------------|
| Tensor encoding (9+ planes: stones, colour, bridges optional) | C | 1.0 |
| Small CNN (e.g. 4–6 conv layers, 64 filters) | C | 1.5 |
| Data pipeline from #1 self-play | D | 2.0 |
| Training off-machine (GPU lab) + export `.pt` | C | 2.0–4.0 |
| PUCT integration + legal-move mask | B | 2.0 |
| CPU latency profiling in Docker amd64 | A | 1.5 |
| Fallback to #1 if inference fails | A + B | 0.5 |
| **5-lite total** | | **10–12** |
| **5-full (iterative self-play)** | | **18–25+** |

### Risks, failure modes, speed impact

| Risk | Impact |
|------|--------|
| Weak teacher → weak net | Marginal win gain |
| Large checkpoint / slow `__init__` | FAILED_LOAD / speed |
| Per-simulation `forward()` | Speed mark hit (25% of grade) |
| Academic integrity: AI-generated agent code | **Misconduct** per `docs/GAME.md` |
| “Download someone’s trained net” | **Grey** — must be your training data pipeline |

**Paused opponent turn:** threads stop — OK; but **do not** spawn training workers during games.

### Coursework fit

- **Best narrative** for “modern AI” — **if** demo is stable.
- **Worst risk-adjusted mark** among extensions due to integration + speed.

---

## Comparison table (extensions at a glance)

| | Effort (pw) | Risk | Win-rate upside | Speed impact | Approach-mark story |
|--|------------|------|-----------------|--------------|---------------------|
| **3** | 4–6 | Low | Moderate (openings) | **++** | Solid, under-explained by many teams |
| **4-lite** | 6–10 | Medium | Moderate–high | 0 / − if heavy | Strong Hex AI literacy |
| **4-full** | 20–35+ | Very high | Very high | −− | Olympic — unrealistic |
| **5-lite** | 10–12 | High | Medium–high | − | AlphaZero-inspired |
| **5-full** | 18–25+ | Very high | Very high | −−− | Research project |
| **3 + lite-4** | 8–12 | Med-low | **High (balanced)** | **+** | **Best overall** |
| **3 + 5-lite** | 12–16 | High | Volatile | − | Only if ML path proven early |

*pw = person-weeks across the team; win upside is qualitative vs stable #1.*

---

## Workload split: base roles vs each extension

### Base (#1) — reference

| Member | Primary |
|--------|---------|
| A | Engine API, time, Docker, threading, CI |
| B | MCTS, parallel root, transpositions |
| C | Two-distance, tactics, move gen |
| D | Benchmarks, swap baseline, submission |

### When adding **Extension 3**

| Member | Shift |
|--------|--------|
| A | Book file I/O, `__init__` performance |
| B | Book/MCTS handoff, less tuning |
| C | Swap margin features (two-distance delta) |
| D | **Owns book + swap**; opening sweeps |

### When adding **4-lite** (with or without 3)

| Member | Shift |
|--------|--------|
| A | Profiling pattern matcher; ensure prune doesn’t break tests |
| B | **Owns MCTS integration**; root-only filters |
| C | **Owns pattern library** + correctness proofs on small boards |
| D | A/B tests win% vs #1; regressions vs last-year bots |

### When adding **5-lite**

| Member | Shift |
|--------|--------|
| A | Docker `torch` CPU, build size, timing guards |
| B | **PUCT** + batching / cache priors at root |
| C | **Net + training pipeline** (heavy) |
| D | Self-play dataset ops; tournament matrix |

**4-full** would invert the team into a miniature Benzene fork — **do not** attempt with fixed A/B/C/D without dropping other modules.

---

## Phased integration plan (weeks 8–14)

Assume **#1 stable by end of week 8** (MCTS parallel + two-distance + tactics passing `check_submission`).

### Recommended path: **3 + lite-4**

| Week | Milestone | Owner emphasis |
|------|-----------|----------------|
| **8** | Choose extension; freeze #1 tag; Red book v0 (3–5 lines); pattern spec for 8 dead templates | D, C |
| **9** | Blue swap v1 (HexWiki table + tests); pattern matcher MVP; root filter behind feature flag | D, C, B |
| **10** | Book depth 6–8; MCTS exit policy; integrate root prune — **proforma / Nov report** documents design | All |
| **11** | Self-play opening suite; prune fuzz tests; tune time mgr (book = instant) | D, A |
| **12** | Full round-robin vs last-year bots; fix false prune bugs | D, C |
| **13** | Speed tuning; **submit for pre-check 14 Dec**; rebuild `build.sh` | A, D |
| **14** | Buffer: only bugfixes; final **18 Dec** submit | All |

### If choosing **3 only** (fallback)

Weeks 9–11: book + swap only; weeks 12–14: tournament polish — leaves slack for #1 debt.

### If choosing **5-lite** (only if week-9 inference &lt;30 ms proven)

Weeks 8–9: data + tiny net; week 10: PUCT; weeks 11–12: train refresh; weeks 13–14: same as above — **no lite-4** unless C is finished early.

---

## Focused recommendation (dominate-class outcome)

**Primary:** **3 + lite-4** — maximises **expected performance mark** under `(3×win + speed)/4`:

1. **Win component:** Blue swap fixes free games; lite dead-cell pruning reduces tactical losses MoHex papers attribute to “weak knowledge” — without betting the term on H-search correctness.
2. **Speed component:** Book moves improve cohort ranking; avoid per-simulation CNN or per-node VC.
3. **Deadline:** Fits **8–12 person-weeks** inside weeks 8–14 alongside other modules.
4. **Integrity:** Explainable, paper-sourced, human-implemented.
5. **Narrative:** “MoHex-informed MCTS” without embedding Benzene — aligns with approach memo and lectures.

**Runner-up:** **3 alone** — if integration bandwidth is low or #1 slips.

**Do not choose:** **4-full** or **5-full** as the *sole* extension unless scope is cut elsewhere and a member has **prior shipped** Hex ML.

**Combo 3 + 5-lite:** only if profiling shows **&lt;50 ms combined overhead per move** at median time budget — otherwise speed mark erodes wins.

---

## Deprioritized / out of scope (Extension 4)

Do **not** build after #1 unless the course staff explicitly rewards solving:

| Component | Why deprioritize |
|-----------|------------------|
| Full **H-search / FastVC** completeness | PSPACE-hard; months to debug ([Anshelevich 2002](https://www.cs.auckland.ac.nz/courses/compsci767s2c/resources/VAnshelevich-ARTINT.pdf); [FastVC](https://sites.ualberta.ca/~hayward/papers/strongervcs.pdf)) |
| **DFPN / SCNS** solver thread | MoHex helper, not student extension in 6 weeks |
| **MoHex 2.0 pattern MM + 65k pattern tables** | Requires large game corpus + inferior engine on patterns |
| Knowledge threshold on **every** tree node | Performance + implementation complexity |
| **Inferior patterns inside rollouts** | MoHex evidence: often **weakens** play |
| Vendoring **Benzene** source | Integrity / license / not portable to `AgentBase` |
| Exhaustive **11×11 opening solve** | Open outside 8×8/9×9 ([MoHex solver stats](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)) |

**Lite+ mustplay** is the only “stretch” item — take it only if lite patterns are **green** in week 10 tests.

---

## Synthesis across sources

| Claim | Confidence |
|-------|------------|
| Opening books materially strengthen MCTS Hex players | **High** (MoHex self-critique + Lincke gains) |
| VC/mustplay is a large multiplier **when correct** | **High** (MoHex 2010) |
| Full VC port feasible for 4 undergrads in 6 weeks | **Low** |
| Dead/fillin pattern subset is implementable | **High** (Henderson thesis figures) |
| CNN priors boost strong MCTS | **High** on research bots ([Gao](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)) |
| CNN priors + CPU limits + weak teacher → reliable class domination | **Low–medium** |
| Pie rule makes **both** Red book and Blue swap mandatory for top marks | **High** (HexWiki + engine rules) |
| Course: speed 25%, paused agent, 8 CPU | **High** ([`docs/GAME.md`](../docs/GAME.md)) |

**Tension:** Research Elo tables (250+, 85, 286) used **minutes/move and Olympiad hardware** — scale expectations down to **~4–7 s average** and **8 cores, no pondering**.

---

## Research corpus

| # | Source | Tier | Topic | Key claim |
|---|--------|------|-------|-----------|
| 1 | `docs/GAME.md` | 1 | Marking | 40 games, 75/25 win/speed, 8 CPU, no GPU, AI-prohibited code |
| 2 | Arneson et al. 2010 MoHex | 1 | MCTS+VC | Mustplay, tree knowledge ≈2× sims, opening weakness |
| 3 | Huang et al. MoHex 2.0 | 1 | Patterns | ~250 Elo vs MoHex 11×11 |
| 4 | Henderson PhD | 1 | Inferior/fillin | Local patterns, ICE |
| 5 | Anshelevich 2002 | 1 | VC theory | H-search limits |
| 6 | Gao move prediction | 1 | CNN | 62.5–73% vs MoHex 2.0 with prior |
| 7 | Gao IJCAI’18 | 1 | PV-MCTS | 3-head vs 2-head; inference ms/sim |
| 8 | HexWiki swap | 3 | Openings | Balanced cells, swap heuristics |
| 9 | Lincke CG’00 (via MoHex cite) | 2 | Opening books | Drop-out expansion |
| 10 | MoHex Olympiad / Wolve reports | 2 | Context | Books + ICE in production |
| 11 | Hex-Ultra GitHub | 4 | Course anecdote | Staged MCTS→AZ — unverified |
| 12 | Prior memo `hex-agent-approaches.md` | 1 (local) | Team plan | #1 baseline scope |

---

## Sources

### Primary / academic

- [MoHex MCTS (Arneson, Hayward, Henderson, 2010)](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)
- [MoHex 2.0 (Huang et al.)](https://sites.ualberta.ca/~hayward/papers/m2.pdf)
- [Henderson PhD thesis](https://sites.ualberta.ca/~hayward/theses/ph.pdf)
- [Anshelevich hierarchical Hex](https://www.cs.auckland.ac.nz/courses/compsci767s2c/resources/VAnshelevich-ARTINT.pdf)
- [Stronger VCs (Pawlewicz et al.)](https://sites.ualberta.ca/~hayward/papers/strongervcs.pdf)
- [Gao et al.: Move prediction CNN](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)
- [Gao et al.: Three-head NN (IJCAI 2018)](https://ijcai.org/proceedings/2018/523)

### Community / reference

- [HexWiki: Swap rule](https://www.hexwiki.net/index.php/Swap_rule)
- [HexWiki: Basic strategy](https://www.hexwiki.net/index.php/Basic_(strategy_guide))
- [Benzene project](https://benzene.sourceforge.net/) — reference only, do not embed

### Course / local

- [`docs/GAME.md`](../docs/GAME.md)
- [`research/2026-11-26-hex-agent-approaches.md`](./2026-11-26-hex-agent-approaches.md)
- [`research/2026-11-26-hex-extensions-3-4-5-five-weeks.md`](./2026-11-26-hex-extensions-3-4-5-five-weeks.md)

### Low confidence (illustrative only)

- [Ray7788/Hex-Ultra](https://github.com/Ray7788/Hex-Ultra)
- [N1tingale/COMP34111-AI-Games-Hex](https://github.com/N1tingale/COMP34111-AI-Games-Hex) — architecture reference, not performance guarantee

---

*Global research memo. Wide corpus first; executive summary filtered to post–#1 extension choice for COMP34111 2026–27.*