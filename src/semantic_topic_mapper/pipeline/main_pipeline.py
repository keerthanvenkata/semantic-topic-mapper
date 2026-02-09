"""
Main pipeline orchestrator.

Wires ingestion, structure, references, entities, audit, and outputs into a
single end-to-end run. No LLM or business logic here — orchestration only.
"""

from __future__ import annotations

from pathlib import Path

from semantic_topic_mapper.audit.ambiguity_detector import run_audit
from semantic_topic_mapper.config import skip_llm
from semantic_topic_mapper.entities.definition_linker import link_entity_definitions
from semantic_topic_mapper.entities.deterministic_entity_detector import detect_entities
from semantic_topic_mapper.entities.entity_relationship_extractor import (
    extract_entity_relationships,
)
from semantic_topic_mapper.entities.llm_entity_enricher import (
    detect_entity_ambiguities,
    enrich_entity_types,
    extract_llm_entity_relationships,
)
from semantic_topic_mapper.ingestion.loader import load_text_file
from semantic_topic_mapper.outputs.ambiguity_report_exporter import export_ambiguity_report
from semantic_topic_mapper.outputs.entity_catalogue_exporter import export_entity_catalogue
from semantic_topic_mapper.outputs.entity_relationship_exporter import (
    export_entity_relationships,
)
from semantic_topic_mapper.outputs.reference_graph_exporter import export_reference_graph
from semantic_topic_mapper.outputs.topic_map_exporter import export_topic_map
from semantic_topic_mapper.references.reference_detector import detect_references
from semantic_topic_mapper.references.reference_graph_builder import build_reference_graph
from semantic_topic_mapper.structure.header_detector import detect_headers
from semantic_topic_mapper.structure.hierarchy_builder import build_topic_hierarchy
from semantic_topic_mapper.structure.segmenter import segment_into_topic_blocks


def run_pipeline(input_path: str, output_dir: str) -> None:
    """
    Run the full semantic topic mapper pipeline: load text, detect structure,
    build hierarchy and reference graph, extract entities, run audit, and
    write all deliverables to output_dir. This is the top-level orchestrator.
    """
    print("[Pipeline] Loading text...")
    text = load_text_file(input_path)

    print("[Pipeline] Detecting headers...")
    headers = detect_headers(text)

    print("[Pipeline] Segmenting into topic blocks...")
    blocks = segment_into_topic_blocks(text, headers)

    print("[Pipeline] Building topic hierarchy...")
    nodes = build_topic_hierarchy(blocks)

    print("[Pipeline] Detecting references...")
    references = detect_references(blocks)

    print("[Pipeline] Building reference graph and reference issues...")
    graph, reference_issues = build_reference_graph(nodes, references)

    print("[Pipeline] Detecting entities...")
    entities = detect_entities(blocks)

    print("[Pipeline] Linking entity definitions...")
    link_entity_definitions(entities, blocks)

    print("[Pipeline] Extracting entity relationships...")
    relationships = extract_entity_relationships(entities, blocks)

    if not skip_llm():
        print("[Pipeline] LLM enrichment (entity types, relationships, ambiguities)...")
        enrich_entity_types(entities, text)
        llm_relationships = extract_llm_entity_relationships(entities, text)
        relationships.extend(llm_relationships)
        llm_issues = detect_entity_ambiguities(entities, text)
    else:
        llm_issues = []

    print("[Pipeline] Running audit...")
    issues = run_audit(nodes, reference_issues, entities)
    issues.extend(llm_issues)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    print(f"[Pipeline] Writing deliverables to {out}...")

    export_topic_map(nodes, str(out / "topic_map.json"))
    print("  - topic_map.json")
    export_entity_catalogue(entities, str(out / "entity_catalogue.csv"))
    print("  - entity_catalogue.csv")
    export_entity_relationships(relationships, str(out / "entity_relationships.json"))
    print("  - entity_relationships.json")
    export_ambiguity_report(issues, str(out / "ambiguity_report.csv"))
    print("  - ambiguity_report.csv")
    export_reference_graph(graph, str(out / "cross_reference_graph.pdf"))
    print("  - cross_reference_graph.pdf")

    print("[Pipeline] Done.")


def run_pipeline_from_config() -> None:
    """
    Run the pipeline using INPUT_PATH and OUTPUT_DIR from config.
    Raises ValueError if INPUT_PATH is not set.
    """
    from semantic_topic_mapper.config import INPUT_PATH, OUTPUT_DIR

    if INPUT_PATH is None:
        raise ValueError(
            "INPUT_PATH is not set. Set it in .env (e.g. INPUT_PATH=data/sample_document.txt) "
            "or pass the file path as an argument: python -m semantic_topic_mapper path/to/file.txt"
        )
    run_pipeline(str(INPUT_PATH), str(OUTPUT_DIR))
