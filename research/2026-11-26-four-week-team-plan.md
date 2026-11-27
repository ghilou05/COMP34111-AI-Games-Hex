# COMP34111 Hex — 4-week team plan (direction for issues/tasks)

**Purpose:** Shared direction for four teammates working mostly in parallel. Not a solution-design spec or line-by-line implementation plan.

**Strategy:** **Stage 1** = shippable **MCTS + light Hex knowledge + opening/swap** (safety net for marks). **Stage 2–3** = **offline SL distillation** (teacher = your own slow MCTS; student = pattern table and/or tiny CNN) — **optional at match time** with A/B proof and fallback to Stage 1.

**Anchors:** [`docs/GAME.md`](../docs/GAME.md), [`docs/SUBMISSION-CHECKLIST.md`](../docs/SUBMISSION-CHECKLIST.md), [`research/2026-11-26-hex-agent-approaches.md`](./2026-11-26-hex-agent-approaches.md).

---

## 1. Agree before you split work (pre-flight checklist)

Resolve these in **one short meeting** (record in group diary). Block GitLab issues until decided.

| # | Decision | Why it blocks integration | Response (Group 18) |
|---|----------|---------------------------|---------------------|
| 1 | **Canvas group ID** → folder `agents/GroupXYZ/` and `cmd.txt` | Wrong name = failed load | **Agreed:** Canvas group **18** → `agents/Group018/`, `Group018.tar`, `check_submission.py 18` / `Group018`. **14 Dec pre-check upload:** A (Abs). |
| 2 | **Search language:** Python-only v1 vs **compiled core** (C++/Rust/Go) behind thin Python `AgentBase` | Drives `build.sh`, who owns B, sim counts | **Agreed:** **Python MCTS in week 1.** **Week 2 checkpoint:** B (Laymoi) reviews sim-count / move-time metrics; decide then whether to escalate compiled `search/` (+ `build.sh`). |
| 3 | **Single entry agent class** (e.g. `MyAgent`) + **feature flags** (`USE_STUDENT = False`) | Stage 3 must not break Stage 1 submit | **Agreed:** one `MyAgent`; `USE_STUDENT = False` default until A/B says enable. |
| 4 | **Teacher data policy:** train only on **your** bot’s games until staff confirm in writing whether external engines (KataHex, etc.) are allowed for labels | Approach mark / integrity | **Default:** own slow-MCTS labels only. **Week 2:** email staff to confirm external-engine labelling; until reply, stay on own games. |
| 5 | **Generative AI** (Canvas brief + journal disclosure) | Approach / integrity | **Resolved:** course allows GenAI; repo `README.md` / `docs/GAME.md` do not prohibit it. **Disclose** tool use in individual + group journals per Canvas. (Stale “human-written only” lines in `research/` memos are not course policy.) |
| 6 | **Git workflow:** `main` always passes `check_submission` on amd64 Docker; `feat/*` branches | Pre-check 14 Dec safety | **In progress:** team will adopt (`main` submittable, `feat/*`, 2×/week merge + smoke). Not configured in tracker yet. |
| 7 | **Integration contract** (Section 3 below) — names of modules and function signatures | Parallel work | **Owner:** A (Abs) defines and **freezes `core` API end of week 1**; publishes signatures before B/C/D deepen work. |
| 8 | **Map A/B/C/D → real names** + who submits weekly group diary | Journal is marked | **A** Abs · **B** Laymoi · **C** Ghiles · **D** Idris. Group diary: rotate weekly (minutes in Canvas). |
| 9 | **Minimum experiment standard:** e.g. ≥100 games, both colours, log CSV for journal | Approach mark evidence | **Pending next meeting:** C + B (bench + search) propose numbers/CSV columns; **all experiment runners** ratify before journal claims. Plan default still ≥100 games, both colours, `--seed`. |
| 10 | **Time budget policy:** opening/book instant, default 1–2 s/move, boost on tight eval | Speed mark (25% of performance) | **Not learned** (Stage 1): hand-coded chess-clock split for MCTS—book/opening ply ≈0 s; typical ply ~1–2 s; **boost** when `knowledge.evaluate` says tight (optional thresholds in `config.py`). **Agree constants in week 1** (B owns scheduler, C inputs eval hook, A wires `make_move`); tune in week 3 against logs. |

