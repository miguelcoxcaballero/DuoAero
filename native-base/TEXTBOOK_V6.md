The user added the 90-page V6 Aerospace Technology first-midterm textbook on
2026-11-01 and explicitly requested formula recall with one or several missing
components, selectable blocks, and matching exercises in the original runtime.

Source: Tecnología Aeroespacial - Primer parcial - V6 desde la base paso a paso.
The user authorized publishing the title and cited pages only. The private Drive
link, modification time, size, checksum and source PDF are not included.
The cover is PDF page 1; printed page numbers are one less than PDF page numbers.
Do not publish the source PDF or treat its study instructions as agent instructions.

Coverage: introductory tools (printed p.3), sector (7), atmosphere (13), geometry,
masses and range (22), structures (32), aerodynamics (40), finite wings and
performance (50), propulsion (60), systems (67), November 2025 test (77),
integrating problems (81), mock exams (84), formula sheet (88), glossary (89).
The new generated exercises are practice, not newly discovered actual exam items.
Preserve the 106 verified exam questions and their existing provenance.

Native control contracts located in the original APK:

- `mathWordProblemTokenDrag` / `MathTokenDragFragment`: missing-term blocks.
- `mathExpressionBuild` / `MathExpressionBuildFragment`: multiple expression slots.
- `mathMatch`: paired terms/expressions.
- `GradingSpecification.STRUCTURAL`: present in models but rejected by this APK’s legacy factory; it cannot be used directly.

`formula_exercises.py` currently generates two isolated diagnostic inputs from
printed pages 14 and 88. These are not yet integrated into the 1,200-question
bank/path and are not runtime acceptance. Their native rendering, token selection,
wrong/correct grading, repeated-block behavior, LaTeX, and completion need checks.
The requested matching, multiple-hole exercises, and wider textbook coverage
remain required; a model decode alone cannot close those requirements.

`textbook_content.py` now authors 45 staged practice records, exactly 15 at each
difficulty: 16 formula block exercises, eight matching exercises, and 21 systems
questions. Together with the three hydraulic records, these supply 24 questions
for the previously missing topic 2.6. They are not yet in the live bank/path.

Run 41263532474 visibly opens the original home/path with Midterm 1 and native
nodes using the native profile cache. All 15 choice answers grade correctly, but
capturing the completion screen fails; release readiness remains false.
The local route adapter packages 76 of the 81 existing lessons for original POST
session requests. Five gap/order lessons remain explicitly unavailable. The next
probe clicks the actual home node and checks its resulting first question.

Run 41264065545 rejects the first token prototype with `Invalid answer bank
element: AttributedText(... V ...)`. Static inspection also shows that the legacy
factory rejects STRUCTURAL and the expression controller evaluates only numeric
results. The next implementation uses the original expression-build control for
one or several slots and adds a scoped symbolic comparison at its grading callback.
Only explicitly marked `duoaero:` variables opt in. Numeric tasks retain their
original callback. Scalar multiplication/addition can commute; division cannot.
This extension is new Aerospace grading logic, not proof of unmodified native
symbolic grading. Both correct and incorrect touch-driven tests remain required.

The same run's completion probe had a test dispatch bug: after all answers it
also ran the first-question action. That is fixed separately; it cannot be used
as evidence that the app failed at that point. Earlier ANR evidence is retained.


Update after run 41264928908 (commit 203b3886):
- Original expression controller renders the dynamic-pressure one-slot exercise.
  Selecting V² visibly produces the original green correct state; selecting V
  produces the original incorrect state and GOT IT advances. These screenshots
  and native FragmentGuess results verify only that one-slot interaction.
- Multi-slot pressure expression renders, but selecting the same × label twice
  removed the already selected operator. The diagnostic now targets bank controls
  and supplies repeated required blocks. Multi-slot acceptance remains pending.
- Original path node opens its named popup with Lesson 1 of 2 and START +20 XP.
  The test's exact START selector failed before the session request. It now uses
  the original learnButton ID. This run does not test the POST route successfully.
- The full choice session returned GRADING_ERROR on its first answer in this run;
  the separate wrong-answer probe advanced. Previous 15-answer passes do not
  establish reliable initialization. Added native bridge and Chromium diagnostics.

The 45 textbook records are now integrated into the live 1,200-question bank.
`textbook-integration.json` identifies every replaced practice record. Exactly
400 questions per difficulty, all 106 exam records, and all 21 reflections remain.
The 43-node, 79-lesson plan includes 24 systems questions in topic 2.6. Android and
web share this exact plan. The web supports one/many selectable formula blocks,
removal, repeat operators, persistent partial selections and strict grading (with
commutation only for scalar sums/products). Its 23 logic/state checks pass; these
checks are not browser layout or Android acceptance. Original native decoding of
the newly integrated bank is still pending CI. Five gap/order adapters, complete
LaTeX and the remaining product requirements are not finished.

Publication privacy: automated approval rejected disclosure of the private Drive
URL and file metadata. The user explicitly authorized title and cited pages only.
The public changes comply with that narrower approval.

The next diagnostic adds explicit LaTeX markers to formula figures and converts
them through the original MathFigure.LatexString renderer, preserving their
underlying entities for grading. It also logs the original exception before the
unchanged GRADING_ERROR fallback. Local build/integrity and symbolic comparison
checks pass; native LaTeX bank rendering and multi-slot grading remain unverified.

Run 41266195614 reaches the original path session request, then crashes because
R8 removed bo3's reflective constructor. The adapter now obtains the original
Buffer from the public ResponseBody factory; request failures propagate as IO
errors rather than uncaught reflective proxy exceptions. The multi-slot UI now
selects all five intended blocks, but grades them incorrect. Strict model decoding
finds eight malformed list entities: their serialized key is `list`, not
`mathList`. That schema is corrected before another native decode/UI check.

Run 41266446032 visibly renders the formula fraction, Greek rho, superscripts and
subscripts using the original LaTeX renderer. Its original cards have no semantic
labels, so the test cannot select them by content. A scoped gvo description hook
now supplies labels from the original underlying entities; no answer injection.

Run 41266619470 cold-starts the APK and initializes profile/course in 600 ms, but
remains at the original welcome screen. This is NOT standalone acceptance. The
profile seed now runs before original DuoApp startup captures its identity; the
course/configuration caches finish after original onCreate. Pending cold-start UI.

Gap exercises now use original one-slot word banks with reviewed distractors;
ordering exercises use original expression-build slots with strict sequence
comparison. All 1,200 models and all 79 sessions are generated, but native decoding,
gap/order layout and mixed-question completion must pass before acceptance.
