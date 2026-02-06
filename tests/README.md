# Tests

Run from **project root** with the **venv activated** and **PYTHONPATH** set so `semantic_topic_mapper` is importable.

**Windows (PowerShell):**

```powershell
cd D:\dev\projects\semantic-topic-mapper
venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python tests/test_topic_models.py
```

**Or with pytest (if installed):**

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/ -v
```

The test file adds `src` to `sys.path` when run as a script, but setting `PYTHONPATH=src` from the project root is required for `python -m pytest` and keeps behavior consistent.
