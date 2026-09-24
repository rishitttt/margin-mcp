"""Explicit local import and stdio server entry points."""

import argparse
import json
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from margin_mcp.models import Corpus
from margin_mcp.storage import CorpusStore, MarginError, load_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="margin", description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    importer = subcommands.add_parser(
        "import-corpus", help="Validate and import a local JSON corpus"
    )
    importer.add_argument("manifest", type=Path)
    importer.add_argument("--db", type=Path, required=True)
    importer.add_argument(
        "--replace", action="store_true", help="Replace the entire existing corpus"
    )
    serve = subcommands.add_parser("serve", help="Run read-only MCP tools over stdio")
    serve.add_argument("--db", type=Path, required=True)
    subcommands.add_parser("schema", help="Print the versioned corpus JSON Schema")
    document = subcommands.add_parser("import-document", help="Register a private local PDF")
    document.add_argument("pdf", type=Path)
    document.add_argument("--manifest", type=Path, required=True)
    document.add_argument("--archive", type=Path, required=True)
    inspect = subcommands.add_parser(
        "inspect-document", help="Inspect one PDF page and coordinates"
    )
    inspect.add_argument("document_id")
    inspect.add_argument("--page", type=int, required=True)
    inspect.add_argument("--archive", type=Path, required=True)
    extract = subcommands.add_parser("extract-document", help="Extract unreviewed financial cells")
    extract.add_argument("document_id")
    extract.add_argument("--recipe", type=Path, required=True)
    extract.add_argument("--archive", type=Path, required=True)
    ingestion_schema = subcommands.add_parser(
        "ingestion-schema", help="Print ingestion JSON Schema"
    )
    ingestion_schema.add_argument("kind", choices=["document", "recipe"])
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
    try:
        if args.command in {
            "import-document",
            "inspect-document",
            "extract-document",
            "ingestion-schema",
        }:
            from margin_mcp.ingestion import DocumentArchive, read_json
            from margin_mcp.ingestion_models import DocumentManifest, ExtractionRecipe

            if args.command == "ingestion-schema":
                model = DocumentManifest if args.kind == "document" else ExtractionRecipe
                result = model.model_json_schema()
            else:
                archive = DocumentArchive(args.archive)
                if args.command == "import-document":
                    result = archive.import_document(
                        args.pdf, DocumentManifest.model_validate(read_json(args.manifest))
                    )
                elif args.command == "inspect-document":
                    result = archive.inspect(args.document_id, args.page)
                else:
                    result = archive.extract(
                        args.document_id, ExtractionRecipe.model_validate(read_json(args.recipe))
                    )
            print(json.dumps(result, indent=2))
            if result.get("status") == "failed":
                return 2
        elif args.command == "schema":
            print(json.dumps(Corpus.model_json_schema(), indent=2))
        elif args.command == "import-corpus":
            corpus = load_manifest(args.manifest)
            snapshot = CorpusStore(args.db).import_corpus(corpus, replace=args.replace)
            print(
                json.dumps(
                    {
                        "corpus_id": corpus.corpus_id,
                        "data_kind": corpus.data_kind,
                        "companies": len(corpus.companies),
                        "filings": len(corpus.filings),
                        "corpus_revision": snapshot.revision,
                        "imported_at": snapshot.imported_at.isoformat(),
                    },
                    indent=2,
                )
            )
        else:
            from margin_mcp.server import create_server

            create_server(args.db).run(transport="stdio")
        return 0
    except (MarginError, ValidationError, OSError) as exc:
        print(f"margin: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
