import sys
import json
from diff_reader import get_changed_files, EXTENSOES_RELEVANTES, get_diff_for_file
from ia import analisar_diff_com_gemini
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def executar_commit_guard(repo_path):
    print("Iniciando CommitGuard...\n", flush=True)
    
    # 1. Pega todos os arquivos alterados
    arquivos = get_changed_files(repo_path)
    
    # 2. Filtra os relevantes
    relevantes = [a for a in arquivos if Path(a).suffix in EXTENSOES_RELEVANTES]
    
    if not relevantes:
        print("Nenhum arquivo crítico modificado neste commit.", flush=True)
        return
    
    relatorio_geral = {}
    
    for arquivo in relevantes:
        print(f"\nAnalisando arquivo: {arquivo}", flush=True)
        diff_texto = get_diff_for_file(repo_path, arquivo)
        
        if not diff_texto.strip():
            continue  # Pula arquivos sem diff
        resultados_ia = analisar_diff_com_gemini(diff_texto, arquivo)
        
        if resultados_ia:
            relatorio_geral[arquivo] = resultados_ia
            
    print("\n================ RELATÓRIO FINAL ==================", flush=True)
    if not relatorio_geral:
        print("✅ Nenhum problema de segurança ou arquitetura encontrado!", flush=True)
    else:
        print(json.dumps(relatorio_geral, indent=2, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    # Coloque o caminho do seu repositório de teste aqui
    caminho_repo = r"C:\Users\joao lima\OneDrive\Music\App Rotina"
    executar_commit_guard(caminho_repo)
