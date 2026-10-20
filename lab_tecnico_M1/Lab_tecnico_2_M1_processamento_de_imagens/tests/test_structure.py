"""Verifica a estrutura de entrega exigida pelo contrato técnico da disciplina."""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "README.md",
    "REPORT.md",
    "AI_USAGE.md",
    "lab.json",
    "requirements.txt",
    "src/pdi_lab",
    "tests",
    "kernels",
    "images/input",
    "images/output",
    "results",
]

# Artefatos de ambiente que o contrato proibe entregar. Eles podem existir em
# disco durante o desenvolvimento, por isso a verificacao e sobre o .gitignore.
IGNORED_PATTERNS = [
    "__pycache__/",
    ".pytest_cache/",
    ".venv/",
    "build/",
]


def test_estrutura_do_projeto():
    for item in REQUIRED_PATHS:
        assert (PROJECT_ROOT / item).exists(), "faltando: " + item


def test_artefatos_de_ambiente_estao_ignorados():
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    for pattern in IGNORED_PATTERNS:
        assert pattern in gitignore, "faltando no .gitignore: " + pattern


def test_lab_json_valido():
    data = json.loads((PROJECT_ROOT / "lab.json").read_text(encoding="utf-8"))

    assert data["schema_version"] == 1
    assert data["lab"] == "m1.2"
    assert data["language"] == "python"
    assert data["student"]["name"]


def test_imagem_de_entrada_presente():
    entradas = list((PROJECT_ROOT / "images" / "input").glob("*.png"))

    assert entradas, "nenhuma imagem de entrada em images/input"
