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

## 🚀 Como executar localmente

1. Clone este repositório e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Crie um arquivo `.env` na raiz com sua chave da API do Gemini:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```
3. Execute apontando para o repositório alvo via CLI:
   ```bash
   python main.py --repo /caminho/do/repositorio --base HEAD~1 --head HEAD
   ```

Opções disponíveis na CLI:
- `--repo`: Caminho do repositório Git (padrão: `.`).
- `--base`: Commit ou branch base para comparação (padrão: `HEAD~1`).
- `--head`: Commit ou branch alvo (padrão: `HEAD`).
- `--output`: Caminho do relatório Markdown gerado (padrão: `relatorio_commitguard.md`).
- `--fail-on`: Retorna código de saída `1` se encontrar problemas a partir da severidade informada (`none`, `baixa`, `media`, `alta`).

---

## 🤖 Automação com GitHub Actions

O projeto já inclui o workflow [`.github/workflows/commit-guard.yml`](.github/workflows/commit-guard.yml) que roda automaticamente em **Pull Requests** e **pushes** na `main`/`master`:

1. No seu repositório do GitHub, acesse **Settings → Secrets and variables → Actions**.
2. Crie um novo secret chamado `GEMINI_API_KEY` com a sua chave da API do Google Gemini.
3. A cada Pull Request aberto ou atualizado, o CommitGuard analisa o diff, publica o relatório no **Summary** da Action, comenta (ou atualiza o comentário) diretamente no PR e bloqueia o merge caso encontre problemas de severidade **Alta**.

---

## 🗺️ Roadmap (Próximas evoluções)

- [x] Extração automática de `git diff` por arquivo e filtro por extensão
- [x] Integração com Google Gemini e resposta padronizada via JSON Schema
- [x] Passagem do caminho do repositório via linha de comando (CLI)
- [x] Exportação de relatórios em Markdown
- [x] Integração com GitHub Actions para rodar em Pull Requests
- [ ] Análise em lote (enviar múltiplos diffs em uma única requisição para otimizar cota)
- [ ] Integração com **Git Hooks** (`pre-commit` / `pre-push`) para bloquear commits críticos automaticamente