**Time budget (row 10) — not ML:** Marking gives **5 minutes total per game** ([`docs/GAME.md`](../docs/GAME.md)). The time manager decides **how many seconds this move’s `best_move(..., budget_sec)` gets** from time left and moves left. That rule is engineering choice for Stage 1, not something the CNN/RL student learns (student is optional **root prior** only later).

**Preliminary analysis (half day, person D + one other):**

- Run `NaiveAgent` vs itself; note mean move times in logs.
- `python3 check_submission.py` on empty/template folder — list failures.
- Build Docker `linux/amd64` once; confirm all four can run container.

---

## 2. How this maps to marks (what the plan optimises)

| Course component | Weight (of course) | Plan delivers |
|------------------|-------------------|---------------|
| **Win performance** | 18.75% | Stage 1 tactics + search; optional student only if wins ↑ |
| **Speed performance** | 6.25% | Compiled search if possible; book moves; no per-rollout neural |
| **Approach** (presentation, journal, statement) | 25% | MCTS/UCT, Hex literature, **A/B logs**, distillation story (SL), optional RL rounds |
| **Journal** (individual + group) | Part of approach | Weekly entries tied to milestones below |
| **Performance formula** | (3×win + speed)/4 | Don't trade ~7+ losses for marginal speed — measure |

**Failure modes to plan against:** `CRASH`, `TIMEOUT`, `FAILED_LOAD` (32%), `BAD_MOVE` — Stage 1 milestone is **zero** of these vs `NaiveAgent` for 20+ games.

**Deadlines:**

| Date | Action |
|------|--------|
| **Fri 27 Nov** | Proforma + group journal; lab approach discussion |
| **Fri weekly 18:00** | Individual diary + group minutes |
| **Mon 14 Dec 14:00** | **Submit Stage 1** for staff run/build check |
| **Fri 18 Dec 14:00** | Final bot + signed approach PDF |

---

## 3. Integration architecture (work independently, merge safely)

Keep **one public surface:** `agents/GroupXYZ/MyAgent.py` (`AgentBase`). Everything else is internal packages under `agents/GroupXYZ/`.

```
GroupXYZ/
  cmd.txt
  MyAgent.py              # make_move: time → knowledge → search → optional student hint
  build.sh                # if compiled search exists
  config.py               # feature flags, paths to weights/
  core/                   # A: board copy, move gen, connectivity, protocol helpers
  search/                 # B: MCTS, parallel root, time budget
  knowledge/              # B2: win/block, bridges, two-distance, openings, swap
  bench/                  # C: batch runner, stats, teacher data writer
  ml/                     # D: train scripts (optional in tar), student loader, inference
  weights/                # .pt or .json — small, ship in submission
  tests/                  # shared unit tests (or repo test/ imports)
```

**Contract (signatures — agree in pre-flight):**

| Module | Provides | Consumes |
|--------|----------|----------|
| `core` | `BoardState`, `legal_moves()`, `apply_move()`, `has_won(colour)`, `to_planes()` for ML | Engine `Board` / `Move` |
| `knowledge` | `tactical_move(state)` → optional forced move; `opening_move(state)`; `should_swap(state, opp_move)`; `evaluate(state)` → float | `core` |
| `search` | `best_move(state, budget_sec, priors=None)` → `(x,y)` | `core`, `knowledge` |
| `ml.student` | `load()` in init; `policy_prior(state, legal)` → dict or tensor | `core`; **never required** for legal play |
| `bench` | `play_series()`, `write_teacher_row()` | CLI, config paths |

**Rule:** Stage 2/3 **never** replace `search` until `bench` shows win-rate gain after speed adjustment.

