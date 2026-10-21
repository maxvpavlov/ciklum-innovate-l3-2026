# Session slides

| File | What it is |
|---|---|
| `01 Agent architecture and the ReAct runtime.pptx` | Session 01 deck (36 slides with speaker notes), built from the session page on the Ciklum L&D template (Confidential, Light, 2026). Import into Google Slides via File → Import slides, or open in PowerPoint. |
| `build_01.py` | The generator. It adds slides from the template's layouts, removes the template's sample slides and prunes unused layouts. |

Rebuild after changing the session page (the template is supplied by L&D and is not kept in the repository):

```bash
uv run --with python-pptx --with lxml python build_01.py <template.pptx> "01 Agent architecture and the ReAct runtime.pptx"
```

The deck follows the brand rules on the template's guideline slide. Titles and text use Zalando Sans Light, highlights use Zalando Sans Medium, and code uses IBM Plex Mono. The colours are #011126, #00FFBE, #0020BB and #F9FAFB. If Google Slides lacks a font, it substitutes one, so check the code slides (28–30) and the tables after import.

The deck repeats the session page, so update it when the page changes; nothing checks the two against each other.
