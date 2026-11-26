# Building Strong Hex Agents: Research Brief for COMP34111-Style Coursework

**Purpose:** Inform a 4-person undergraduate team (~1 semester) choosing algorithms, heuristics, and architecture for an 11×11 Hex bot in the UoM COMP34111 engine.

**Research question:** What Hex AI approaches are credible in research, and which are realistically achievable under COMP34111 constraints (5 min/match, 8 CPUs, no GPU, pie rule, human-written code)?

**Author context:** Repository is the official 2026–2027 COMP34111 Hex engine (`docs/GAME.md`); marking uses last year’s class bots plus speed ranking.

**Date:** 2026-11-26

**Research verified:** Yes (≥12 corpus sources; course rules from local `docs/GAME.md`)

**Follow-on memos (extensions 3 / 4 / 5):**

- [Hex extensions 3–4–5 — full comparison](./2026-11-26-hex-extensions-3-4-5.md) ([global-research](23b32825-5446-48e1-b37f-972007e277ba))
- [Hex extensions — **5-week** calendar plan](./2026-11-26-hex-extensions-3-4-5-five-weeks.md)

---

## Executive Summary

Hex is a **perfect-information, connection game** on an 11×11 rhombus: Red connects top–bottom, Blue connects left–right; **pie rule** on turn 2. Industrial-strength play combines **Monte Carlo tree search (MCTS)** with **Hex-specific knowledge**—especially **virtual connections (VCs)**, **inferior-cell pruning**, and strong **local evaluators** (two-distance or resistance). The reference stack is the University of Alberta **Benzene** project (**MoHex**, **Wolve**, solvers), not a single “minimax only” design.

For a **student team in one semester**, the best effort/strength tradeoff is usually:

| Rank | Approach | Effort | Expected strength | Fit for marking |
|------|-----------|--------|-------------------|-----------------|
| **1** | **MCTS + light Hex knowledge** (bridge replies, immediate win/block, simple two-distance or resistance eval, move filters) | Medium | **High among peers** | Strong; scales with 8 CPUs if search runs only on your turn |
| **2** | **Iterative deepening αβ + two-distance eval + tactical extensions** | Medium–high | High in tactics; weaker in murky midgame | Good if time mgmt is careful (speed mark matters) |
| **3** | **MCTS + opening book + swap heuristics** (HexWiki-style balanced openings) | Low–medium | Reliable vs random/naive; modest vs search bots | Easy win-rate gains |
| **4** | **MoHex-style full VC engine + pattern priors** (ported from Benzene ideas) | **Very high** | Near-research quality *if* finished | Risky scope for 4 students |
| **5** | **Train CNN/AlphaZero-style net + MCTS** (PyTorch CPU at tournament time) | **Very high** | Can dominate *if* pipeline works | Heavy infra; marking has **no GPU**; coursework is **AI-prohibited for submitted code** (design from papers OK, code must be human-authored) |
| **6** | **Plain minimax / random MCTS** | Low | Baseline | Insufficient for top marks |

**Naming note:** The canonical MCTS+Hex paper is **Arneson, Hayward, Henderson** (“MoHex,” IEEE TCIAIG 2010)—often confused with “Aravindh” (unrelated chess context). Key follow-ups: **MoHex 2.0** (Huang et al., pattern-based MCTS), **FastVC** (Pawlewicz et al.), **DeepHex** (sibling conspiracy number search), **Gao et al.** (CNN / three-head nets).

**Marking reality check (from `docs/GAME.md`):** 40 games vs last year’s bots; win component 50 + wins (max 90); speed vs cohort (50–90%); combined **(3×win + speed)/4**; **5 min total** per player per game; agent **frozen on opponent’s turn** (no background MCTS). Design for **anytime search**, **per-move budgets**, and **fast init** (≤3 min).

---

## Landscape map (variants considered)

