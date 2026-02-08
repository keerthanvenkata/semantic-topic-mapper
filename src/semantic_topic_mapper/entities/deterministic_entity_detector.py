"""
Deterministic entity mention detection.

Prioritizes precision over recall: some entity mentions may be missed in this
stage. Subsequent LLM-based enrichment can propose additional entities or
link implicit mentions, but such outputs are treated as advisory and surfaced
with confidence signals rather than altering the deterministic backbone
automatically.
"""
