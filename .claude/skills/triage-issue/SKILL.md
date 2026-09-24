---
name: triage-issue
description: Label a GitHub issue and draft a reply to the reporter. Use to triage, label, classify, reply to, or close issues.
---

# Triage an issue

Goal: each open issue has the correct labels and, when necessary, a reply that asks for the missing
information.

## Steps

1. Read the issue and its comments: `gh issue view <n> --comments`.
2. Check that the labels below still exist: `gh label list`. If they do not match, tell the user and
   update this file.
3. Decide the labels:
   - Exactly one `type:` label.
   - One `status:` label while the issue waits for something. Remove it when the issue is ready for work.
   - One `priority:` label when the issue is classified.
   - One or more `comp:` labels.
4. Check if a bug has enough information: the knowit version, the Python version, the command or
   code, and the full error. For knowit, ask for the `knowit-report.yml` file from
   `knowit --bug-report <file>`. It has all of these items and the raw backend output. For an error about
   a file name, also ask for the output of `knowit --check-name "<name>"`. See `docs/bug-reports.md`.
5. Draft a reply in strict STE100 (`writing-style` skill) and in the reply style below. Ask for each
   missing item in a separate sentence.
6. Show the labels and the reply to the user. **Wait for approval.** Then run
   `gh issue edit <n> --add-label ... --remove-label ...` and `gh issue comment <n> --body-file <file>`.
7. If the user wants to start work, continue with the `investigate` skill.

## Reply style

Write as the maintainer: short, direct, and to the point.

- Give the decision, the reason, and the next action for the reporter. Two or three sentences are
  usually enough.
- Do not put the investigation in the reply: no root cause, no code, no analysis. It goes in the PR or
  in `plans/`.
- No greeting, no thanks, no apology.

Example: close an old issue that has not enough information to reproduce
(`gh issue close <n> --reason "not planned" --comment "..."`):

> Closing this as stale. There is not enough information to reproduce it: no MediaInfo version and no
> raw output.
>
> If it still happens, please open a new issue with the output of `knowit --bug-report <file>`.

## Labels

| Label | Use when |
| --- | --- |
| `type: bug` | The behavior is wrong and someone can reproduce it. |
| `type: feature` | A new capability or an enhancement. |
| `type: tech-debt` | Refactoring, dependencies, internal tools. |
| `type: docs` | README or other documentation. |
| `status: triage` | New. Nobody reviewed it yet. |
| `status: waiting-on-author` | We asked the reporter for information. |
| `status: blocked` | It waits for another project or library. |
| `priority: critical` | A crash or a regression for many users, or a broken build. |
| `priority: high` | An important bug or feature for many users. |
| `priority: low` | An edge case or a small improvement. |
| `comp: cli` | The command line: `knowit/__main__.py`, its options, and its output. |
| `comp: parsers` | Parsing of raw values: `knowit/properties/`, `knowit/rules/`, `knowit/defaults.yml`. |
| `comp: video` | Video track fields: codec, profile, resolution, HDR, scan type. |
| `comp: audio` | Audio track fields: codec, profile, channels, Atmos, DTS-HD. |
| `comp: subtitles` | Subtitle track fields: format, closed captions, hearing impaired. |
| `comp: provider` | A backend or its executor: `knowit/provider.py`, `knowit/providers/`, opening the file. |

`good first issue` and `help wanted` stay without a prefix. GitHub shows them to new contributors.

## Many issues

For a review of all open issues, run `gh issue list --state open --limit 100`. Make a table: number,
title, current labels, suggested labels, and one line on the next action. Do not change labels until the
user approves the table.
