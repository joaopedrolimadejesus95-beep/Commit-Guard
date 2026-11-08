import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

def analisar_diff_com_gemini(diff_texto, nome_arquivo):
    
    """Envia o diff de um arquivo para o Gemini atuar como um Code Reviewer rigoroso."""
    
    system_prompt = """Você é um Tech Lead Sênior extremamente rigoroso focado em segurança e arquitetura.
                    Sua tarefa é revisar o `diff` de um código.
                    IGNORE completamente problemas de estilo, formatação, tabulação ou aspas.
                    Foque EXCLUSIVAMENTE em:
                    1. Vulnerabilidades de segurança (SQL Injection, XSS, vazamento de chaves, Prompt Injection).
                    2. Problemas graves de arquitetura (acoplamento excessivo, falta de tratamento de erros, consultas ineficientes ao banco).
                    3. Vazamento de memória ou problemas crônicos de performance.

Se o código estiver limpo em relação a esses pontos, retorne um array vazio"""


    # Isso garante que a IA sempre devolva os dados do mesmo jeito que você precisa
    schema_resposta = types.Schema(
        type = types.Type.ARRAY,
        description = "Lista de problemas encontrados no diff do arquivo",
        items = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "linha": types.Schema(type=types.Type.STRING, description="Linha ou bloco do problema (ex: +34)"),
                "tipo": types.Schema(type=types.Type.STRING, description="Categoria do problema (Segurança, Arquitetura, Performance)"),
                "severidade": types.Schema(type=types.Type.STRING, description="Alta, Media, ou Baixa"),
                "descricao": types.Schema(type=types.Type.STRING, description="Explicação curta do bug"),
                "sugestao": types.Schema(type=types.Type.STRING, description="Sugestão de código para corrigir"),
            },
            required=["linha", "tipo", "severidade", "descricao", "sugestao"]
        )
    )
    print(f"Analisando: {nome_arquivo}...", flush=True)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=f"Aqui está o diff do arquivo {nome_arquivo}:\n\n{diff_texto}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=schema_resposta,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro ao analisar {nome_arquivo}: {e}", flush=True)
        return []
    
    
if __name__ == "__main__":
    diff_simulado = """
@@ -10,4 +10,5 @@ def buscar_usuario(cursor, username):
-    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
+    query = f"SELECT * FROM users WHERE username = '{username}'"
+    cursor.execute(query)
"""
    resultados = analisar_diff_com_gemini(diff_simulado, "db_controller.py")
    
    # Imprimindo o resultado formatado
    print("\n--- Relatório do CommitGuard ---")
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
