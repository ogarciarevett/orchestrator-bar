# Task status

Write `.orca/task-status.json` in each running worker's worktree. The panel reads
it; it never writes or estimates progress for a worker. Keep it out of commits.
Each worktree has one current task; terminals sharing it show the same status.

```json
{
  "task": "Fix login redirects",
  "pr": "#12",
  "state": "running",
  "left": "Review, then merge",
  "eta_utc": "2026-10-24T16:00:00Z",
  "updated": "2026-10-24T15:40:00Z"
}
```

All six fields are strings. Use a full UTC timestamp ending in `Z` for `updated`
and `eta_utc`; use an empty `eta_utc` when unknown. `pr` may be a number label or
URL, or empty. `state` and `left` are short descriptions, not inferred estimates.
The panel keeps only these fields, collapses whitespace and masks phone numbers.
Each field is limited to 2,000 characters; the file to 16 KiB. Write a temporary
file then rename it to avoid partial reads. Update it when the task changes.

Tasks groups follow config coordinators. Add `"parent": "Alpha"` to a
sub-coordinator to show it under `Alpha`; parent names must exist and cannot form
cycles. Workers discovered from terminal worktree prefixes belong to the most
specific matching coordinator. Dispatched workers retain their run's coordinator.
The terminal inventory supplies the worktree path; no filesystem scan is used.

One row appears for each active worker terminal, including workers waiting for
input or permission. Done and failed workers are omitted. The collapsed row has
only a short task title and ETA in **Europe/Madrid** time (`DD/MM HH:mm`, including
daylight saving changes). Titles omit spinner/status glyphs and end between
words. Click a row or select it and press Enter to open the full title, PR link
and reported state, what remains, last update in Madrid time, full terminal ID,
coordinator and reported model. Click again to close it.

Missing values say `no report yet`. Terminal activity does not establish a task
update or ETA. An old report keeps its actual update time; Tasks never replaces
its state with a freshness label. Without a valid status file, the terminal title
supplies the summary and the remaining fields stay unreported. Supply a full
GitHub PR URL for a reliable link. A numeric PR label becomes a link when the
worker's path contains a repository name listed in config.

Explicit `Missing and why:` and `Waiting (drafts, named blockers):` lines from a
coordinator's current terminal screen also appear as expandable report rows.
Only those lines are retained; arbitrary terminal output is not displayed.
Their ETA and update time stay unreported unless supplied by a task status file.
There is no BENCH parser.

Each configured coordinator, including entries with `parent`, has a mode line
at the top even when Coordinators is collapsed or collection has not succeeded.
Set its `sessionFile` to a session JSONL path in that coordinator's cwd folder.
The filename is a hint: the reader selects the most recently modified top-level
`*.jsonl` in that same folder on every poll, so a restart selects the new session.
If two configured coordinators share a folder, their exact filename hints are
used to avoid confusing their sessions; update those hints after a restart.
A small read-only subprocess scans its complete records backward and returns only the newest
`permissionMode`, normalized to `bypass`, `auto`, `plan`, or `manual`. It returns
no transcript text or other session fields. Unknown modes, missing paths and
failed reads say `no report yet`; every value other than bypass is red.
Terminal footer labels and role documents never establish the running mode.
Update the `sessionFile` folder if the coordinator changes cwd, and keep terminal
handles current.

Only the configured session reads files. It uses the existing 10-second local
timer and 15-second cache TTL (one read per distinct active worktree per TTL),
plus the existing remote inventory poll (60 seconds by default, minimum 30).
Mode collection adds one field-only subprocess per configured session per remote
poll. It uses the existing screen reads for coordinator task report lines.
There are no per-worker timers or additional remote polls.
