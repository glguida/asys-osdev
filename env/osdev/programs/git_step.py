"""Version-control steps of the OS development flow.

  begin JOB_ID TITLE           commit pending work as the job's base and mark it
  commit JOB_ID TITLE MESSAGE  commit one implementation round
  discard JOB_ID REASON [--fail]  reset the tree to the job's base; with --fail,
                                 also fail the step so recovery handles it

The workspace is the git repository; it is created when missing. Commits stay
local. The job base is kept in refs/osdev/job-base.
"""
import json
import os
import subprocess
import sys

BASE = "refs/osdev/job-base"


def git(*args, check=True):
    result = subprocess.run(["git", "-c", "safe.directory=*", *args],
                            capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if check and result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed with status {result.returncode}")
    return result.stdout.strip()


def commit_all(message):
    git("add", "-A")
    if not git("status", "--porcelain"):
        return None
    git("commit", "-q", "-m", message)
    return git("rev-parse", "HEAD")


def head():
    return git("rev-parse", "--verify", "-q", "HEAD", check=False) or None


def main(action, job_id, *rest):
    if action == "begin":
        if not os.path.isdir(".git"):
            git("init", "-q")
        commit = commit_all(f"{job_id}: design\n\n{rest[0]}")
        if head() is None:
            git("commit", "-q", "--allow-empty", "-m", f"{job_id}: design")
        git("update-ref", BASE, "HEAD")
        return {"action": action, "job_id": job_id, "base": head(), "committed": commit is not None}
    if action == "commit":
        title, message = rest
        # Workers often commit their own work; always record the round's
        # review outcome, with an empty commit when nothing is pending.
        git("add", "-A")
        git("commit", "-q", "--allow-empty", "-m", f"{job_id}: {title}\n\n{message}")
        return {"action": action, "job_id": job_id, "commit": head(), "committed": True}
    if action == "discard":
        base = git("rev-parse", "--verify", "-q", BASE, check=False)
        if not base:
            raise SystemExit("no job base recorded; refusing to discard")
        discarded = git("rev-parse", "HEAD")
        git("reset", "-q", "--hard", base)
        git("clean", "-q", "-fd")
        summary = f"job {job_id} discarded (reset {discarded} to base {base}): {rest[0]}"
        if "--fail" in rest[1:]:
            raise SystemExit(summary)
        return {"action": action, "job_id": job_id, "discarded": discarded, "base": base,
                "summary": summary}
    raise SystemExit(f"unknown action {action}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    result = main(*sys.argv[1:])
    with open(os.environ["ASYS_RESULT"], "w", encoding="utf-8") as out:
        json.dump(result, out)
