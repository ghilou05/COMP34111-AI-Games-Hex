# Group 018 integration contract (v0.1)

**Owner:** A (Abs) · **Group:** 18 · **Path:** `agents/Group018/`

**API freeze:** **Sunday 2 Dec 2026** (end of week 1). After that, **breaking changes** to signatures or semantics require agreement in **team chat** and an update to this document.

**Public entry:** `MyAgent.py` (`AgentBase`). All other packages are internal.

---

## Architecture (from team plan §3)

```
Group018/
  cmd.txt
  MyAgent.py
  build.sh                # optional compiled search
  config.py
  core/                   # board copy, move gen, connectivity, ML planes
  search/                 # MCTS, parallel root, time budget
  knowledge/              # win/block, bridges, openings, swap
  bench/                  # batch runner, stats, teacher data
  ml/                     # train scripts, student loader, inference
  weights/
  tests/
```

---

## Contract table

| Module | Provides | Consumes |
|--------|----------|----------|
| `core` | `BoardState`, `legal_moves()`, `apply_move()`, `has_won(colour)`, `to_planes()` | Engine `Board` / `Move` / `Colour` |
| `knowledge` | `tactical_move`, `opening_move`, `should_swap`, `evaluate` | `core` |
| `search` | `best_move` | `core`, `knowledge` |
| `ml` (student) | `load`, `policy_prior` | `core` (optional at runtime) |
| `bench` | `play_series`, `write_teacher_row` | CLI, `config` paths |

---

## `core` (implemented — frozen v0.1)

```python
# agents/Group018/core/board_state.py

class BoardState:
    to_play: Colour

    @classmethod
    def from_board(cls, board: Board, *, to_play: Colour = Colour.RED) -> BoardState: ...

    @property
    def board(self) -> Board: ...

    @property
    def size(self) -> int: ...

    def legal_moves(self) -> list[Move]:
        """Empty cells only; swap Move(-1,-1) never listed."""

    def apply_move(self, move: Move) -> BoardState:
        """Place ``to_play`` at (x,y); next state's ``to_play`` is opponent."""

    def has_won(self, colour: Colour) -> bool:
        """Delegates to engine connectivity (``Board.has_ended``)."""

    def to_planes(self) -> numpy.ndarray:
        """Shape (3, size, size), float32 in {0,1}.
        Channel 0: stones of ``to_play``; 1: opponent; 2: empty."""
```

**Import:** `from agents.Group018.core import BoardState`

---

## `knowledge` (stubs — not implemented week 1)

```python
# agents/Group018/knowledge/__init__.py — TBD

def tactical_move(state: BoardState) -> Move | None:
    raise NotImplementedError

def opening_move(state: BoardState) -> Move | None:
    raise NotImplementedError

def should_swap(state: BoardState, opp_move: Move) -> bool:
    raise NotImplementedError

def evaluate(state: BoardState) -> float:
    raise NotImplementedError
```

---

## `search` (stubs)

```python
# agents/Group018/search/__init__.py — TBD

def best_move(
    state: BoardState,
    budget_sec: float,
    priors: dict[tuple[int, int], float] | None = None,
) -> tuple[int, int]:
    raise NotImplementedError
```

---

## `ml` / student (stubs)

```python
# agents/Group018/ml/__init__.py — TBD

def load(weights_path: str) -> None:
    raise NotImplementedError

def policy_prior(
    state: BoardState,
    legal: list[Move],
) -> dict[tuple[int, int], float]:
    raise NotImplementedError
```

**Rule:** Student inference is **never required** for legal play (`config.USE_STUDENT = False` default).

---

## `bench` (stubs)

```python
# agents/Group018/bench/__init__.py — TBD

def play_series(
    *,
    games: int,
    seed: int,
    log_path: str,
    version_tag: str,
) -> None:
    raise NotImplementedError

def write_teacher_row(
    state: BoardState,
    policy: dict[tuple[int, int], float],
    out_path: str,
) -> None:
    raise NotImplementedError
```

---

## Integration rule (team plan)

Stage 2/3 **must not** replace `search` until `bench` shows a win-rate gain after speed adjustment.