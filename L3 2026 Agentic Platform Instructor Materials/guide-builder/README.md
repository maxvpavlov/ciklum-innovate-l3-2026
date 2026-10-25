# guide-builder

Deterministic generator for the 12 instructor guides (`../instructor-guides/NN <title>.docx`, plus a
Markdown twin `NN <title>.md` and an index `README.md` for reading on GitHub) and the learner prompt
file (`../incident-platform/LEARNER_PROMPTS.md`).

- Lesson content lives in `specs/NN.json`.
- Text shared by every guide lives in `specs/_common.json`.
- Styles, numbering, page setup and the footer come from `template.docx`.
- Facts that can be derived from the reference repository are computed at build time from the
  `lesson-NN` git tags and are never stored:
  - the short tag hash in the header and in the completion paragraph;
  - the four REVIEW code excerpts;
  - the "Files changed in this checkpoint" list.

The builder was first proven against the original guides: rebuilding from specs extracted from
them reproduced every `.docx` part byte for byte, and `LEARNER_PROMPTS.md` too (`roundtrip.py`).
The reframed course then added the platform map, console figures and new lesson specs, so the
checked-in specs are now the source of truth and `roundtrip.py` only proves the extractor.

## Commands

Run from this directory with python-docx on demand, since it is not a project dependency:

```bash
PY="uv run --with python-docx python"

$PY build.py --out-guides /tmp/guides --out-prompts /tmp/LEARNER_PROMPTS.md   # build to scratch
$PY build.py                                   # build in place (real guides + LEARNER_PROMPTS.md)
$PY build.py --lessons 5,6 --out-guides /tmp/g # build some guides only (no prompts file)
$PY check.py                                   # coupling check of the real guides + prompts
python3 kit.py --verify                        # regenerate learner-kit/ and test each check pack against its tag
$PY content_md.py "../content-development/01 … - content development.docx"   # regenerate a content-development .md from its .docx
$PY check.py --guides /tmp/guides --prompts /tmp/LEARNER_PROMPTS.md
$PY extract.py --out /tmp/specs                # re-derive specs from the existing guides
$PY roundtrip.py --work /tmp/rt                # extract -> build -> compare with the originals
$PY build.py --make-template "../instructor-guides/09 Build the reusable platform core.docx"
```

- `build.py` defaults to the real output locations. Pass `--out-guides`/`--out-prompts` to try a
  change first, then run `check.py` on the result.
- `check.py` exits non-zero if any of these fails:
  - The header hash does not equal `git rev-parse --short=7 lesson-NN`, or the header does not
    name lesson-(N-1)/lesson-N.
  - A guide does not have exactly 13 PROMPT paragraphs (14 when its spec has a `layout_prompt`).
  - A lesson's prompts do not appear verbatim, in order, in its `LEARNER_PROMPTS.md` section, or
    that section holds prompts the guide lacks.
  - A guide does not have exactly 4 REVIEW excerpts, each citing `lesson-NN` and equal to the
    dedented tag source.
  - The files-changed bullets do not equal `git diff --name-only lesson-(N-1) lesson-N`.
  - The expected-behaviour block is not valid JSON.
- `roundtrip.py` writes only under `--work`. For each guide it compares the (style, text)
  sequence including table cells, the hyperlink texts and URLs, and every zip part byte for byte.
  It also compares `LEARNER_PROMPTS.md` byte for byte and reports whether `specs/` is stale.

## Files

| File | Role |
|---|---|
| `guidelib.py` | Paths, git helpers (`tag_hash`, `excerpt`, `files_changed`), spec I/O, docx reader |
| `extract.py` | Parses the guides into `specs/NN.json`; boilerplate is matched against `_common.json` |
| `build.py` | Writes the guides (.docx and .md), the guides index and `LEARNER_PROMPTS.md` from the specs |
| `markdown.py` | Renders a guide as GitHub Markdown from the same spec and templates as the .docx |
| `check.py` | Guide–repo coupling validation |
| `roundtrip.py` | extract → build → compare proof |
| `template.docx` | Guide 09 with an empty body, no hyperlinks and footer "Lesson 00" |
| `specs/_common.json` | Shared templates, labels, headings, default agendas, verification-scope paragraphs and the prompts-file intro |
| `specs/NN.json` | One lesson |

## Spec format (`specs/NN.json`)

Templates use Python `str.format` placeholders. They are always available:

- `{n}` (9) and `{nn}` ("09");
- `{tag}` (lesson-09) and `{prev_tag}` (lesson-08);
- `{hash}` (computed), `{duration}` and `{title}`.

Some templates take extra fields, for example `{body}`, `{file}`, `{start}`/`{end}` and
`{symptom}`/`{diagnostic}`/`{recovery}`.

