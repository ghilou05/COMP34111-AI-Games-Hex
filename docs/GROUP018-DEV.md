# Group 18 — local dev setup

Course environment notes for **COMP34111 Hex** (marking runs in the repo’s Docker image on **linux/amd64**). Full rules: [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md). Engine overview: [README.md](../README.md).

## Prerequisites

- Docker Desktop (or Docker Engine) with bash
- This repo cloned locally
- **Do not change** the root `Dockerfile` (see checklist §1)

## Build the image

From the repository root:

```bash
docker build -t hex .
```

**Apple Silicon Mac:** build an x86-64 image so binaries match the marking machine:

```bash
docker build --platform linux/amd64 -t hex .
```

Optional (compiled agents): build the build-stage image — see [README.md](../README.md).

## Run the container

Linux, macOS, or WSL (bash) — commands from the README:

```bash
docker run -it --cpuset-cpus=0-7 --memory=16g --name hex -v "$(pwd)":/home/hex hex bash
```

If your machine has **fewer than 8 CPUs**, omit `--cpuset-cpus=0-7`. Marked games use up to 8 vCPUs and **16 GB RAM for both bots together** (8 GB each).

Inside the container, the working directory is `/home/hex` (this repo, bind-mounted).  
`exit` stops the session; `docker start -i hex` reattaches; `docker rm hex` removes the container.

## Play games

Default: two `NaiveAgent` instances:

```bash
python3 Hex.py
```

Named agents (README format):

```bash
python3 Hex.py -p1 "agents.Group007.MyAgent MyAgent" -p2 "agents.DefaultAgents.NaiveAgent NaiveAgent"
```

For Group 18 (once `agents/Group018/` exists in Issue 2), use `agents.Group018.<module> <ClassName>` instead of `Group007`.

All options:

```bash
python3 Hex.py --help
```

Example smoke test after your bot exists:

```bash
python3 Hex.py -p1 "agents.Group018.MyAgent MyAgent" -p2 "agents.DefaultAgents.NaiveAgent NaiveAgent" --seed 1 -l test1.log
```

Run games **inside the container** for the same environment as marking.

## Check submission

```bash
python3 check_submission.py 18
```

(`Group018` is the folder name for group number 18; the script takes the numeric group id.)

**Until Issue 2** scaffolds `agents/Group018/`, this command is expected to **FAIL** with `agents/Group018 does not exist`. Fix failures before Canvas submission — see [SUBMISSION-CHECKLIST.md](SUBMISSION-CHECKLIST.md) §4.

## Unit tests

```bash
python3 -m unittest discover
```

## Week 1 acceptance (Issue #1)

Each member should:

1. Build `hex` with `--platform linux/amd64` on Apple Silicon (or plain `docker build` on amd64 Linux).
2. Start the container with `--memory=16g` and `--cpuset-cpus=0-7` when possible.
3. Run `python3 Hex.py` (Naive vs Naive) successfully inside the container.

Next platform issue: scaffold `agents/Group018/` so `check_submission.py 18` can load the folder.