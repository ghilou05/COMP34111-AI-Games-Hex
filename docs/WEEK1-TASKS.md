# Week 1 tasks (Group 18)

Derived from [`research/2026-11-26-four-week-team-plan.md`](../research/2026-11-26-four-week-team-plan.md) (calendar §5, epics §7, pre-flight §1).  
**Week 1 window:** 26 Nov – 2 Dec.

Use this if GitHub Issues is off on the course fork. To import to GitHub: **Settings → General → Issues → Enable**, then run the commands in [Import to GitHub Issues](#import-to-github-issues) or paste titles into the issue form.

| Status | Owner | Task | Done when |
|--------|-------|------|-----------|
| ☐ | **A** Abs | Docker `linux/amd64` + team dev setup | All four run `python3 Hex.py` vs Naive in container |
| ☐ | **A** | Scaffold `agents/Group018/` (`cmd.txt`, `MyAgent`, `config.py`, package tree) | `check_submission.py 18` can find folder/cmd |
| ☐ | **A** | `core.BoardState` + publish integration contract | Round-trip unit test; API frozen by **Wed W1** |
| ☐ | **A** | `MyAgent` legal play vs NaiveAgent | Full game both colours, no CRASH/TIMEOUT/BAD_MOVE |
| ☐ | **B** Laymoi | `search/` skeleton MCTS (UCT, random rollouts) | 10 games without crash |
| ☐ | **B + C** | Agree Stage 1 **time-budget** constants (pre-flight #10) | Documented in `config.py` / minutes |
| ☐ | **C** Ghiles | Root **win/block** in `knowledge/` | Unit tests: win in 1, block in 1 |
| ☐ | **C** | `bench/` harness stub (optional W1) | Can run a scripted series from CLI |
| ☐ | **D** Idris | ML schema doc + empty `policy_prior` loader | No blocker for B; `USE_STUDENT=False` |
| ☐ | **D + one** | Pre-flight spike: NaiveAgent timings + `check_submission.py` dry run | Notes in group chat / journal |

**Cross-team:** 2×/week merge to `main` + 5-game smoke; Friday diary/minutes (Canvas).

---

## Import to GitHub Issues

Repo: `ghilou05/COMP34111-AI-Games-Hex` — **Issues are currently disabled**; a maintainer must enable them before `gh issue create` works.

Labels created (if Issues enabled): `week-1`, `stage-1`, `owner-A` … `owner-D`.

Example (repeat per row after enabling Issues):

```bash
gh issue create --repo ghilou05/COMP34111-AI-Games-Hex \
  --title "[W1][A] Docker amd64 + team dev setup" \
  --label "week-1,stage-1,owner-A" \
  --body "Acceptance: All four members run Hex.py vs Naive in amd64 Docker."
```

See plan epic table for Stage 1 items that spill into week 2 (two-distance, opening book, parallel MCTS, etc.).