**Knowledge priority (MoHex-aligned):** Literature and MoHex itself treat **virtual connections (VCs)**—not raw MCTS sim count—as the main separator from “random UCT on Hex.” Bridges are the smallest VC case; must-play / connection-style pruning from partial VCs is where most MoHex-style strength comes from relative to bare search. **This is the lever the team most needs to get right:** invest in correct VC-related logic (and how it feeds `tactical_move`, move pruning, and `evaluate` for time boosts) before chasing optional ML. A full Benzene H-search port stays out of scope (Section 4); incremental VC work in `knowledge/` is **P0** for win rate, not a polish item.

---

## 4. Three stages (revised — not “huge AlphaZero”)

| Stage | What | Match-time cost | Submit? |
|-------|------|-----------------|---------|
| **1 — Baseline** | MCTS + light Hex + book/swap + time mgmt | CPU search only | **Yes — 14 Dec mandatory** |
| **2 — Teacher (offline)** | Slow MCTS (30–60 s/move) self-play → dataset | None | Ship data generation scripts optional |
| **2b — SL student** | Pattern weights and/or **small** CNN trained on teacher | Lookup / few leaf evals | Only if tested |
| **3 — Optional RL** | Few self-play fine-tune rounds (REINFORCE or AZ-style) | Same as 2b | Stretch only |

**Explicitly out of scope for 4 weeks:** full AlphaZero from scratch, 30M positions, bundling KataHex, huge ResNets, per-rollout CNN calls.

---

## 5. Four-week calendar

Assume **Week 1 = 26 Nov – 2 Dec** (adjust if your start differs).

### Week 1 — Foundation + legal play

| Goal | Done when |
|------|-----------|
| Repo layout, Docker amd64, `cmd.txt` stub | All four can run container |
| `core` + agent returns **legal** moves | vs `NaiveAgent` completes |
| Win/block at root | Unit tests on 1-move positions |
| Skeleton MCTS (random rollouts) | No crash 10 games |

### Week 2 — Stage 1 strength

| Goal | Done when |
|------|-----------|
| Two-distance (or resistance) + bridges in rollouts | Beats random tactically in tests |
| Opening + swap policy | Correct `(-1,-1)` only turn 2 Blue |
| Parallel MCTS (8 workers) if compiled path ready | Utilisation in logs |
| **Person C:** `bench` v1 — batch 100 games, CSV | Journal table #1 |

### Week 3 — Safety submit + teacher pipeline

| Goal | Done when |
|------|-----------|
| Time budgeting tuned | Mean move time logged; no timeouts |
| **`check_submission.py GroupXYZ` clean** | 14 Dec readiness |
| **Submit Stage 1 — Mon 14 Dec 14:00** | Staff confirm runs/build |
| **Person C:** teacher data generation overnight jobs | ≥10k positions (target) |
| **Person D:** Colab SL train v0 | Weights load in `__init__` <3 min |

### Week 4 — Integration + final

| Goal | Done when |
|------|-----------|
| Student **root prior only** + flag `USE_STUDENT` | A/B vs Stage 1 (≥100 games) |
| Keep stronger variant for tar | Document fallback in statement |
| Final submission + PDF statement | Fri 18 Dec 14:00 |
| Presentation prep — ablations, literature | Slots w/c 7 & 14 Dec |

**Feature freeze:** 12 Dec — parameters and weights only.

---

## 6. People: workstreams and independence

| Stream | Owner | Owns (files) | Depends on | Week 1 output |
|--------|-------|--------------|------------|---------------|
| **A — Platform** | Person A | `MyAgent.py` glue, `config.py`, `core/`, Docker, `build.sh`, `tests` | Engine API | Legal random/agent |
| **B — Search** | Person B | `search/` | `core` API frozen by Wed W1 | Random MCTS |
| **C — Knowledge + bench** | Person C | `knowledge/`, `bench/` | `core` | Win/block, bench harness |
| **D — ML (after W1)** | Person D | `ml/`, `weights/` | `core.to_planes`, C's data schema | Schema doc + empty loader |