| ID | Variant | Who uses it | Distinct rules / economics |
|----|---------|-------------|---------------------------|
| A | Pure αβ / minimax + static eval | Queenbee, Wolve, student bots | Depth-limited; wins on clarity, loses in depth/branching |
| B | MCTS / UCT (+ RAVE) | MoHex, Fuego family, many student bots | Anytime; needs playout policy; strong with priors |
| C | MCTS + VC / inferior-cell engines | MoHex, MoHex 2.0 | Prunes tree; **mustplay** when opponent has winning SC |
| D | Proof-number / DFPN / SCNS solvers | Benzene solver, DeepHex | Proves wins in endgame; Olympiad bots use parallel DFPN alongside MCTS |
| E | Pattern-based move priors & playouts | MoHex 2.0, MoHex-CNN | Learned weights from self-play data |
| F | Neural move prediction / value (CNN, ResNet) | MoHex-CNN, Gao IJCAI’18, neurobenzene | Policy priors or leaf eval; training is GPU-heavy |
| G | AlphaZero-style self-play + MCTS | Strong past course projects (e.g. public repos) | Best ceiling; highest integration risk under CPU-only marking |
| H | Opening books + swap policy only | Human-style bots | Cheap Elo vs weak fields; plateaus vs search |
| I | Electrical resistance / flow eval | Shannon, Anshelevich, Hexy | Fast global heuristic; good for ordering, not alone |
| J | Two-distance + mobility (Queenbee) | Wolve default eval family | Standard αβ eval; well-documented |
| K | External engine wrapper | Benzene CLI | Strong for **testing**, usually **not** allowed as submission if policy forbids third-party engines—confirm brief |

---

## 1. Hex rules and win conditions (brief)

**Board:** 11×11; neighbours are the six hex-adjacent cells (see engine doc for exact indexing). **Red (P1)** connects **rows 0 and 10**; **Blue (P2)** connects **columns 0 and 10**. Players alternate placing stones on empty cells.

