#!/usr/bin/env python3
"""Replay bench for the build and review roles (see README.md).

  bench.py build  cases.toml --builders M[,M...] --judge M[:effort] [--reps 3]
  bench.py review cases.toml --reviewers M[:effort][,...]           [--reps 3]
  bench.py verify cases.toml        (no model: are the checks sound?)
  bench.py report

Every cell (case x arm x repetition) starts from the same frozen snapshot,
runs headless with `claude -p`, and writes one cell.json. A finished cell is
never run again, so an interrupted run continues where it stopped.
"""

import argparse
import csv
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import time
import tomllib
from pathlib import Path

TOOLS = "Bash,Read,Edit,Write,Glob,Grep"
GIT_ID = ["-c", "user.name=bench", "-c", "user.email=bench@localhost"]

BUILD = """\
You are the BUILDER for one work package, in a replay bench. Nobody answers
messages here: your final reply is your message.

Ticket: {inp}/ticket.md (this file is the whole ticket; do not look it up on
GitHub).
Your branch: {branch}. Base: main (tag bench-base).

Read these first and follow them:
1. Your role: {roles}/bootstrap/automation/builder.md
2. {handoff}

This checkout has no remote. Where builder.md says push, commit only. Open no
pull request. Skip the pr-screenshots branch: keep screenshots in {inp}/shots.
End with one reply that starts with READY FOR REVIEW in builder.md's format,
or with "BLOCKED: <one sentence>".
"""

FIX = """\
The reviewer's findings, in full:

{review}

Fix once as builder.md step 5 says and commit. Open no pull request. Reply
with "FIXED <short sha>", what you fixed and what not and why, and for every
command of the ticket whether you re-ran it.
"""

REVIEW = """\
You are the REVIEWER of one branch, with a fresh context, in a replay bench.
You write findings and change nothing: no commit. Nobody answers messages
here: your final reply is your message.

Ticket: {inp}/ticket.md (this file is the whole ticket; do not look it up on
GitHub).
Under review: HEAD @ {sha}. Base: tag bench-base
(`git diff bench-base...HEAD`). There is no remote and no pr-screenshots
branch; screenshots, if any, are in {inp}/shots.

Read these first and follow them:
1. Your role: {roles}/bootstrap/automation/reviewer.md
2. {handoff}

The builder's hand-over message, in full:
{handover}

End with one reply that starts with REVIEW, in the format reviewer.md gives.
"""

GRADE = """\
Compare one code review with a list of known defects. Reply with JSON only:
{{"hit": [<true|false for each known defect, in order>], "extra_must_fix": <number of [must-fix] findings in the review that match no known defect>}}
A known defect is hit only when a finding names the same problem, at any
severity.

Known defects:
{known}

Review:
{review}
"""


def run(cmd, cwd=None, **kw):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True, **kw)


def git(work, *args):
    return run(["git", *GIT_ID, *args], cwd=work).stdout.strip()


def export(repo, commit, dest, paths=()):
    """Copy the files of one commit, without any history."""
    dest.mkdir(parents=True, exist_ok=True)
    tar = subprocess.run(["git", "-C", str(repo), "archive", commit, *paths], check=True, capture_output=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar.stdout, check=True)


def snapshot(case, work, candidate=None, base=None):
    """A repository that holds the base as one commit (tag bench-base) and,
    for a review, the candidate as a second one. The merged fix is not in it."""
    repo = Path(case["repo"]).expanduser()
    export(repo, base or case["base"], work)
    run(["git", "init", "-q", "-b", "main"], cwd=work)
    git(work, "config", "user.name", "bench")
    git(work, "config", "user.email", "bench@localhost")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "base")
    git(work, "tag", "bench-base")
    if candidate:
        git(work, "checkout", "-q", "-b", "candidate")
        git(work, "rm", "-rq", ".")
        export(repo, candidate, work)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", "candidate")


