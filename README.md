# osdev: an asys team for operating-system development

This directory holds an [asys](https://github.com/glguida/asys) environment
and workflow for building operating systems with a team of agents. The work is
specified, planned, implemented, tested and reviewed in stages. A Senate of
specialists makes the decisions, and you have the final say.

```text
~/osdev/
  env/osdev/          the environment: image, agents, Senates, skills, programs
  workflow/           the workflow: osdev.yaml and the files it calls
  exok/               a project: the MIT exokernel on NUX (the first task)
  exok-request.md     that project's request
```

The environment is not tied to one project. Each task is a separate workspace
(a git repository) plus a request file describing what to build.

## 1. Install asys

asys builds from its repository (`git@github.com:glguida/asys.git`; the local
checkout is `~/asys`). Its `INSTALL.md` is the authority; in short:

**Requirements.** Linux, GNU Make, Python 3.10+, Go 1.25+, Docker Engine 23+
with BuildKit usable by your user, and dcomp 0.3.2+ (`dcomp` and `dcomp-proxy`
on `PATH`).

```sh
cd ~/asys
make install            # builds commands and images; installs to ~/.local
export PATH="$HOME/.local/bin:$PATH"
asys version            # installed release, images, and the services' builds
```

**Choose a state directory.** It holds runs, inference and human state. You
can use a private one:

```sh
asys init ~/asys-state
. ~/asys-state/asys-env
```

or the shared system on this machine, which needs membership of the `asys`
group:

```sh
. /mnt/asys/asys-env    # ASYS_STATE_ROOT=/mnt/asys, DCOMP_STATE_ROOT=/mnt/dcomp
```

After being added to the group, a session started earlier does not have it
yet. Use `newgrp asys` in that shell, or run single commands through
`sg asys -c '...'`. `sg` needs you listed in `/etc/gshadow`; `sudo gpasswd -a
$USER asys` does both.

**Start inference and pick models** (the shared system already has this set
up):

```sh
asys-inference init && asys-inference start
asys-inference gateway login openai-codex --as work
asys-inference models                       # the model IDs you can use
```

This environment names its model explicitly (`pool/gpt-6.1-sol`) in every
worker. If your gateway does not export that ID, change the `model` fields in
`env/osdev/workers/*.json`.

**Skills for coding agents** (optional): `asys skill ~/.claude/skills` exports
the `asys` and `asys-authoring` skills.

## 2. The environment (`env/osdev`)

### What the image contains

Built on the `asys-workers` image of the installed release (Debian 12):

| | |
| --- | --- |
| Cross toolchains | `amd64-`, `i686-`, `riscv64-unknown-elf` GCC 14.2.0 and binutils 2.43.1, built with [gcc_toolchain_build](https://github.com/glguida/gcc_toolchain_build) into `/opt/cross-toolchain` |
| Emulation | QEMU 10.0.2 (`qemu-system-i386`, `-x86_64`, `-riscv64`) with OpenSBI 1.5.1 and OVMF |
| Debugging | `gdb` and `gdb-multiarch` 13.1 |
| Build and source tools | autotools, bison, flex, `dtc`, mtools, dosfstools, `indent`, ctags, cscope, ripgrep, xxd |
| Literature | the `exokernel` skill: 25 MIT exokernel papers and theses as PDF and searchable text, with an annotated index |

`env/osdev/tools.md` lists every tool and its version. The agents read it.

Workers have outbound network access (`"egress": true` in `workers.json`), so
they can clone sources and download specifications. Egress alone gives them no
web-search tool; see `~/pcb-engineer/env/kicad` for how one is added.

### Building the image

asys builds the image from `env/osdev/Dockerfile` when a run starts. The first
build compiles the three cross toolchains, which takes about 25 minutes. After
that the build cache makes rebuilds take seconds.

The toolchains are rebuilt only when the first stage of the Dockerfile (the
`FROM debian:bookworm AS cross-toolchain` block) changes, when Docker's build
cache is cleared, or when a newer `debian:bookworm` is pulled. Editing prompts,
workers, skills or the packages in the second stage leaves them cached.

A running run keeps the image it started with. Changes to the environment
apply to new runs, or to a run you upgrade with `asys-run --upgrade RUN`.

### Workers

| Worker | Kind | Responsibility |
| --- | --- | --- |
| `os-architect` | agent | Architecture: kernel/userspace division, interfaces, memory and protection |
| `hardware-expert` | agent | Correctness against x86 and RISC-V hardware and firmware specifications |
| `head-of-engineering` | agent | Delivers changes that build on every target and keep the tests passing |
| `head-of-qa` | agent | Independent verification: builds, tests and debugs the work |
| `head-of-performance` | agent | Measures and improves the cost of low-level mechanisms |
| `head-of-anti-bloat` | agent | Keeps the system minimal |
| `goal` | goal | Implements, then is checked by an independent verifier; at most 8 attempts |
| `senate-architecture` | senate | The six heads judge the specification; the OS Architect weighs most |
| `senate-test-plan` | senate | They judge the test plan; the Head of QA weighs somewhat more |
| `senate-planning` | senate | A short session choosing the next job; Engineering and QA lead |
| `senate-review` | senate | They judge a finished job; all equal |
| `senate-plenary` | senate | They judge the whole project; all equal |
| `senate` | senate | The six heads on any question you put to them |
| `flow-recovery` | agent | Decides where the workflow resumes after a failure |
| `git` | program | Commits and resets job work (`programs/git_step.py`) |
| `human` | program | Asks you a question through the Human service |

Every Senate has a neutral chair, the *Princeps senatus*, who decides on the
strength of the arguments. Prompts are in `env/osdev/agents/NAME/prompt.md`.
The agents are not tied to any particular OS project: they take their goals
from the workspace and the request.

The agents and Senates also run on their own, outside the workflow:

```sh
asys-run ~/osdev/env/osdev os-architect "Review the page-table design in docs/" --workspace PROJECT
asys-run ~/osdev/env/osdev senate "Should the scheduler live in the kernel?" --workspace PROJECT
```

To change the environment, use the asys tools:

```sh
asys-workers list ~/osdev/env/osdev
asys-workers edit ~/osdev/env/osdev head-of-qa          # a worker definition
asys-environment edit ~/osdev/env/osdev agents/head-of-qa/prompt.md
asys-environment add-skill ~/osdev/env/osdev ./my-skill
```

## 3. The workflow (`workflow/osdev.yaml`)

```text
architecture ──► test plan ──► cycle (repeat until the plan is done) ──► plenary ──► you
   goal writes       goal writes     senate-planning: next job + design       │
   the spec          the test plan   git begin                                │ approved ──► end
   senate-           senate-         goal implements ─► QA tests ─►           │ revise ────► cycle
   architecture      test-plan       senate-review ─► git commit              │ rejected ──► architecture
   (3 rounds)        (3 rounds)      (3 rounds, then discard and replan)      │
```

1. **Architecture.** A goal writes `docs/spec/architecture.md`: requirements,
   architecture, and a *plan of work* in stages, each divided into finite jobs
   with IDs (S1-J1, ...), dependencies and acceptance criteria. The
   architecture Senate approves it or returns findings, and the goal revises.
   That is up to 3 rounds.
2. **Test plan.** The same, for `docs/spec/test-plan.md`: how every job is
   verified, and what counts as a pass.
3. **Cycle.** The planning Senate picks the next job and writes its design to
   `docs/jobs/JOB/design.md`, logging it in `docs/jobs/log.md`. A goal
   implements it, the Head of QA tests it independently and writes
   `docs/jobs/JOB/test-report.md`, and the review Senate approves it or returns
   findings. A rejected job is fixed up to 3 times. After that it is discarded
   and planning redesigns or splits it. The cycle repeats until the planning
   Senate declares the plan finished.
4. **Plenary.** The plenary Senate examines the whole project, writes
   `docs/plenary/report.md` and proposes a verdict. **You confirm or override
   it:** approved ends the run, revise sends its bugs back into the cycle, and
   rejected sends the project back to architecture.

**Version control.** The workspace is a local git repository, and nothing is
pushed. The agents commit their own work. The `git` step marks each job's
starting point (`refs/osdev/job-base`), and records each round with its review
verdict. A job rejected three times is reset to that starting point.

**Failures.** Any failing stage goes to `flow-recovery`, which reads the
failure and the workspace, then resumes the right stage with guidance,
escalates to you, or aborts. It keeps `docs/flow/recovery-log.md` and
escalates rather than retrying the same cause a third time. A stage that is
still not approved after its 3 rounds also comes to you.

**You are asked only** for the plenary verdict and for escalations.

## 4. Running a task

**1. Create the project workspace.**

```sh
mkdir ~/osdev/myos && cd ~/osdev/myos && git init
```

**2. Write the request.** Keep it outside the workspace, so it does not end up
in the project's commits. Say what to build, the authorities to follow, the
targets, the constraints and the deliverables. `exok-request.md` is a worked
example.

**3. Check and start.** Use tmux or screen, because a run takes hours or days:

```sh
. /mnt/asys/asys-env                      # or your own state's asys-env
asys workflow check ~/osdev/workflow/osdev.yaml --environment ~/osdev/env/osdev
asys-run ~/osdev/env/osdev ~/osdev/workflow/osdev.yaml \
  --input ~/osdev/myos-request.md --workspace ~/osdev/myos --name myos
```

**4. Follow it.**

| | |
| --- | --- |
| `asys ps` / `asys status RUN` | runs; one run's steps and their state |
| `asys top RUN` | live jobs and transcripts |
| `asys logs RUN [JOB]` | saved output of the run or of one worker |
| `asys dashboard` | workflow map, transcripts, Senate debates |
| `asys dashboard --run RUN --port 8765` | a dashboard that serves this run only |
| `asys-flow-view -run RUN` | the workflow graph, live (X11) |
| `git -C ~/osdev/myos log` | what each round produced, and each verdict |

`RUN` is an ID, a unique prefix of it, or `latest`. `--run` is in asys
commit `8a34660`, so `make install` from `~/asys` first. To share a dashboard,
use an SSH tunnel with the same port on both ends
(`ssh -L 8765:127.0.0.1:8765 host`), because it only answers requests
addressed to `localhost`. Whoever has it can still cancel the run's jobs.

**5. Answer questions** when the run asks for you:

```sh
asys-human-prompt                         # or the dashboard
```

**6. Recover.** If a run fails outside the workflow's own recovery:

```sh
asys-run --resume RUN                     # retry the failed stage, keeping finished work
asys-run --upgrade RUN                    # pick up environment changes, then resume
```

## 5. What to expect

Timings from the exok run: writing the specification took about 20 minutes,
and a Senate round about 30 minutes, since all seven members speak.
Implementing and verifying a job takes one to several hours. Expect a project
to take days, and plenty of model calls.

Verification is thorough. In exok's first job, the goal's verifier and then
QA each wrote their own adversarial tests and found a real defect in the test
runner. The job went back for fixes rather than being approved.

Each session's chair writes the session's document: the planning chair the
job design, the plenary chair its report. When a run looks stuck, check that
these appear in the workspace.
