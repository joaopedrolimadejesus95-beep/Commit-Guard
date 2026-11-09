import sys
import json
import concurrent.futures
from diff_reader import get_changed_files, EXTENSOES_RELEVANTES, get_diff_for_file
from ia import analisar_diff_com_gemini
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def gerar_relatorio_markdown(relatorio_json):
    if not relatorio_json:
        return "✅ **CommitGuard:** Nenhum problema de arquitetura ou segurança detectado neste commit."
    
    linhas_md = ["# 🛡️ Relatório do CommitGuard\n"]
    for arquivo, problemas in relatorio_json.items():
        linhas_md.append(f"## 📄 `{arquivo}`\n")
        for prob in problemas:
            sev = prob.get("severidade", "").lower()
            icone = "🔴" if sev == "alta" else "🟡" if sev == "media" else "🔵"
            linhas_md.append(f"### {icone} [{prob['tipo']}] Alteração: {prob['linha']}")
            linhas_md.append(f"**Problema:** {prob['descricao']}\n")
            linhas_md.append(f"**Sugestão:**\n```\n{prob['sugestao']}\n```\n")
        linhas_md.append("---\n")
    return "\n".join(linhas_md)

def processar_arquivo(repo_path, arquivo):
    """Função isolada para rodar em paralelo dentro de uma Thread."""
    diff_texto = get_diff_for_file(repo_path, arquivo)
    if not diff_texto.strip():
        return arquivo, None
        
    print(f"Enviando para IA: {arquivo}...", flush=True)
    resultados_ia = analisar_diff_com_gemini(diff_texto, arquivo)
    return arquivo, resultados_ia

def executar_commit_guard(repo_path):
    print("Iniciando CommitGuard...\n", flush=True)
    arquivos = get_changed_files(repo_path)
    relevantes = [a for a in arquivos if Path(a).suffix in EXTENSOES_RELEVANTES]
    
    if not relevantes:
        print("Nenhum arquivo crítico modificado neste commit.", flush=True)
        return
    
    relatorio_geral = {}
    print(f"Iniciando análise paralela de {len(relevantes)} arquivos...\n", flush=True)
    
    # Executa as chamadas em paralelo (até 5 ao mesmo tempo)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Prepara as tarefas
        futuros = {executor.submit(processar_arquivo, repo_path, arq): arq for arq in relevantes}
        
        # Coleta os resultados assim que cada thread termina
        for futuro in concurrent.futures.as_completed(futuros):
            arquivo, resultados_ia = futuro.result()
            if resultados_ia:
                relatorio_geral[arquivo] = resultados_ia
                print(f"✅ Análise concluída: {arquivo}", flush=True)
            
    print("\n================ RELATÓRIO FINAL ==================", flush=True)
    if not relatorio_geral:
        print("✅ Nenhum problema de segurança ou arquitetura encontrado!", flush=True)
    else:
        relatorio_md = gerar_relatorio_markdown(relatorio_geral)
        print(relatorio_md)
        with open("relatorio_commitguard.md", "w", encoding="utf-8") as f:
            f.write(relatorio_md)
            print("\n[!] Relatório salvo em 'relatorio_commitguard.md'")

if __name__ == "__main__":
    caminho_repo = r"C:\Users\joao lima\OneDrive\Music\App Rotina"
    executar_commit_guard(caminho_repo)