def claude(prompt, arm, cwd, dirs=(), resume=None, tools=TOOLS, timeout=3600):
    model, _, effort = arm.partition(":")
    cmd = ["claude", "-p", "--output-format", "json", "--strict-mcp-config", "--model", model]
    if tools:
        cmd += ["--permission-mode", "acceptEdits", "--allowedTools", tools]
    if effort:
        cmd += ["--effort", effort]
    if resume:
        cmd += ["--resume", resume]
    for d in dirs:
        cmd += ["--add-dir", str(d)]
    # No GitHub credentials: the ticket is a file, and the real pull request
    # must stay out of reach.
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
    env["GH_CONFIG_DIR"] = "/nonexistent"
    start = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=cwd, input=prompt, text=True, capture_output=True, env=env, timeout=timeout)
        r = json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        r = {"is_error": True, "result": f"timeout after {timeout}s"}
    except json.JSONDecodeError:
        r = {"is_error": True, "result": (p.stderr or p.stdout)[-2000:]}
    u = r.get("usage") or {}
    return {
        "arm": arm,
        "error": bool(r.get("is_error", True)),
        "reply": str(r.get("result") or ""),
        "session": r.get("session_id"),
        "usd": r.get("total_cost_usd") or 0.0,
        "wall_s": round(time.monotonic() - start, 1),
        "turns": r.get("num_turns") or 0,
        "tok_in": u.get("input_tokens", 0),
        "tok_cache_write": u.get("cache_creation_input_tokens", 0),
        "tok_cache_read": u.get("cache_read_input_tokens", 0),
        "tok_out": u.get("output_tokens", 0),
    }


def checks(case, work, cell, name):
    """Run the ticket's commands on a copy, with the tests of the real merged
    pull request laid over it. The builder never sees those tests."""
    copy = cell / "check"
    shutil.copytree(work, copy, symlinks=True)
    if case.get("hidden"):
        export(Path(case["repo"]).expanduser(), case.get("hidden_commit", case["merged"]), copy, case["hidden"])
    out = []
    for c in case.get("checks", []):
        try:
            p = subprocess.run(c, shell=True, cwd=copy, text=True, capture_output=True,
                               timeout=case.get("check_timeout", 900))
            out.append({"cmd": c, "exit": p.returncode, "tail": (p.stdout + p.stderr)[-1500:]})
        except subprocess.TimeoutExpired:
            out.append({"cmd": c, "exit": -1, "tail": "timeout"})
    shutil.rmtree(copy)
    (cell / f"{name}.json").write_text(json.dumps(out, indent=1))
    return all(c["exit"] == 0 for c in out)


def findings(review):
    kinds = re.findall(r"^\s*\d+\.\s*\[(must-fix|should-fix|note)\]", review, re.M)
    return {k: kinds.count(k) for k in ("must-fix", "should-fix", "note")}


def inputs(cfg, case, cell, a):
    """Ticket, handoff and role files, outside the checkout."""
    inp = cell / "in"
    (inp / "shots").mkdir(parents=True)
    shutil.copy(cfg["_dir"] / case["ticket"], inp / "ticket.md")
    handoff = "No project handoff: the ticket and the repository's AGENTS.md and CODING_STANDARDS.md take its place."
    if case.get("handoff"):
        shutil.copy(cfg["_dir"] / case["handoff"], inp / "handoff.md")
        handoff = f"The project handoff: {inp}/handoff.md"
    roles = a.out / "_principles" / cfg["principles_commit"]
    if not roles.exists():
        export(Path(cfg["principles"]).expanduser(), cfg["principles_commit"], roles)
    return {"inp": inp, "roles": roles, "handoff": handoff}


def new_cell(a, *parts):
    cell = a.out.joinpath(*parts)
    if (cell / "cell.json").exists():
        return None
    if cell.exists():
        shutil.rmtree(cell)  # a cell that was interrupted starts again
    cell.mkdir(parents=True)
    return cell


def slug(arm):
    return arm.replace(":", "@")


