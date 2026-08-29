# Findings register

**Machine-readable. `tools/check_claims.py` reconciles this file against the code.**

Every accepted finding appears here with the test that closes it. The checker verifies that each
named test **exists**, and reports any finding whose closing evidence is missing or unnamed.

This used to say *"every finding accepted in a review stop"*. That was too narrow, and F-8 is
why: it was found by D2.7's boundary hunt, not at a stop. A finding does not become less real
because of when it was found, and a register that only admits stop findings would have quietly
excluded it.

**It is now reconciled in both directions, and the second direction was missing for weeks.**
`check_findings` validates the rows that are *here*. `check_register` — added 2026-08-29 — scans
every document for `F-n` / `V-n` / `Q-n` and requires each one the record names to have a row.
Without it, a finding discussed in nine files and absent from this table **passed the gate**:
**V-12, V-13, V-14 and V-15 were exactly that**, while the checker printed *"22 findings in the
register, all accounted for."* That sentence was true and worthless — it answered *is everything
here consistent?* when the question was *is everything here?* The four rows are below, added with
the check that would have demanded them.

**Why this file exists.** Three times in Phase 1 a report was accurate about what it covered and
misleading about what it left out — `docs/CORRECTIONS.md` C-12, C-13, and the recurrence one turn
after C-12 was recorded. That class is not caught by running the thing; it is only caught by
reconciling a report against the artifact it describes. This is the artifact. The checker is the
reconciliation.

**A test named here is evidence, not proof.** The suite is the builder's. What this file defends
against is a finding quietly disappearing between reports, not a test that agrees with the code for
the same wrong reason.

## Status vocabulary

| Status | Means |
|---|---|
| `closed` | Fixed, with a named test that fails without the fix |
| `open` | Accepted, not yet fixed |
| `ruled` | Resolved by a decision rather than code |
| `noted` | Recorded as a limit; no fix is possible or intended |

## Register

| ID | Sev | Status | Closing evidence | Record |
|---|---|---|---|---|
| F-1 | high | closed | `test_a_non_numeric_label_is_refused_by_name` | C-13 |
| F-2 | medium | closed | `test_chunk_files_are_read_back_in_numeric_order` | — |
| F-3 | medium | closed | `test_a_missing_sample_size_is_a_missing_field` | D-22 |
| F-4 | medium | closed | `test_swapped_chunks_within_one_item` | — |
| F-5 | low | closed | `test_verify_without_the_key_refuses_by_name` | — |
| F-6 | low | closed | `test_labels_for_a_different_sample_are_refused` | — |
| F-7 | low | closed | `test_a_different_id_in_the_same_directory_is_refused` | — |
| F-8 | high | closed | `test_a_confidence_outside_zero_to_one_is_refused_by_name` | D2.7 |
| V-1 | critical | closed | `test_replanning_into_an_open_workspace_is_refused` | D-17 |
| V-2 | high | closed | `test_replan_without_rerunning_names_the_plan_not_the_estimate` | C-10 |
| V-3 | high | closed | `test_an_unrecognised_comparison_is_refused` | — |
| V-4 | high | closed | `test_a_non_numeric_threshold_is_refused_at_load` | — |
| V-5 | medium | closed | `test_a_count_disagreeing_with_the_digest_list_is_refused` | — |
| V-6 | medium | closed | `test_verify_without_the_key_refuses_by_name` | — |
| V-7 | medium | closed | `test_both_frame_counts_reach_the_record` | D-21 |
| V-8 | medium | closed | `test_a_numeric_threshold_under_equals_is_refused` | D-20 |
| V-9 | low | closed | `test_the_sealed_plan_is_canonical_bytes` | — |
| V-10 | low | closed | `test_verify_structure_docstring_does_not_promise_a_keyless_verify` | O-14 |
| V-11 | medium | closed | `test_the_ceiling_is_named_not_a_traceback` | D-19 |
| V-12 | high | closed | `test_the_tampered_plan_is_caught_without_the_flag` | D-24 |
| V-13 | medium | closed | `test_the_recorded_plan_path_is_as_invoked` | C-19 |
| V-14 | medium | ruled | `test_a_plan_without_a_source_path_records_none` | D-25 |
| V-15 | medium | closed | `test_the_path_check_reads_documents_outside_src_and_tests` | D-23 |
| V-16 | medium | closed | `test_ci_runs_every_check_the_gate_documents` | D-28 |
| V-17 | medium | closed | `test_the_register_names_the_route_the_witness_used` | D-29 |
| Q-1 | — | ruled | `test_svy_wilson_is_not_the_textbook_interval` | D-18 |
| Q-2 | — | noted | none — not fixable by the builder | C-12 |

## Q-2 is deliberately unclosable

Q-2 is the observation that the suite is the builder's: written from one understanding, wrong in
both places when that understanding is wrong. No test the builder writes can close it, because the
test would have the same author.

What narrows it is a second instrument with a different author — the reviewer harness — and even
that is not independent truth. `docs/contracts/PHASE-1-CONTRACT.md` §7a records what it does not
reach.

Leaving Q-2 permanently `noted` is the honest entry. Marking it closed would be the failure it
describes.