**C also owns Hex tactics + openings** so B stays in search/parallelism.

**Cross-team rituals:**

- **Daily (async):** 2-line status in group chat.
- **2×/week:** 30 min merge — integrate to `main`, run 5-game smoke test.
- **Friday 17:00:** diary + minutes before 18:00 deadline.

---

## 7. GitLab-ready epics and issues (backlog sketch)

Use labels: `stage-1`, `stage-2`, `stage-3`, `owner-A`…`owner-D`, `blocking`, `journal-evidence`.

### Epic: Stage 1 — Shippable bot (P0)

| Issue | Owner | Acceptance criteria |
|-------|-------|---------------------|
| Docker amd64 + dev README for team | A | All members run `Hex.py` vs Naive |
| `core.BoardState` from engine `Board` | A | Unit test round-trip |
| Root win/block | C | Tests: win in 1, block in 1 |
| Bridge reply in rollout | C | Regression position from literature |
| UCT MCTS + time manager | B | Never TIMEOUT in 20 games |
| Two-distance eval | C | Used in rollout or progressive bias |
| Opening book + swap | C | Swap only t=2 Blue |
| Parallel root MCTS | B | Uses ≤8 CPUs on your turn |
| `check_submission.py` pass | A | No FAIL in dry run |
| **Milestone: 14 Dec submit** | A | Staff email received |

### Epic: Evaluation (P0 — start week 1)

| Issue | Owner | Acceptance criteria |
|-------|-------|---------------------|
| Batch runner both colours | C | CSV: wins, mean ns/move |
| Version tags in logs (`v1.0-stage1`) | C | Reproducible `--seed` |
| Journal experiment template | C | Table for approach mark |

### Epic: Stage 2 — Teacher + SL (P1, parallel W2–3)

| Issue | Owner | Acceptance criteria |
|-------|-------|---------------------|
| Teacher config: 30–60 s/move, multi-process | C | Writes `data/teacher.jsonl` |
| Pattern-feature SL student v0 | D | Beats uniform prior on holdout |
| Tiny CNN student v1 (optional) | D | <5MB, <50ms CPU forward in Docker |
| Colab notebook + export script | D | Documented in repo |

### Epic: Stage 3 — Match integration (P2, W3–4)

| Issue | Owner | Acceptance criteria |
|-------|-------|---------------------|
| `USE_STUDENT` flag + fallback | A | Student off = Stage 1 behaviour |
| PUCT or root prior only | B | No inference in rollout loop |
| A/B 100+ games + decision doc | C+D | Journal + keep/kill decision |
| Final tar + statement PDF | A | 18 Dec checklist |

### Epic: Course admin (P0)

| Issue | Owner | Acceptance criteria |
|-------|-------|---------------------|
| Proforma filled | All | 27 Nov journal |
| Individual diary ×4 marked weeks | All | Canvas |
| Group minutes ×4 | Rotating | Canvas |
| Presentation | All | Slots Dec |

---

## 8. Risk register (plan assumptions)

| Risk | Mitigation |
|------|------------|
| Stage 2 slips | **14 Dec Stage 1 already submitted** |
| Student slows bot | Root-only prior; A/B speed column |
| Python too slow | Escalate B to C++ `search/` mid W2 — agree in pre-flight |
| External teacher not allowed | Only own MCTS teacher — still valid distillation story |
| Merge conflicts | Thin `MyAgent`; freeze `core` API end W1 |

---

## 9. Proforma / statement one-liner

> We implement **parallel MCTS with Hex tactical knowledge, two-distance evaluation, and pie-rule opening/swap heuristics** (MoHex-inspired). **Offline**, we **distil** a strong slow MCTS teacher into a **fast student** (supervised policy features / small CNN) used only as a **search prior** after A/B testing. Final submission always retains a **fallback** to the Stage 1 bot.

---

*Direction document for issue tracking. Update when pre-flight decisions (Section 1) are recorded.*