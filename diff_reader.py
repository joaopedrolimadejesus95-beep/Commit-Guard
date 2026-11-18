import subprocess
from pathlib import Path

# Extensões de arquivo que interessam pra análise de segurança
EXTENSOES_RELEVANTES = {".java", ".py", ".js", ".ts", ".sql", ".html", ".xml", ".properties", ".php"}


def rodar_git(repo_path, args):
    """Roda um comando git dentro do repositório e devolve a saída como texto."""
    result = subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


EMPTY_TREE_HASH = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def resolver_base_ref(repo_path, base_ref):
    """Resolve a referência base; se não existir (ex: primeiro commit), usa a árvore vazia."""
    if not base_ref or set(base_ref) == {"0"}:
        return EMPTY_TREE_HASH
    try:
        rodar_git(repo_path, ["rev-parse", "--verify", base_ref])
        return base_ref
    except RuntimeError:
        return EMPTY_TREE_HASH


def get_last_commit_diff(repo_path, base_ref="HEAD~1", head_ref="HEAD"):
    """Diff completo entre base_ref e head_ref (padrão: HEAD~1 -> HEAD)."""
    base = resolver_base_ref(repo_path, base_ref)
    return rodar_git(repo_path, ["diff", base, head_ref])


def get_changed_files(repo_path, base_ref="HEAD~1", head_ref="HEAD"):
    """Lista os nomes dos arquivos alterados entre base_ref e head_ref."""
    base = resolver_base_ref(repo_path, base_ref)
    saida = rodar_git(repo_path, ["diff", "--name-only", base, head_ref])
    return [linha for linha in saida.splitlines() if linha.strip()]


def get_diff_for_file(repo_path, file_path, base_ref="HEAD~1", head_ref="HEAD"):
    """Diff de um arquivo específico entre base_ref e head_ref."""
    base = resolver_base_ref(repo_path, base_ref)
    return rodar_git(repo_path, ["diff", base, head_ref, "--", file_path])


if __name__ == "__main__":
    repo = r"C:\Users\joao lima\OneDrive\Music\App Rotina"

    arquivos = get_changed_files(repo)
    relevantes = [a for a in arquivos if Path(a).suffix in EXTENSOES_RELEVANTES]

    print("Todos:", arquivos)
    print("Relevantes:", relevantes)