def build_cell(cfg, case, arm, rep, a):
    cell = new_cell(a, "build", case["id"], slug(arm), f"rep{rep}")
    if not cell:
        return None
    work = cell / "work"
    snapshot(case, work)
    ctx = inputs(cfg, case, cell, a)
    dirs = [ctx["inp"], ctx["roles"]]
    steps = {}

    steps["build"] = b = claude(BUILD.format(branch=f"feature/{case['id']}", **ctx), arm, work, dirs)
    commits = int(git(work, "rev-list", "--count", "bench-base..HEAD"))
    ready = not b["error"] and b["reply"].lstrip().startswith("READY FOR REVIEW") and commits > 0
    res = {"stage": "build", "case": case["id"], "arm": arm, "rep": rep, "ready": ready,
           "checks_first": False, "checks_final": False, "must_fix": None, "should_fix": None, "fixed": False}
    if ready:
        res["checks_first"] = res["checks_final"] = checks(case, work, cell, "checks-first")
        judge_dir = cell / "judge"
        shutil.copytree(work, judge_dir, symlinks=True)
        sha = git(work, "rev-parse", "--short", "HEAD")
        steps["judge"] = j = claude(REVIEW.format(sha=sha, handover=b["reply"], **ctx), a.judge, judge_dir, dirs)
        shutil.rmtree(judge_dir)
        if not j["error"]:
            f = findings(j["reply"])
            res["must_fix"], res["should_fix"] = f["must-fix"], f["should-fix"]
            if a.fix and (f["must-fix"] or f["should-fix"]) and b["session"]:
                steps["fix"] = claude(FIX.format(review=j["reply"]), arm, work, dirs, resume=b["session"])
                res["fixed"] = not steps["fix"]["error"]
                res["checks_final"] = checks(case, work, cell, "checks-final")
    (cell / "diff.patch").write_text(git(work, "diff", "bench-base", "HEAD"))
    res["accepted_first"] = bool(ready and res["checks_first"] and res["must_fix"] == 0)
    res["accepted"] = bool(ready and res["checks_final"] and res["must_fix"] is not None
                           and (res["must_fix"] == 0 or res["fixed"]))
    mine = [steps[k] for k in ("build", "fix") if k in steps]
    for k in ("usd", "wall_s", "turns", "tok_in", "tok_cache_write", "tok_cache_read", "tok_out"):
        res[k] = round(sum(s[k] for s in mine), 4)
    res["judge_usd"] = steps.get("judge", {}).get("usd", 0.0)
    res["error"] = any(s["error"] for s in steps.values())
    return finish(cell, res, steps, a)


def review_cell(cfg, case, rev, arm, rep, a):
    cell = new_cell(a, "review", f"{case['id']}-{rev['id']}", slug(arm), f"rep{rep}")
    if not cell:
        return None
    work = cell / "work"
    snapshot(case, work, candidate=rev["commit"], base=rev.get("base"))
    ctx = inputs(cfg, case, cell, a)
    handover = (cfg["_dir"] / rev["handover"]).read_text() if rev.get("handover") else "(none)"
    steps = {}
    sha = git(work, "rev-parse", "--short", "HEAD")
    steps["review"] = r = claude(REVIEW.format(sha=sha, handover=handover, **ctx), arm, work,
                                 [ctx["inp"], ctx["roles"]])
    known = rev.get("known", [])
    res = {"stage": "review", "case": f"{case['id']}-{rev['id']}", "arm": arm, "rep": rep,
           "known": len(known), "hits": None, "extra_must_fix": None, **findings(r["reply"])}
    if not r["error"] and not known:  # a clean commit: every must-fix is extra
        res["hits"], res["extra_must_fix"] = 0, res["must-fix"]
    if not r["error"] and known:
        listed = "\n".join(f"{i}. {k}" for i, k in enumerate(known, 1))
        steps["grade"] = g = claude(GRADE.format(known=listed, review=r["reply"]), a.grader, cell, tools=None)
        try:
            verdict = json.loads(g["reply"][g["reply"].index("{"):g["reply"].rindex("}") + 1])
            res["hits"] = sum(bool(h) for h in verdict["hit"][:len(known)])
            res["hit_list"] = verdict["hit"]
            res["extra_must_fix"] = int(verdict["extra_must_fix"])
        except (ValueError, KeyError, TypeError):
            pass  # left empty: grade this review by hand
    for k in ("usd", "wall_s", "turns", "tok_in", "tok_cache_write", "tok_cache_read", "tok_out"):
        res[k] = r[k]
    res["error"] = r["error"]
    return finish(cell, res, steps, a)


