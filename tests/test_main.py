import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main


def _git(repo_path, *args):
    subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_gerar_relatorio_markdown_vazio():
    md = main.gerar_relatorio_markdown({})
    assert "Nenhum problema" in md


def test_gerar_relatorio_markdown_com_problemas():
    relatorio = {
        "app.py": [
            {
                "linha": "+12",
                "tipo": "Segurança",
                "severidade": "Alta",
                "descricao": "SQL Injection detectado",
                "sugestao": "Use query parametrizada",
            },
            {
                "linha": "+20",
                "tipo": "Arquitetura",
                "severidade": "Média",
                "descricao": "Falta tratamento de erro",
                "sugestao": "Adicione try/except",
            },
            {
                "linha": "+30",
                "tipo": "Performance",
                "severidade": "Baixa",
                "descricao": "Loop desnecessário",
                "sugestao": "Use set()",
            },
        ]
    }
    md = main.gerar_relatorio_markdown(relatorio)
    assert "🔴" in md
    assert "🟡" in md
    assert "🔵" in md
    assert "SQL Injection detectado" in md
    assert "`app.py`" in md


def test_deve_falhar_por_severidade():
    rel_alta = {"a.py": [{"severidade": "Alta"}]}
    rel_media = {"a.py": [{"severidade": "Média"}]}
    rel_baixa = {"a.py": [{"severidade": "Baixa"}]}

    assert main.deve_falhar({}, "baixa") is False
    assert main.deve_falhar(rel_alta, "none") is False
    assert main.deve_falhar(rel_alta, "alta") is True
    assert main.deve_falhar(rel_media, "alta") is False
    assert main.deve_falhar(rel_media, "media") is True
    assert main.deve_falhar(rel_baixa, "baixa") is True
    assert main.deve_falhar(rel_baixa, "media") is False


def test_parse_args_defaults_e_customizados():
    default_args = main.parse_args([])
    assert default_args.repo == "."
    assert default_args.base == "HEAD~1"
    assert default_args.head == "HEAD"
    assert default_args.output == "relatorio_commitguard.md"
    assert default_args.fail_on == "none"

    custom = main.parse_args(
        ["--repo", "/tmp/repo", "--base", "main", "--head", "feat", "--output", "out.md", "--fail-on", "alta"]
    )
    assert custom.repo == "/tmp/repo"
    assert custom.base == "main"
    assert custom.head == "feat"
    assert custom.output == "out.md"
    assert custom.fail_on == "alta"


def test_executar_commit_guard_ignora_extensoes_irrelevantes(tmp_path, monkeypatch):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "notas.txt").write_text("apenas texto\n", encoding="utf-8")
    _git(tmp_path, "add", "notas.txt")
    _git(tmp_path, "commit", "-m", "add txt")

    chamado = False

    def fake_analisar(diff_texto, nome_arquivo):
        nonlocal chamado
        chamado = True
        return []

    monkeypatch.setattr(main, "analisar_diff_com_gemini", fake_analisar)

    out_file = tmp_path / "relatorio.md"
    code = main.executar_commit_guard(
        repo_path=str(tmp_path),
        base_ref="HEAD~1",
        head_ref="HEAD",
        output_path=str(out_file),
        fail_on="alta",
    )

    assert code == 0
    assert chamado is False
    assert out_file.exists()
    assert "Nenhum problema" in out_file.read_text(encoding="utf-8")


def test_executar_commit_guard_falha_em_alta_e_gera_relatorio(tmp_path, monkeypatch):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "query.SQL").write_text("SELECT * FROM users;\n", encoding="utf-8")
    _git(tmp_path, "add", "query.SQL")
    _git(tmp_path, "commit", "-m", "add sql")

    def fake_analisar(diff_texto, nome_arquivo):
        return [
            {
                "linha": "+1",
                "tipo": "Segurança",
                "severidade": "Alta",
                "descricao": "SELECT * sem filtro",
                "sugestao": "Especifique as colunas",
            }
        ]

    monkeypatch.setattr(main, "analisar_diff_com_gemini", fake_analisar)

    out_file = tmp_path / "relatorio.md"
    code = main.executar_commit_guard(
        repo_path=str(tmp_path),
        base_ref="HEAD~1",
        head_ref="HEAD",
        output_path=str(out_file),
        fail_on="alta",
    )

    assert code == 1
    conteudo = out_file.read_text(encoding="utf-8")
    assert "query.SQL" in conteudo
    assert "SELECT * sem filtro" in conteudo
