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


def get_last_commit_diff(repo_path):
    """Diff completo do último commit (HEAD~1 -> HEAD)."""
    return rodar_git(repo_path, ["diff", "HEAD~1", "HEAD"])


def get_changed_files(repo_path):
    """Lista só os nomes dos arquivos alterados no último commit."""
    saida = rodar_git(repo_path, ["diff", "--name-only", "HEAD~1", "HEAD"])
    return saida.splitlines()

def get_diff_for_file(repo_path, file_path):
    """Diff de um arquivo específico no último commit."""
    return rodar_git(repo_path, ["diff", "HEAD~1", "HEAD", "--", file_path])


if __name__ == "__main__":
    repo = r"C:\Users\joao lima\OneDrive\Music\App Rotina"

    arquivos = get_changed_files(repo)
    relevantes = [a for a in arquivos if Path(a).suffix in EXTENSOES_RELEVANTES]

    print("Todos:", arquivos)
    print("Relevantes:", relevantes)