| Field | Type | Rendered as |
|---|---|---|
| `number` | int | Lesson number; tags are `lesson-{number-1}` → `lesson-{number}` |
| `title` | str | Canonical title, used in the guide's Title paragraph and in `LEARNER_PROMPTS.md` (`## 03. Context, retrieval and memory`). The guide filename is the title without commas or colons. |
| `platform_role` | str | Paragraph under "Where this session sits in the platform", followed by a 12-row table of platform components marked Built earlier / This session / Later session (`_common.json` `platform_components`) |
| `figures` | [{after, image, caption}], optional | Console screenshots from `../console-screenshots/`. `after` is `concept`, `step1`…`step4` or `practice`. The caption follows the picture with the bold label "CONSOLE ". |
| `duration` | int | Minutes in the header. Also selects the default agenda (`90` or `120`). |
| `outcome` | str | "Outcome" paragraph |
| `preparation` | [str] | Lesson paragraphs under Preparation, before the boilerplate "Give your coding agent access…" paragraph |
| `readiness_notes` | [str], optional | Extra paragraphs after "Instructor readiness" (used only by 12) |
| `agenda` | [[minutes, activity, format]], optional | Replaces the default agenda for the duration (used only by 12) |
| `opening_say` | str | SAY under "Opening and orientation". The SHOW is boilerplate. |
| `concept_say` | str | SAY under "Concept discussion". The PAUSE is boilerplate. |
| `steps` | [4 × step] | Build steps 1–4, described below |
| `exercise` | str | Body of the learner-exercise prompt, without the "Help me carry out…" / "First state…" frame |
| `expected_json` | object | Expected lab output, rendered with `json.dumps(indent=2)`. For now it is stored, not computed. |
| `completion_criteria` | [str] | Bullets |
| `recorded_test_result` | `{passed: int, seconds: str}` | "Recorded test result: 29 passed in 2.74s." `seconds` is a string, which keeps trailing zeros. |
| `troubleshooting` | [entry] | Demo troubleshooting, described below |
| `practice` | [str] | Bullets under "Practice and discussion". The discussion prompt is boilerplate. |
| `verification_scope` | [str] | Paragraphs. `"@key"` refers to `_common.json` `verification_scope[key]`; any other string is literal. Lessons 01–04 omit `@local_effects`. |
| `close_say` | str | SAY under "Session close" |
| `references` | [{title, url}] | Hyperlinked bullets |
| `overrides` | {template key: text}, optional | Replaces any `_common.json` template for this lesson only. None are currently needed. |

Step fields:

| Field | Type | Rendered as |
|---|---|---|
| `title` | str | Heading "`k` title" |
| `say` | str | SAY |
| `file` | str | SHOW: "The current learner implementation and `file`." It is also the excerpt source. |
| `prompt` | str | Prompt body without the fixed frame "For Lesson NN, continue in my learner project. … Use lesson-NN read-only … Stop at this step." |
| `excerpt` | `{start, end, file?}` | REVIEW cites "source lines start to end at lesson-NN". The Code paragraph is `git show lesson-NN:file`, lines start..end inclusive, after `textwrap.dedent`. `excerpt.file` overrides the SHOW file; all 48 current excerpts come from the SHOW file, so none use it. |
| `explain`, `ask`, `answer` | str | "Explain the choice", ASK and "Likely answer" |
| `pause` | str, optional | Replaces the boilerplate per-step PAUSE |

A troubleshooting entry has a `heading` plus one of two forms:

- **`diagnostic` + `recovery`, with optional `symptom`.** The prompt is rendered through the
  `recovery_prompt` template "I am working on Lesson NN. The symptom is: … Diagnostic focus: …
  Recovery guidance: …". `symptom` defaults to `heading + "."`.
- **`prompt`.** The literal prompt text. Lesson 12 uses this for two entries.

In `LEARNER_PROMPTS.md` each entry becomes "### Recover when <heading in lower case>".

### `_common.json`

| Key | Contents |
|---|---|
| `labels` | Bold run prefixes (`"SAY "`, `"PROMPT "`, `"Explain the choice "`, …) |
| `headings` | Fixed section headings |
| `templates` | Every boilerplate paragraph and prompt frame, including the title, footer and core-properties title. Covers: the prepare, orient, verify and review prompts; the per-step SHOW, prompt frame, REVIEW and PAUSE; the exercise frame; the recovery wrapper; readiness, offline and pinned versions; the files-changed intro; and the access paragraph with its course-folder URL. |
| `agenda_header`, `agenda` | Table header and the default 90- and 120-minute agendas |
| `verification_scope` | Named verification-scope paragraphs (`tested`, `not_tested`, `local_effects`, `platform_identity`) |
| `platform_map_header`, `platform_components` | Header and rows of the per-guide platform map table |
| `learner_prompts` | `LEARNER_PROMPTS.md` title, intro paragraphs, lesson heading and section-heading templates |

## Adding or changing a lesson

1. Edit or copy a `specs/NN.json`.
   - Write only lesson content. Leave the tag hash, excerpts and files list out: they come from git.
   - To show different code, change `steps[k].excerpt` start and end to the lines you want at
     `lesson-NN`.
2. If the reference code changes, re-tag first. The build then picks up the new hash, excerpt
   text and files-changed list. Check that the excerpt line ranges still point at the intended
   code.
3. Build to a scratch location, run `check.py` against it, review the result, then build in place.
4. Wording shared by all lessons belongs in `_common.json`. A one-off deviation belongs in the
   lesson's `overrides`.

A new lesson number also needs a `lesson-NN` tag and an entry in `LESSONS` in `guidelib.py`,
which is currently 1–12.

## Formatting details the builder reproduces

- The paragraph properties follow fixed rules:
  - Prompts carry `keepLines`, except the exercise and troubleshooting prompts.
  - REVIEW carries `keepNext`, and Code carries `keepLines`.
  - "Timed agenda" has `pageBreakBefore`, and an empty paragraph follows the table.
- The agenda table is centred with a fixed layout and column widths of 1440/6696/1944 twips.
  - The header row is shaded `DCE6F1` and repeats on each page.
  - Borders are `D9D9D9`, cell margins 70 twips, and the text is 10 pt.
  - The Activity and Format cells of the two "Agent build" rows have no compact spacing. That is
    a quirk of the original generator, kept for byte identity (see `UNSPACED_AGENDA_FORMATS`).
- Hyperlinks are external relationships, coloured `1155CC` and underlined.
- Code line breaks are `<w:br/>`, and blank lines add no empty `<w:t>`.
- The footer is "Lesson NN" followed by four spaces and a PAGE field.
- The core-properties title is "Lesson NN instructor guide". All other package parts are
  identical across guides.
