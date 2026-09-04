# Generative Step1X-3D research batch — raw research records, 2026-09-04

These files are the raw research output behind the 100 generative research concepts
`SKU-315`–`SKU-414` in `business/02-portfolio/research-ideas-additions-3.csv`.

## Files

| File | Scope |
| --- | --- |
| `research-B-characters.md` | Original stylized characters, cartoon/comic figurines, tabletop miniatures; platform figures, tabletop market filings, IP rule |
| `research-C-toys.md` | Toys, fidgets, puzzles, kinetic desk objects; Printables API figures, toy market data, EU toy-safety timeline, 18 concepts |
| `research-D-tools.md` | Hand tools, workshop aids, desk accessories; Printables/MakerWorld API figures, citable interface nominals, 16 concepts |
| `research-E-figures-decor.md` | Human figures and trending decor; platform API figures, price observations, compliance flags, 28 concepts |
| `research-F-pipeline.md` | Step1X-3D licence, capabilities and documented limits; legal duties; mesh-quality gate |
| `printables-animals-api-2026-09-04.json` | Raw Printables GraphQL response: animals category ranked by downloads (source `S84`) |

## Source-ID remapping

The research files were written with a provisional ID range starting at `S54`. That range
was already occupied in this repository by the named-interface nominal research of the same
day, so the records were renumbered upward when they were appended to
`business/02-portfolio/research-idea-sources-additions.csv`:

- provisional `S54` → registered `S84` (Printables animals API)
- provisional `S55` → registered `S85` (MakerWorld design API and the snippet-accuracy control)
- provisional `S62`–`S106` → registered `S86`–`S130` (uniform `+24` offset)

Cited IDs inside these raw files are therefore the **provisional** ones. The registered IDs
in the portfolio CSVs and in the workbook are the authoritative ones.

## Evidence limits recorded by the research itself

- Platform HTML on Printables, MakerWorld, Thingiverse, Thangs, MyMiniFactory, Etsy and
  Hero Forge refused automated retrieval. Per-model figures come from the platforms' own
  public APIs where those were reachable, and are marked UNVERIFIED where they were not.
- Search-engine snippets were found to quote materially wrong download counts (one snippet
  claimed 216,900 downloads for a model whose API record shows 4,405, and 57k for a model at
  15,737). Snippet figures were therefore excluded from every trend score.
- EUR-Lex article text, the EU AI Act transparency article, US/EU copyright guidance on
  AI output, most platform AI policies, EUR retail price points and German/EU DIY and
  consumer survey data were **not** retrieved. Every statement depending on them is marked
  UNVERIFIED in the files and must be confirmed before it enters customer-facing or
  compliance copy.
- The Step1X-3D licence conflict in `research-F-pipeline.md` is the blocking gate for this
  whole batch; it is carried per row in the portfolio as `Idea__Generative_Tool_Licence_Gate`
  and as a failing `TOOL-LICENCE` hard gate.