def finish(cell, res, steps, a):
    (cell / "steps.json").write_text(json.dumps(steps, indent=1))
    (cell / "cell.json").write_text(json.dumps(res, indent=1))
    if not a.keep:
        shutil.rmtree(cell / "work")
    flag = "ERROR" if res["error"] else "ok"
    print(f"  {res['case']:<24} {res['arm']:<28} rep{res['rep']}  {res['usd']:>6.2f} USD  {res['wall_s']:>6.0f}s  {flag}",
          flush=True)
    return res


def load(path):
    cfg = tomllib.loads(Path(path).read_text())
    cfg["_dir"] = Path(path).resolve().parent
    return cfg


def sweep(cells, a):
    """Repetition by repetition, arms shuffled inside each, so that no arm
    has all its runs at one time of day or on a warmer cache."""
    failed = 0
    for rep in range(1, a.reps + 1):
        todo = list(cells)
        random.Random(rep).shuffle(todo)
        print(f"repetition {rep} of {a.reps}", flush=True)
        for fn, args in todo:
            res = fn(*args, rep, a)
            if res is None:
                continue
            failed = failed + 1 if res["error"] else 0
            if failed == 2:
                sys.exit("Two cells in a row failed (usage limit?). Stopped; run the same command again to continue.")


def cmd_build(a):
    cfg = load(a.cases)
    sweep([(build_cell, (cfg, c, arm)) for c in cfg["case"] for arm in a.builders.split(",")], a)


def cmd_review(a):
    cfg = load(a.cases)
    sweep([(review_cell, (cfg, c, r, arm)) for c in cfg["case"] for r in c.get("review", [])
           for arm in a.reviewers.split(",")], a)


def cmd_verify(a):
    """Before any model runs: the checks must pass on the merged commit, and
    the hidden tests should fail on the base."""
    cfg = load(a.cases)
    bad = 0
    for case in cfg["case"]:
        if a.only and case["id"] not in a.only.split(","):
            continue
        cell = a.out / "_verify" / case["id"]
        if cell.exists():
            shutil.rmtree(cell)
        repo = Path(case["repo"]).expanduser()
        for name, commit in (("merged", case["merged"]), ("base", case["base"])):
            if name == "base" and not case.get("hidden"):
                print(f"{case['id']:<16} base    no hidden tests: only the judge tells a missing build")
                continue
            export(repo, commit, cell / name)
            ok = checks(case, cell / name, cell, name)
            shutil.rmtree(cell / name)
            want = name == "merged"
            bad += ok != want
            failed = [c["cmd"] for c in json.loads((cell / f"{name}.json").read_text()) if c["exit"] != 0]
            print(f"{case['id']:<16} {name:<7} {'pass' if ok else 'FAIL'}  ({'as it should' if ok == want else 'NOT as it should'})"
                  + "".join(f"\n    failed: {c}" for c in failed), flush=True)
        for rev in case.get("review", []):
            for key in ("commit", "base"):
                if rev.get(key):
                    run(["git", "-C", str(repo), "cat-file", "-e", rev[key] + "^{commit}"])
    sys.exit(1 if bad else 0)


