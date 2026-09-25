# Local PDF ingestion and candidate extraction

Implemented workflow, updated 25 September 2026. These CLI commands register local PDFs, inspect pages and extract unreviewed candidates. A separate [curated acquisition command](acquisition-development.md) can download known documents first. The four existing MCP tools still read metadata only; document processing uses a separate archive and never changes that corpus implicitly.

## Run the synthetic example

Install the updated project and generate a fictional PDF with its provenance manifest and extraction recipe:

```sh
.venv/bin/python -m pip install -c requirements-dev.lock -e '.[dev]'
.venv/bin/python examples/make_ingestion_demo.py --output data/private/ingestion-demo
.venv/bin/margin import-document data/private/ingestion-demo/synthetic-results.pdf \
  --manifest data/private/ingestion-demo/document.json \
  --archive data/private/ingestion-demo/archive
```

Copy the returned `document_id` into the following commands:

```sh
.venv/bin/margin inspect-document DOCUMENT_ID --page 1 \
  --archive data/private/ingestion-demo/archive
.venv/bin/margin extract-document DOCUMENT_ID \
  --recipe data/private/ingestion-demo/recipe.json \
  --archive data/private/ingestion-demo/archive
```

The output is JSON. The demo produces three candidates: revenue `1234.50` crore, loss before tax `-120.25` crore, and a missing profit value represented by a dash. These are fictional test values. Each candidate includes original text, coordinates, context, source value and normalized INR value. Successful extraction returns `needs_review`; it does not mean the context is independently verified or that the value may be published.

Repeated imports with the same bytes and identical manifest return the same ID and `duplicate=true`. A different manifest creates a separate provenance record sharing the same stored bytes. Changed file bytes create a new version; previous records remain. Registrations with the same `filing_id` can be compared as versions, but correction/supersedes relationships are not inferred.

## Import a real document

Supply an explicit local PDF and a manifest matching the generated schema:

```sh
.venv/bin/margin ingestion-schema document > /tmp/margin-document-schema.json
.venv/bin/margin ingestion-schema recipe > /tmp/margin-recipe-schema.json
```

The document manifest records company ID/name, filing ID/title, real/synthetic classification, original URL, publication date, acquisition timestamp and declared usage basis. A date-only publication is preserved as `published_on`; no exact publication time is invented. Real documents require a source URL. `processing_scope` is currently `local_only`.

The manifest records operator declarations, not verified licensing. Keep originals and outputs under ignored `data/private/`. Archive company/filing IDs are currently descriptive references, not foreign keys to the metadata corpus; verify their identity before any future publication step. This separation allows date-only source provenance without weakening milestone 1's existing schema.

Files must be unencrypted PDFs of at most 25 MiB and 500 pages. Invalid inputs fail before archive creation. The importer stores original bytes without rewriting the PDF. It does not fetch a URL. A URL in the manifest is provenance only.

## Prepare an extraction recipe

1. Inspect the physical PDF page using `inspect-document`. Page numbers start at 1, independent of printed page labels.
2. Render the page and visually identify the relevant row and column. For local inspection, `pdfplumber` supports `page.to_image(resolution=150).save(...)`.
3. Set `document_sha256` to the import result's hash. A recipe for different bytes is rejected.
4. For every selected cell, specify regions for the value, row label, period header, basis header, unit header and accounting-standard text. Regions may be on different pages when notes provide context.
5. For every non-value region, copy the expected text from the inspection output. Extraction requires an exact match after whitespace normalization.
6. Set the intended metric, reporting period/kind, standalone/consolidated basis, standard, currency and source scale. Review these semantic assignments against the rendered source: text matching cannot prove that a chosen header belongs to a chosen cell.

Coordinates are PDF points using pdfplumber's `(x0, top, x1, bottom)` convention; use the page's returned bbox rather than assuming pixel coordinates. `within_bbox` selects fully contained characters. Keep enough margin to include the whole number and avoid neighboring columns. The example generator is a complete executable recipe reference.

Supported metrics are revenue from operations, profit before tax and profit for the period. Monetary values are INR, with rupee/lakh/crore/million scales. EPS, ownership attribution and other metrics require distinct contracts later. Indian and international digit grouping are supported, as are parenthesized losses and Unicode minus signs. Zero remains zero. Empty regions/dashes/NA become missing candidates; malformed or multi-number cells fail explicitly.

## Run the real-cell development study

After acquiring/importing the four financial-results packages from the catalog:

```sh
.venv/bin/python examples/evaluate_real_corpus.py --archive data/private/real-archive
```

This uses `examples/real-extraction/study.json` and four hash-bound recipes. It persists/replays extraction runs, compares 36 selected cells against visually transcribed development expectations and prints a JSON report. Exit 0 means all selected cells matched; missing documents, extraction failures or mismatches return exit 2. Use `--study PATH` for a separately prepared study; recipe paths must remain inside its directory. The provided study covers only consolidated Ind AS INR values in crore/million scales. It is not a general benchmark schema.

The recipes were developed on the same pages as the expected values. A match is not independent verification or accepted-fact publication. Current results and text-layer gaps are recorded in the [corpus trial](research/corpus-trial.md). Original PDFs remain private and absent from a fresh clone.

## Storage and reproducibility

`--archive DIR` uses `DIR/documents.sqlite3`, with a distinct application ID and schema version from the metadata store. Tables contain immutable PDF blobs keyed by SHA-256, provenance registrations, and extraction runs. Original bytes and registration records commit together. Unrelated databases are rejected. Reads do not create a missing archive; document bytes and provenance hashes are checked before inspection/extraction.

A run ID binds registration, recipe, pdfplumber/pdfminer versions and extractor version. Re-running the same recipe replays the recorded result. Changed recipes produce new runs, preserving previous attempts. Mapping failures are recorded alongside their indices; a run containing any such error returns `failed` and CLI exit code 2. Successful mappings in that failed run remain unreviewed candidates. Invalid recipe/schema/hash inputs and fatal PDF failures return errors before a run is recorded.

This is a small, operator-controlled local archive. Size/page limits are basic input bounds, not CPU/memory isolation for hostile uploads. OCR, unattended processing, automatic table/header recognition, approval records, fact publication, source scheduling and MCP evidence serving are not implemented. `ocr_required` means no extractable words on the inspected page; a blank page can produce the same status.

## Validation

See [current validation results](implementation.md#validation) for test counts and outcomes. Ingestion checks cover import/replay, deduplication, changed versions, corrupt bytes, provenance requirements, invalid/encrypted PDFs, size bounds, blank pages, exact decimal scaling, Indian grouping, missing versus zero, anchor/page/region errors and the CLI workflow. The synthetic PDF was rendered and visually inspected. These results establish behavior on controlled fixtures, not real financial-document accuracy.

Use the existing Ruff and pytest commands in [development](development.md). See the [acquisition log](research/ingestion-access-log.md) for real-document status. Seven real documents are now imported and four real extraction recipes have been run; see the [corpus trial](research/corpus-trial.md). Next: independent numeric/context review and a review/publication contract before exposing facts through MCP.
