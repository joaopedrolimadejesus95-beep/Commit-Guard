import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ia


def test_get_client_sem_api_key_lanca_erro(monkeypatch):
    monkeypatch.setattr(ia, "_client", None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        ia._get_client()


def test_analisar_diff_com_gemini_sucesso(monkeypatch):
    payload = [
        {
            "linha": "+4",
            "tipo": "Segurança",
            "severidade": "Alta",
            "descricao": "SQL Injection",
            "sugestao": "Use parâmetros",
        }
    ]

    class FakeModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text=json.dumps(payload))

    fake_client = SimpleNamespace(models=FakeModels())
    monkeypatch.setattr(ia, "_get_client", lambda: fake_client)

    resultado = ia.analisar_diff_com_gemini("+ query = f'...'", "db.py")
    assert resultado == payload


def test_analisar_diff_com_gemini_erro_retorna_lista_vazia(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("API indisponível")

    fake_client = SimpleNamespace(models=FakeModels())
    monkeypatch.setattr(ia, "_get_client", lambda: fake_client)

    resultado = ia.analisar_diff_com_gemini("+ x = 1", "app.py")
    assert resultado == []