def med(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return statistics.median(vals) if vals else float("nan")


def cmd_report(a):
    rows = [json.loads(p.read_text()) for p in sorted(a.out.glob("*/*/*/*/cell.json"))]
    if not rows:
        sys.exit(f"No finished cells under {a.out}")
    keys = sorted({k for r in rows for k in r})
    with open(a.out / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(rows)
    out = []
    for stage in ("build", "review"):
        mine = [r for r in rows if r["stage"] == stage]
        if not mine:
            continue
        arms = sorted({r["arm"] for r in mine})
        cases = sorted({r["case"] for r in mine})
        out.append(f"## {stage.capitalize()}\n")
        if stage == "build":
            out.append("| Builder | Runs | Accepted, first pass | Accepted | Median USD | Median min | Median must-fix | USD per accepted ticket |")
            out.append("|---|---|---|---|---|---|---|---|")
            for arm in arms:
                rs = [r for r in mine if r["arm"] == arm]
                ok = sum(r["accepted"] for r in rs)
                per = f"{sum(r['usd'] for r in rs) / ok:.2f}" if ok else "none accepted"
                out.append(f"| {arm} | {len(rs)} | {sum(r['accepted_first'] for r in rs)} | {ok} | "
                           f"{med(rs, 'usd'):.2f} | {med(rs, 'wall_s') / 60:.1f} | {med(rs, 'must_fix'):.0f} | {per} |")
        else:
            out.append("| Reviewer | Runs | Known defects found | Median extra must-fix | Median USD | Median min | USD per defect found |")
            out.append("|---|---|---|---|---|---|---|")
            for arm in arms:
                rs = [r for r in mine if r["arm"] == arm]
                graded = [r for r in rs if r["hits"] is not None]
                hits, known = sum(r["hits"] for r in graded), sum(r["known"] for r in graded)
                per = f"{sum(r['usd'] for r in graded) / hits:.2f}" if hits else "none found"
                out.append(f"| {arm} | {len(rs)} | {hits} of {known} | {med(rs, 'extra_must_fix'):.0f} | "
                           f"{med(rs, 'usd'):.2f} | {med(rs, 'wall_s') / 60:.1f} | {per} |")
        out.append(f"\nMedian USD per case (compare along a row):\n")
        out.append("| Case | " + " | ".join(arms) + " |")
        out.append("|---|" + "---|" * len(arms))
        for c in cases:
            cells = [f"{med([r for r in mine if r['case'] == c and r['arm'] == arm], 'usd'):.2f}" for arm in arms]
            out.append(f"| {c} | " + " | ".join(cells) + " |")
        errors = sum(r["error"] for r in mine)
        out.append(f"\nCells with an error: {errors} of {len(mine)}.\n")
    (a.out / "summary.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"Written: {a.out / 'summary.md'}, {a.out / 'runs.csv'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=Path.home() / "automation-bench",
                   help="where runs are kept; outside every repository (default: ~/automation-bench)")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("cases")
    b.add_argument("--builders", required=True, help="models, comma-separated, each optionally model:effort")
    b.add_argument("--judge", required=True, help="the one reviewer that judges every arm, model[:effort]")
    b.add_argument("--no-fix", dest="fix", action="store_false", help="leave out the fix round")
    b.set_defaults(fn=cmd_build)
    r = sub.add_parser("review")
    r.add_argument("cases")
    r.add_argument("--reviewers", required=True, help="model[:effort], comma-separated")
    r.add_argument("--grader", default="claude-sonnet-5-5",
                   help="matches findings to the known defects (default: claude-sonnet-5-5)")
    r.set_defaults(fn=cmd_review)
    for s in (b, r):
        s.add_argument("--reps", type=int, default=3)
        s.add_argument("--keep", action="store_true", help="keep each cell's checkout")
    v = sub.add_parser("verify", help="run the checks on the merged commit and on the base, without a model")
    v.add_argument("cases")
    v.add_argument("--only", help="case ids, comma-separated")
    v.set_defaults(fn=cmd_verify)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    a = p.parse_args()
    a.out = a.out.expanduser().resolve()
    a.fn(a)


if __name__ == "__main__":
    main()
