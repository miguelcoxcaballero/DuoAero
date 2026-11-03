# First-midterm review queue

The heuristic counts candidates rather than confirmed defects. On the current
bank it reports 535 possible calculations without authored hints; the separate
long-stem count is 278 unstaged source stems over 300 characters. The entries
below record this review's decisions, including conceptual false positives that
remain in the heuristic count. A host check or authored sequence does not imply
Android or real-account acceptance.

| Source ID | Review decision |
| --- | --- |
| TA1-0244 | Conceptual: identify the ISA layer from its stated lapse rate; no calculation hint needed. |
| TA1-0409 | Conceptual: interpret the notation ISA+15; the number is the label being identified. |
| TA1-0812 | Conceptual: identify the ISA region from its stated temperature gradient. |
| TA1-0869 | Conceptual: select pressure behavior across the layer boundary. |
| TA1-0937 | Conceptual: identify the ISA region from its stated temperature gradient. |
| TA1-0765 | Conceptual: interpret the notation ISA-10; no computation is requested. |
| EX-2025-11-06-4 | Needs editorial review: an approximate temperature is requested without the numerical cruise conditions needed for a unique calculation. No invented hint was attached. |
| TA1-0832-D3 | Real coupled range calculation; pending a properly rendered interactive square-root prerequisite and staged calculations. |
| TA1-0173-F1 | Real TSFC unit conversion: staged into 14 word, named, symbolic and single-operation controls, with a new uncredited lesson and exact historical-proof checks. Android hint, touch, layout and persistence remain pending. |

### Two ideal-jet practice families: arithmetic audit, sequencing pending

`research/audit_jet_families.py` extracts the stated parameters and checks that
exactly one original option is closest for each case. It independently applies
the ideal Breguet assumptions stated in the questions, including the reserve,
tank and takeoff constraints. This is arithmetic evidence only: none of these
20 questions has been accepted as a newly sequenced lesson by this audit.

- Range after prior fuel burn: TA1-0798-D3, TA1-0885-D3, TA1-0930-D3,
  TA1-0959-D3, TA1-0968-D3, TA1-N3-34-06, TA1-N3-34-07,
  TA1-N3-34-08, TA1-N3-34-09, TA1-N3-34-10. All ten original answers
  agree; teaching steps, historical migration and Android remain pending.
- Payload with four constraints: TA1-0645-D3, TA1-0703-D3, TA1-0718-D3,
  TA1-0923-D3, TA1-0934-D3, TA1-N3-09-06, TA1-N3-09-07,
  TA1-N3-09-08, TA1-N3-09-09, TA1-N3-09-10. All ten original answers
  agree; teaching steps, historical migration and Android remain pending.

The fuel-limit equation is derived from the mass ratio, not from a constant
fuel mass independent of payload. The existing session limits mean that simply
expanding these source items in place would overfill sessions. A safe split
must preserve original IDs, award no unearned completion, and be exercised on
Android before connecting these drafts to the course.

The two families now have reusable draft generators in
`research/jet_family_steps.py`: each displayed arithmetic step uses the
operands shown in that step, preserves the source ID/options for the final
choice and links hints to explicitly named formula prerequisites. The 56
word/full-name/symbol prerequisite models are in
`research/jet_family_prerequisites.py`. Model tests cover all 20 variants;
they are not yet lessons. In particular, the exponential named layout still
uses exp rather than a verified superscript arrangement, the multi-factor
fraction layouts are not accepted, and neither selection nor hint/retry has
been exercised for these drafts on Android. Session distribution and exact
historical progress preservation are also still required before integration.

`research/jet_family_distribution.py` now partitions the draft into four
formula sessions and twenty case sessions (six nodes of four), each with
10–20 native challenges and prerequisites preceding every linked hint.
The draft session IDs are absent from all four published session histories;
the original 20 question IDs are retained in the case finales. This simulation
does not alter the course or assign historical completions. Integrating it
still requires resolving old sessions after removing the original questions,
exact proof migration, native interaction and the unaccepted formula layouts.

The trapezoidal-wing family TA1-0512-D3 and nine variants was checked for
physical taper domain. Five formerly used negative algebraic lower bounds;
their correct width now uses a zero lower bound. Three have a negative upper
bound and now correctly answer that no nonnegative taper is feasible. The
original IDs remain; the eight corrected practice records have content
revision 2 and revised explanations and distractors. The other two already
have nonnegative bounds. `research/test_taper_domain.py` checks all ten and is
run by both bank and Android diagnostic workflows. No source generator for
this family was located in tracked Python source; `author_taper_domain.py`
provides a repeatable repair and the test rejects reintroduced invalid output.
Published historical completions are not altered by this editorial repair;
Android grading/layout of the revised questions remains unverified.

Run 41591175636 rendered the clarified taper stem with its last formula clipped
and the emulator killed the app under memory pressure after nine graded cases.
`research/taper_stages.py` now scaffolds 24 single-operation calculations for
each of the ten variants and checks their resulting algebraic bounds against
the independent domain calculation. The draft also includes choices and a
physical-domain decision, retaining each original ID for the final answer.
It has no taught prerequisites, hints, course sessions, migration or Android
validation. It does not fix the live
clipped prompt until that remaining work is completed and integrated.

The round-trip fuel-budget family now has a parametrized arithmetic draft in
`research/wind_budget_steps.py`. It keeps the original final IDs and options,
uses one displayed arithmetic operation per step, and enforces a real wind
speed below the stated airspeed. The ten source IDs are TA1-0420-D3,
TA1-0484-D3, TA1-0523-D3, TA1-0627-D3, TA1-0936-D3, TA1-N3-06-06,
TA1-N3-06-07, TA1-N3-06-08, TA1-N3-06-09 and TA1-N3-06-10. Their calculated
closest options and intermediate displayed operands pass host tests. The wind
draft includes word, complete-quantity and symbolic exercises for
six of its seven relations. The final wind square-root relation is still
explicitly rejected by the hint-order validator until a native formula layout
with a fixed radical and interactive quantity is implemented and verified.
The hints must not be connected to the course yet; migration, Android layout,
touch and retry remain unverified.
