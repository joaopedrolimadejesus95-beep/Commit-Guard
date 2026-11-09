# 🛡️ CommitGuard

O **CommitGuard** é uma ferramenta de **Code Review automatizado com IA** que analisa o `git diff` dos commits em busca de problemas reais de **segurança**, **arquitetura** e **performance**, ignorando detalhes cosméticos de formatação ou estilo.

> 🚧 **Status do Projeto:** Em desenvolvimento ativo (evoluindo continuamente com novas funcionalidades).

---

## 🎯 O que ele analisa?

Utilizando a API do **Google Gemini** com saída estruturada (JSON Schema), o CommitGuard atua como um Tech Lead rigoroso focando em:

1. **Segurança:** SQL Injection, XSS, exposição de credenciais/chaves de API, Prompt Injection.
2. **Arquitetura:** Acoplamento excessivo, quebra de Injeção de Dependência, ausência de tratamento de erros.
3. **Performance:** Consultas N+1 ao banco de dados, falta de índices em chaves estrangeiras, vazamento de recursos/memória.

---

## ⚙️ Como funciona hoje

1. Lê o último commit do repositório alvo via `git diff` (`diff_reader.py`).
2. Filtra apenas extensões de código relevantes (`.java`, `.py`, `.js`, `.ts`, `.sql`, `.html`, `.xml`, `.properties`, `.php`).
3. Envia as alterações para análise na API do Gemini (`ia.py`).
4. Gera um relatório consolidado em JSON indicando **linha**, **categoria**, **severidade**, **descrição do problema** e **sugestão de correção** (`main.py`).

---

## 🚀 Como executar

1. Clone este repositório e instale as dependências:
   ```bash
   pip install google-genai python-dotenv
   ```
2. Crie um arquivo `.env` na raiz com sua chave da API do Gemini:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```
3. Configure o caminho do repositório que deseja analisar em `main.py` e execute:
   ```bash
   python main.py
   ```

---

## 🗺️ Roadmap (Próximas evoluções)

- [x] Extração automática de `git diff` por arquivo e filtro por extensão
- [x] Integração com Google Gemini e resposta padronizada via JSON Schema
- [ ] Análise em lote (enviar múltiplos diffs em uma única requisição para otimizar cota)
- [ ] Integração com **Git Hooks** (`pre-commit` / `pre-push`) para bloquear commits críticos automaticamente
- [ ] Passagem do caminho do repositório via linha de comando (CLI)
- [ ] Exportação de relatórios em Markdown / HTML
- [ ] Integração com GitHub Actions para rodar em Pull Requests
