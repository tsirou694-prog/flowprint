# FlowPrint Evidence Audit Contract

Use this contract for every classification preview. It prevents a valid scope
from becoming a broad search and prevents unread or stale files from being
presented as evidence.

## 1. Run workspace preflight first

Run `scripts/check_evidence_scope.py` before any workspace listing, search, or
read. Treat a nonzero result as a hard stop for recursive discovery.

- `allowed_project_scope`: targeted discovery may remain inside this project.
- `allowed_explicit_only`: read only exact paths named by the user; do not list
  their parent or siblings.
- `blocked`: use visible conversation only, or ask the user to open the actual
  project directory.

Never reinterpret `Downloads`, `Desktop`, `Documents`, a home directory, a
drive/filesystem root, a shared temporary root, or the installed plugin cache
as a safe project merely because it is the current working directory.

## 2. Keep a read ledger in memory

Separate these sets throughout the run:

1. **Discovered metadata** — names returned by a scoped listing or search.
2. **Actually read evidence** — workspace files whose contents were opened.
3. **Actually read FlowPrint rules** — bundle references or scripts opened only
   to apply FlowPrint.
4. **Visible conversation evidence** — exact user statements used directly.

Listing a filename does not make its contents evidence. A rule filename that
was not opened cannot be cited as a rule source. The final audit must match the
tool trace; when they conflict, remove or downgrade the claim.

## 3. Bind evidence cohorts

When files contain task, run, date, entity, version, or environment identifiers,
group them into evidence cohorts before extracting concrete values.

Use this order:

1. the current task's explicit accepted result;
2. same entity, same run/date, and same target version;
3. same entity and version with an explicitly explained cross-run comparison;
4. older or different-version evidence only as a labeled Failure Lesson.

Do not combine versions to fill missing commands, paths, results, hashes, or
environment facts. If the requested cohort is incomplete, keep the missing
value unknown and list the absent locator. Evidence from an older cohort may
explain a past failure but may not support a current-version success claim.

## 4. Cite only what was read

Every concrete item must cite one of:

- a visible-conversation statement;
- an exact path in **Actually read evidence**;
- an exact FlowPrint file in **Actually read FlowPrint rules**;
- `model_inference`, clearly labeled and never used alone for a high-impact or
  permission item.

Do not cite generic labels such as “FlowPrint contract” or “project evidence”.
Name the exact file or conversation statement. Do not import facts remembered
from earlier sessions or older files that were only discovered.

## 5. Required audit output

End every preview with `Evidence scope audit` containing:

- preflight status and exact workspace root;
- whether recursive discovery was allowed;
- discovered metadata paths, summarized if numerous;
- exact workspace evidence files actually read;
- exact FlowPrint rule files actually read;
- evidence cohort selected, including version/date when present;
- older/different cohorts discovered but not used for current claims;
- prohibited roots or stores not accessed;
- files written and external actions performed.

If the audit cannot be made consistent with the tool trace, return
`Status: needs_review` and do not compile.
