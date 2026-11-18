import argparse
import concurrent.futures
import sys
from pathlib import Path

from diff_reader import EXTENSOES_RELEVANTES, get_changed_files, get_diff_for_file
from ia import analisar_diff_com_gemini

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SEVERIDADE_NIVEL = {
    "baixa": 1,
    "media": 2,
    "média": 2,
    "alta": 3,
}


def gerar_relatorio_markdown(relatorio_json):
    if not relatorio_json:
        return "✅ **CommitGuard:** Nenhum problema de arquitetura ou segurança detectado neste commit."

    linhas_md = ["# 🛡️ Relatório do CommitGuard\n"]
    for arquivo, problemas in relatorio_json.items():
        linhas_md.append(f"## 📄 `{arquivo}`\n")
        for prob in problemas:
            sev = prob.get("severidade", "").lower()
            icone = "🔴" if sev == "alta" else "🟡" if sev in ("media", "média") else "🔵"
            tipo = prob.get("tipo", "Geral")
            linha = prob.get("linha", "?")
            linhas_md.append(f"### {icone} [{tipo}] Alteração: {linha} (Severidade: {prob.get('severidade', 'N/A')})")
            linhas_md.append(f"**Problema:** {prob.get('descricao', '')}\n")
            linhas_md.append(f"**Sugestão:**\n```\n{prob.get('sugestao', '')}\n```\n")
        linhas_md.append("---\n")
    return "\n".join(linhas_md)


def processar_arquivo(repo_path, arquivo, base_ref="HEAD~1", head_ref="HEAD"):
    """Função isolada para rodar em paralelo dentro de uma Thread."""
    diff_texto = get_diff_for_file(repo_path, arquivo, base_ref=base_ref, head_ref=head_ref)
    if not diff_texto.strip():
        return arquivo, None

    print(f"Enviando para IA: {arquivo}...", flush=True)
    resultados_ia = analisar_diff_com_gemini(diff_texto, arquivo)
    return arquivo, resultados_ia


def deve_falhar(relatorio_geral, fail_on):
    """Retorna True se houver algum problema com severidade >= fail_on."""
    if fail_on == "none" or not relatorio_geral:
        return False

    limite = SEVERIDADE_NIVEL[fail_on]
    for problemas in relatorio_geral.values():
        for prob in problemas:
            sev = prob.get("severidade", "").strip().lower()
            if SEVERIDADE_NIVEL.get(sev, 0) >= limite:
                return True
    return False


def executar_commit_guard(
    repo_path,
    base_ref="HEAD~1",
    head_ref="HEAD",
    output_path="relatorio_commitguard.md",
    fail_on="none",
):
    print(f"Iniciando CommitGuard em '{repo_path}' ({base_ref}..{head_ref})...\n", flush=True)
    arquivos = get_changed_files(repo_path, base_ref=base_ref, head_ref=head_ref)
    relevantes = [a for a in arquivos if Path(a).suffix.lower() in EXTENSOES_RELEVANTES]

    relatorio_geral = {}
    if not relevantes:
        print("Nenhum arquivo crítico modificado neste intervalo.", flush=True)
    else:
        print(f"Iniciando análise paralela de {len(relevantes)} arquivo(s)...\n", flush=True)

        # Executa as chamadas em paralelo (até 5 ao mesmo tempo)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futuros = {
                executor.submit(processar_arquivo, repo_path, arq, base_ref, head_ref): arq
                for arq in relevantes
            }

            for futuro in concurrent.futures.as_completed(futuros):
                arquivo, resultados_ia = futuro.result()
                if resultados_ia:
                    relatorio_geral[arquivo] = resultados_ia
                    print(f"✅ Análise concluída: {arquivo}", flush=True)

    print("\n================ RELATÓRIO FINAL ==================", flush=True)
    relatorio_md = gerar_relatorio_markdown(relatorio_geral)
    print(relatorio_md)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(relatorio_md)
        print(f"\n[!] Relatório salvo em '{output_path}'")

    return 1 if deve_falhar(relatorio_geral, fail_on) else 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="CommitGuard - Code Review automatizado com IA focado em segurança, arquitetura e performance."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Caminho do repositório Git a ser analisado (padrão: diretório atual).",
    )
    parser.add_argument(
        "--base",
        default="HEAD~1",
        help="Commit ou branch base para comparação (padrão: HEAD~1).",
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="Commit ou branch alvo para comparação (padrão: HEAD).",
    )
    parser.add_argument(
        "--output",
        default="relatorio_commitguard.md",
        help="Caminho do arquivo Markdown de saída (padrão: relatorio_commitguard.md).",
    )
    parser.add_argument(
        "--fail-on",
        choices=["none", "baixa", "media", "alta"],
        default="none",
        help="Retorna código de saída 1 se encontrar problemas a partir desta severidade (padrão: none).",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    exit_code = executar_commit_guard(
        repo_path=args.repo,
        base_ref=args.base,
        head_ref=args.head,
        output_path=args.output,
        fail_on=args.fail_on,
    )
    sys.exit(exit_code)