**Win:** First player to connect their two sides with a **monochrome path** wins. Draws are impossible on standard boards (strategy-stealing / topology arguments—see [Wikipedia: Hex](https://en.wikipedia.org/wiki/Hex_(board_game))).

**Pie rule (swap):** On **turn 2 only**, Blue may play `Move(-1, -1)` to swap colours (engine implements “swap sides”). Red should open with **balanced** moves—not center-too-strong, not weak edge moves—so Blue’s swap decision is hard ([HexWiki swap rule](https://www.hexwiki.net/index.php/Swap_rule)).

**Course specifics:** 5 minutes **total** move time per player; 3 minutes max `__init__`; illegal swap or bad `Move` ⇒ instant loss.

---

## 2. State of the art and classical approaches

### 2.1 Minimax / alpha–beta (Wolve lineage)

Classical **αβ with move ordering**, **transposition table**, **selective extensions** was the pre-MCTS standard. **Wolve** (Benzene) combines αβ with VC/inferior machinery; **Queenbee** used two-distance eval + selective deepening ([van Rijswijck MSc thesis](https://sites.ualberta.ca/~hayward/theses/jackmsc.pdf)).

**Strengths:** Precise in tactical lines; good teaching path from CS courses. **Weaknesses:** Branching factor ~100+ on 11×11; without Hex pruning, depth is shallow.

### 2.2 MCTS / UCT (+ RAVE)

**MoHex** (Arneson et al., 2010) uses **Fuego** MCTS with **UCT + RAVE**, runs VC/inferior analysis on **heavy nodes**, simulates on a **reduced equivalent board**, and runs a **parallel DFPN solver** for solved subgames ([MCTS in Hex PDF](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)).

**MoHex 2.0** adds **learned pattern weights** for in-tree priors and softmax playouts—large Elo gain over MoHex 1.x on 11×11 and 13×13 ([MoHex 2.0 paper](https://sites.ualberta.ca/~hayward/papers/m2.pdf)).

### 2.3 Virtual connections and patterns

**Anshelevich H-search** iteratively builds **virtual connections** (VC) and **virtual semi-connections** (SC) via AND/OR rules on carriers ([Anshelevich, AI 2002](https://www.cs.auckland.ac.nz/courses/compsci767s2c/resources/VAnshelevich-ARTINT.pdf)). **Incomplete** but fast; underpins pruning.

**Mustplay:** If opponent has a **winning SC**, your moves outside its carrier are **provably losing**—MoHex exploits this heavily.

**FastVC Search** improves VC discovery for MCTS pruning ([Stronger VCs](https://sites.ualberta.ca/~hayward/papers/strongervcs.pdf)).

**Patterns:** Bridges (two-cell VC), **savebridge** in MoHex playouts, local **dead/vulnerable/captured** cells ([Henderson PhD](https://sites.ualberta.ca/~hayward/theses/ph.pdf), [dead cell paper](https://sites.ualberta.ca/~hayward/papers/bergeParis.pdf)).

### 2.4 Proof-number search (not quite “Monte Carlo” PN)

**DFPN** and **Scalable Parallel DFPN** solve many 9×9 openings and some 10×10 ([Pawlewicz & Hayward, CG 2013](https://sites.ualberta.ca/~hayward/papers/pawlhayw.pdf)). MoHex runs DFPN **on separate threads** during search.

**DeepHex** uses **Sibling Conspiracy Number Search** with a **local** resistance-style heuristic; competitive with MoHex at long time controls ([SCNS / DeepHex](https://sites.ualberta.ca/~hayward/papers/cnsrss.pdf), [2015 Olympiad report](https://sites.ualberta.ca/~hayward/papers/rptLeiden15.pdf)).

### 2.5 Neural networks

**MoHex-CNN** (Gao, Hayward, Müller): CNN **move prediction** from MoHex 2.0 self-play—net alone ≈ strong eval; boosts MCTS as prior ([IEEE TCIAIG move prediction](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)).

**Three-head net** (policy, state-value, action-value) improves PV-MCTS over two-head ([IJCAI 2018](https://ijcai.org/proceedings/2018/523)).

**neurobenzene** integrates TensorFlow inference into Benzene ([GitHub cgao3/neurobenzene](https://github.com/cgao3/neurobenzene)); transferable nets across board sizes ([transfer learning paper](https://sites.ualberta.ca/~hayward/papers/transferable.pdf)).

**Student feasibility:** Inference in **CPU PyTorch** is allowed in the Docker image; **training** is off-machine. Past strong submissions combined **C++/Java MCTS + small ResNet** (public course forks). Full AlphaZero parity with MoHex is a **multi-month systems project**, not a default plan.

---

## 3. Realistic approaches for a 4-person undergrad team (~1 semester)

### Assumptions

- Mixed Java/Python comfort; no prior Hex AI.
- ~12–14 teaching weeks; parallel coursework.
- Must pass `check_submission.py`, Docker x86-64 rebuild, **human-written** code.

### Recommended phased plan (aligned with effort table)

**Phase 1 (weeks 1–3): Infrastructure + rules**

- Board copy, legal moves, **connectivity win check** (BFS/Union-Find from both goals).
- **Swap logic** on turn 2 (evaluate swap with short rollouts or fixed heuristic).
- Baseline: random + “win now / block opponent win.”

**Phase 2 (weeks 4–7): Core search**

- **MCTS** with time budget per move: `remaining_time / estimated_moves_left`.
- Playout policy: random legal + **bridge defence** (MoHex savebridge pattern).
- Optional **RAVE** for early opening.

**Phase 3 (weeks 8–10): Hex heuristics**

- Implement **two-distance** eval (BFS from each border; second-shortest path idea—[van Rijswijck](https://www.cs.cornell.edu/~adith/docs/y_hex.pdf), [Benzene TwoDistance.hpp](https://benzene.sourceforge.net/benzene-doc/html/TwoDistance_8hpp_source.html)).
- Or **resistance** eval for move ordering only ([Anshelevich circuit model](https://scispace.com/pdf/the-game-of-hex-an-automatic-theorem-proving-approach-to-o8mcidhpwn.pdf)).
- Pattern filter: **fill obvious dead cells** (Figure patterns from Henderson thesis—subset of 5 patterns is enough for pruning junk moves).

**Phase 4 (weeks 11–14): Tournament hardening**

- **Opening repertoire** for Red (e.g. a2/b2/a3 family per [HexWiki opening guide](https://www.hexwiki.net/index.php/Basic_(strategy_guide))).
- **Parallel root-level MCTS** (8 workers; join before returning move—watch **pause** semantics).
- Tune for **speed mark**: median target ~sub-second early, burst on critical moves.
- Regression suite: NaiveAgent, last year’s weak bots, self-play.

### What to avoid in semester scope

- Full **H-search / FastVC** reimplementation (months for correctness + tuning).
- **DFPN solver** as primary move selector (hard to debug; MoHex uses it as helper).
- **Training a strong net from scratch** without existing GPU pipeline and team ML experience.

### Java vs Python

| Layer | Python | Java / C++ |
|-------|--------|------------|
| Agent API | Native `AgentBase` | `ExternalAgent` IPC |
| Search hot loop | OK with NumPy; GIL limits threads | Preferred for parallel MCTS |
| PyTorch inference | Easy | Possible via subprocess or JNI |
| Course friction | Lowest | Extra IPC + build.sh |

**Pragmatic split:** Python orchestration + **C++ or Java search core** compiled with `-march=x86-64-v3` if CPU-bound; keep neural net optional in Python.

---

## 4. Libraries, engines, and key papers

### Engines & codebases

| Resource | Role | Link |
|----------|------|------|
| **Benzene** | MoHex, Wolve, DFPN solver, VC code | [benzene.sourceforge.net](https://benzene.sourceforge.net/) |
| **benzene-vanilla-cmake** | Maintainable CMake build (MoHex 2.0, Wolve) | [cgao3/benzene-vanilla-cmake](https://github.com/cgao3/benzene-vanilla-cmake) |
| **Fuego** | MCTS framework underlying MoHex | [Fuego project](http://sourceforge.net/projects/fuego/) |
| **neurobenzene / mohex3HNN** | DNN integration research fork | [cgao3/neurobenzene](https://github.com/cgao3/neurobenzene) |
| **HexGui** | Visualisation / human play | Linked from Benzene site |

Use these as **opponents and algorithm references**, not necessarily vendored into submission (check academic integrity / brief).

### Papers & theses (student reading list)

| Topic | Citation | URL |
|-------|----------|-----|
| MoHex MCTS + VC pruning | Arneson, Hayward, Henderson, IEEE TCIAIG 2010 | [PDF](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf) |
| MoHex 2.0 patterns | Huang et al. | [PDF](https://sites.ualberta.ca/~hayward/papers/m2.pdf) |
| VC foundations | Anshelevich, AI 2002 | [PDF](https://www.cs.auckland.ac.nz/courses/compsci767s2c/resources/VAnshelevich-ARTINT.pdf) |
| FastVC | Pawlewicz et al. | [PDF](https://sites.ualberta.ca/~hayward/papers/strongervcs.pdf) |
| Inferior cells | Hayward et al. | [PDF](https://sites.ualberta.ca/~hayward/theses/ph.pdf) (Ch. 2.9) |
| Two-distance / search | van Rijswijck | [PDF](https://www.cs.cornell.edu/~adith/docs/y_hex.pdf) |
| Parallel DFPN | Pawlewicz & Hayward | [PDF](https://sites.ualberta.ca/~hayward/papers/pawlhayw.pdf) |
| DeepHex SCNS | Pawlewicz & Hayward | [PDF](https://sites.ualberta.ca/~hayward/papers/cnsrss.pdf) |
| CNN move prediction | Gao, Hayward, Müller | [PDF](https://sites.ualberta.ac.uk/~hayward/papers/movepredhex.pdf) *(use ualberta mirror if needed)* |
| Three-head MCTS | Gao et al., IJCAI 2018 | [Proceedings](https://ijcai.org/proceedings/2018/523) |

### Olympiad benchmarks

MoHex family dominated **Computer Olympiad Hex** 2008–2015 ([Benzene results table](https://benzene.sourceforge.net/), [2015 report](https://sites.ualberta.ca/~hayward/papers/rptLeiden15.pdf)). Useful for **relative** strength claims, not direct mapping to course marks.

---

## 5. Evaluation functions and Hex-specific heuristics

### 5.1 Connectivity and win detection

- **Union-Find** or **BFS** from virtual **super-nodes** on each border edge—O(n) per check. Run after every simulated move in search.

### 5.2 Two-distance (Queenbee / Wolve)

For each colour, compute distance from each cell to both target edges using **second-shortest-path** logic (opponent can block one shortest route). Aggregate **board potential** = min cell score; **mobility** = count of cells achieving that min. Score ≈ `M·(B−W) − (aB−aW)` ([Queenbee thesis Ch. 5](https://sites.ualberta.ca/~hayward/theses/jackmsc.pdf)).

**Caveat:** Rare positions misclassified as lost ([van Rijswijck counterexample](https://www.cs.cornell.edu/~adith/docs/y_hex.pdf)); combine with win/block overrides.

### 5.3 Resistance (Anshelevich / Shannon)

Model empty=1Ω, own stone=0, opponent=∞; ratio **R_B/R_W** as eval ([circuit model](https://scispace.com/pdf/the-game-of-hex-an-automatic-theorem-proving-approach-to-o8mcidhpwn.pdf)). **Per-cell voltage drop** useful for **move ordering** in SCNS/DeepHex ([CNSRSS paper](https://sites.ualberta.ca/~hayward/papers/cnsrss.pdf)).

### 5.4 Tactical patterns (high ROI for students)

| Pattern | Use |
|---------|-----|
| **Bridge** (2×2 VC) | Playout reply; don’t break own bridges |
| **Immediate win / block** | Mandatory at root |
| **Dead cell patterns** (local templates) | Shrink move list |
| **Mustplay from winning SC** | If you implement partial VCs, only search carrier (advanced) |

### 5.5 MCTS-specific

- **RAVE / AMAF** for Hex: helps when same empty cells touched across simulations (MoHex uses RAVE).
- **PUCT** if using neural policy prior (AlphaZero-style).
- **Progressive bias** from two-distance delta on child moves.

---

## 6. Tournament and benchmark considerations

### Course tournament (`docs/GAME.md`)

| Factor | Implication |
|--------|-------------|
| **40 games** vs fixed pool | Optimise for **consistent** play, not one trick |
| **Both colours** | Red opening + Blue swap policy both matter |
| **5 min chess clock** | ~40–80 moves ⇒ **~4–7 s/move** average if uniform; better to **allocate** |
| **Speed mark 25%** | Wasting 30s every move hurts even with high win rate |
| **Paused on opponent turn** | No pondering; **root reuse** only within your turn |
| **Fresh folder per game** | **Precompute in `__init__`** (opening tables, pattern files); don’t rely on cross-game caches on disk |
| **Seeded RNG** | Engine seeds `random`/NumPy/torch after import—document local RNG for reproducibility |

### Internal benchmarking

1. **Elo or round-robin** vs `NaiveAgent`, in-house MCTS, and **Benzene mohex** with time cap matched to course (CLI opponent).
2. **Opening sweep:** all 121 first moves as Red—measure swap accept rate and win%.
3. **Regression tests:** forced 1-move win, 1-move block, swap turn, timeout near limit.
4. **CI:** `python3 -m unittest discover` + `check_submission.py GroupXYZ` in Docker amd64.

### Interpreting research benchmarks

Olympiad bots use **multi-core, multi-GB, minutes per move**—far above coursework. Scale claims down; prioritise **knowledge per CPU-second**.

---

## 7. Recommended architecture: search vs evaluation vs infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│  Agent façade (Python AgentBase / Java ExternalAgent)      │
│  • Time manager (global 5 min) • Turn/swap policy            │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
│ Search module  │ │ Knowledge     │ │ Infrastructure   │
│ MCTS or αβ     │ │ Board + win   │ │ Board hash/TT    │
│ Parallel root  │ │ Two-distance  │ │ Thread pool      │
│ Move gen       │ │ Patterns      │ │ Logging/tests    │
│ Optional TT    │ │ Opening book  │ │ build.sh         │
└────────┬───────┘ └───────┬───────┘ └──────────────────┘
         │                 │
         └────────┬────────┘
                  ▼
         Optional: NN inference (CPU torch) → policy prior / value
```

**Ownership suggestions (4 students):**

| Student | Module |
|---------|--------|
| A | **Infrastructure** — engine API, time, connectivity, tests, Docker |
| B | **Search** — MCTS/αβ, parallelisation, transpositions |
| C | **Evaluation** — two-distance or resistance, tactical rules, move pruning |
| D | **Opening/swap** + integration — books, tournament tuning, `check_submission` |

**Interface contract:** `BoardState` immutable → `generate_moves()` → `evaluate(state, colour)` → search returns `(x,y)` or swap.

---

## Synthesis across sources

| Claim | Confidence | Notes |
|-------|------------|-------|
| MCTS + Hex knowledge beats plain αβ at 11×11 given equal effort | **High** | MoHex 2009–2015 trajectory; MoHex 2.0 gains |
| VC/mustplay is large strength multiplier for MCTS | **High** | MoHex paper; many losses when missing mustplay |
| Full VC engine is hard for students in one term | **High** | PSPACE complexity of VC set; incomplete H-search |
| Two-distance is best “first real eval” for students | **High** | Documented, used in Wolve/Queenbee; implementable in BFS |
| Neural nets can match strong eval **with search** | **Medium** | Gao papers; training cost ≠ course default |
| DeepHex-style SCNS for undergrad semester | **Low** | Research-grade; better as reading |
| Pie rule changes opening theory materially | **High** | HexWiki + engine rules |

**Tension:** MoHex strength is **not** “MCTS alone”—inferior cells + VCs + solver dominate endgames. Student teams should import **ideas** incrementally rather than cloning Benzene.

---

## Focused implications for COMP34111 team

1. **Default target architecture:** Parallel **MCTS** + **two-distance**-biased playouts + **bridge/tactical** rules + **swap/opening** policy.
2. **Win rate vs speed:** With 75% win / 25% speed in project weighting, prefer **fast early moves** and **spend budget** when eval says position is tight (low margin in two-distance).
3. **Use Benzene** to calibrate: if your bot loses 100% to `mohex` at 3s/move internally, expect similar vs strong class bots until knowledge is added.
4. **Neural path:** Only if one member has ML time **and** team accepts CPU inference limits; use net as **prior**, not sole policy.
5. **Academic integrity:** Research memo and papers OK; **submitted code human-written** per `docs/GAME.md`.

---

## Deprioritized / out of scope

- **Embedding full MoHex/Benzene** as the submitted agent (integrity / LGPL / not the learning goal).
- **Exhaustive VC / solving all openings** on 11×11 (open research problem at long times).
- **GPU-dependent** tournament logic (marking has no GPU).
- **General game AI frameworks** without Hex move pruning (too shallow).
- **Human ladder theory** beyond what patterns/immediate tactics need (defer unless opening phase weak).

---

## Research corpus

| # | Source | Tier | Topic | Key claim |
|---|--------|------|-------|-----------|
| 1 | `docs/GAME.md` (local) | 1 | Course rules | 11×11, pie rule, 5 min, 8 CPU, marking formula |
| 2 | Arneson et al. 2010 | 1 | MCTS+VC | MoHex architecture, mustplay, reduced-board rollouts |
| 3 | Huang et al. MoHex 2.0 | 1 | Patterns | Learned priors + playouts +250 Elo class gains |
| 4 | Anshelevich 2002 | 1 | VC theory | H-search AND/OR rules |
| 5 | Pawlewicz FastVC | 1 | VC speed | Faster VC sets strengthen MoHex |
| 6 | Henderson PhD | 1 | Inferior cells | Dead/vulnerable/captured pruning |
| 7 | van Rijswijck thesis / report | 2 | Two-distance | Standard eval for Queenbee |
| 8 | Pawlewicz DFPN | 1 | Solving | Parallel proof search in Hex |
| 9 | Pawlewicz & Hayward SCNS | 1 | DeepHex | Local heuristic + conspiracy search |
| 10 | Gao move prediction / IJCAI | 1 | Neural | CNN priors for Hex |
| 11 | Benzene project site | 3 | Software | MoHex/Wolve/solver ecosystem |
| 12 | HexWiki swap/opening | 3 | Human theory | Balanced openings, swap heuristics |

---

## Sources

### Primary / academic

- [MoHex MCTS (Arneson, Hayward, Henderson, 2010)](https://sites.ualberta.ca/~hayward/papers/mcts-hex.pdf)
- [MoHex 2.0 (Huang et al.)](https://sites.ualberta.ca/~hayward/papers/m2.pdf)
- [Anshelevich hierarchical Hex](https://www.cs.auckland.ac.nz/courses/compsci767s2c/resources/VAnshelevich-ARTINT.pdf)
- [Stronger VCs (Pawlewicz et al.)](https://sites.ualberta.ca/~hayward/papers/strongervcs.pdf)
- [Henderson PhD thesis](https://sites.ualberta.ca/~hayward/theses/ph.pdf)
- [van Rijswijck: Search and evaluation in Hex](https://www.cs.cornell.edu/~adith/docs/y_hex.pdf)
- [Pawlewicz & Hayward: Scalable Parallel DFPN](https://sites.ualberta.ca/~hayward/papers/pawlhayw.pdf)
- [Pawlewicz & Hayward: SCNS / DeepHex](https://sites.ualberta.ca/~hayward/papers/cnsrss.pdf)
- [Gao et al.: Move prediction CNN](https://sites.ualberta.ca/~hayward/papers/movepredhex.pdf)
- [Gao et al.: Three-head NN (IJCAI 2018)](https://ijcai.org/proceedings/2018/523)

### Industry / community

- [Benzene project](https://benzene.sourceforge.net/)
- [benzene-vanilla-cmake](https://github.com/cgao3/benzene-vanilla-cmake)
- [neurobenzene](https://github.com/cgao3/neurobenzene)
- [HexWiki: Swap rule](https://www.hexwiki.net/index.php/Swap_rule)
- [HexWiki: Basic strategy / openings](https://www.hexwiki.net/index.php/Basic_(strategy_guide))

### Course / local

- [COMP34111 engine `docs/GAME.md`](../docs/GAME.md)
- [Wikipedia: Hex](https://en.wikipedia.org/wiki/Hex_(board_game))

### Illustrative student repos (Tier 4 — anecdotal, not performance guarantees)

- [Ray7788/Hex-Ultra](https://github.com/Ray7788/Hex-Ultra) — staged MCTS → AlphaZero narrative
- Public 2025–2026 course forks (e.g. AlphaZero-style agents on GitHub) — useful for **architecture patterns**, verify claims against your own testing

---

*Global research memo. Wide corpus first; executive summary reflects synthesis filtered to COMP34111 Hex coursework.*