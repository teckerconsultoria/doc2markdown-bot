# Diário Técnico — doc2markdown-bot

**Data:** 24/03/2026
**Repositório:** https://github.com/teckerconsultoria/doc2markdown-bot
**Sessão:** reorganização, publicação no GitHub e refactoring guiado por testes

---

## Visão Geral da Sessão

Esta sessão cobriu três fases distintas:

1. **Reorganização do projeto** — estrutura de pastas bagunçada, sem git
2. **Publicação no GitHub** — repositório criado e código publicado
3. **Refactoring com TDD** — 6 bugs/melhorias implementadas em 7 tasks via subagentes

---

## Fase 1 — Reorganização do Projeto

### Situação inicial

O projeto estava nesta estrutura confusa:

```
doc2markdown-bot/
├── 00_LEIA_PRIMEIRO.txt          ← documentos de entrega na raiz
├── CHECKLIST.md
├── GUIA_FINAL.md
├── INDICE.md
├── LISTA_ARQUIVOS_ENTREGUES.txt
├── RESUMO_ENTREGA.md
├── RESUMO_EXECUTIVO.md
├── doc2markdown-bot-github-ready/       ← código enterrado 2 níveis abaixo
│   └── doc2markdown-bot-github/
│       ├── bot.py
│       ├── keep_alive.py
│       └── ...
└── doc2markdown-bot-github-ready.zip   ← duplicata do conteúdo acima
```

### Ações realizadas

| Ação | Resultado |
|------|-----------|
| Mover documentos de entrega → `docs/` | Preservados sem exclusão |
| Mover código de `doc2markdown-bot-github-ready/doc2markdown-bot-github/` → raiz | Código acessível no nível certo |
| Deletar pasta aninhada e `.zip` | Sem duplicatas |
| Adicionar `.claude/` e `CLAUDE.md` ao `.gitignore` | Configs internas do Claude Code não versionadas |

### Estrutura final

```
doc2markdown-bot/
├── .github/            ← templates e CI/CD
├── docs/               ← documentação de entrega + planos técnicos
├── tests/              ← criado na fase de refactoring
├── bot.py
├── keep_alive.py
├── requirements.txt
├── render.yaml
├── .gitignore
└── LICENSE
```

---

## Fase 2 — Publicação no GitHub

### Commit inicial

```
c55ae1d — chore: initial commit
```

- 24 arquivos, 4.123 inserções
- Inclui código, 7 docs de entrega em `docs/`, templates GitHub (`.github/`), CI/CD (`tests.yml`), licença MIT

### Criação do repositório

```bash
gh repo create doc2markdown-bot --public \
  --description "Bot Telegram que converte documentos para Markdown" \
  --source . --remote origin --push
```

Repositório criado em: **https://github.com/teckerconsultoria/doc2markdown-bot**

---

## Fase 3 — Refactoring com TDD (7 Tasks)

### Diagnóstico inicial

Análise do código (`bot.py` — 221 linhas, `keep_alive.py` — 38 linhas) revelou 6 problemas:

| # | Arquivo | Problema | Severidade |
|---|---------|----------|------------|
| 1 | `bot.py:126,169` | `asyncio.get_event_loop()` deprecated no Python 3.10+ | Bug |
| 2 | `bot.py:131` | `os.unlink()` sem `try/finally` — temp file vaza em exceções | Bug |
| 3 | `keep_alive.py` | Flask como dependência só para 2 rotas | Desnecessário |
| 4 | `bot.py:98,151` | Lógica de conversão duplicada em `handle_document` e `handle_url` | DRY |
| 5 | `bot.py:175` | Derivação de stem de URL com `.replace()` encadeados frágeis | Qualidade |
| 6 | `bot.py:98` | Sem verificação de tamanho de arquivo | Robustez |

Plano salvo em: `docs/superpowers/plans/2026-03-24-refactoring.md`

---

### Task 1 — Setup de testes

**Commit:** `85ebb18`
**Arquivos:** `tests/__init__.py`, `tests/conftest.py`, `requirements.txt`

Criação da infraestrutura de testes:

- `tests/conftest.py` com fixtures `mock_update` e `mock_context` para simular objetos Telegram
- `requirements.txt` com `pytest`, `pytest-asyncio`, `pytest-mock`
- Flask mantido neste commit — removido somente na Task 4 após testes de baseline

```python
# conftest.py — fixtures criadas
@pytest.fixture
def mock_update(): ...   # simula Update do Telegram com document, chat_id, etc.

@pytest.fixture
def mock_context(): ...  # simula bot.get_file e bot.send_document
```

---

### Task 2 — Fix: `asyncio.get_event_loop()` deprecated

**Commit:** `136142a`
**Arquivos:** `bot.py` (2 linhas), `tests/test_bot.py` (novo)

**Problema:** `get_event_loop()` levanta `DeprecationWarning` no Python 3.10+ quando chamado dentro de um loop async já em execução.

**Solução:** substituir por `get_running_loop()`, que é a chamada correta dentro de corotinas.

**Abordagem TDD:** teste AST que analisa o código-fonte em busca do padrão deprecado:

```python
def test_no_get_event_loop_in_bot():
    source = BOT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "get_event_loop":
            pytest.fail(f"bot.py linha {node.lineno}: use get_running_loop()")
```

O teste falhou antes da correção (detectou linhas 126 e 169) e passou após.

---

### Task 3 — Fix: vazamento de temp file

**Commit:** `9755ceb` *(commit combinado com Task 4 — ver nota abaixo)*
**Arquivos:** `bot.py` (handle_document), `tests/test_bot.py`

**Problema:** `os.unlink(tmp_path)` só era chamado no caminho feliz. Se `get_converter().convert()` lançasse exceção, o temp file nunca era deletado.

**Solução:**

```python
# ANTES
os.unlink(tmp_path)  # só executava em caso de sucesso

# DEPOIS
try:
    await tg_file.download_to_drive(tmp_path)
    await _convert_and_send(...)
finally:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
```

O `try/finally` cobre tanto o download quanto a conversão, garantindo limpeza em qualquer cenário.

**Teste:**

```python
@pytest.mark.asyncio
async def test_temp_file_cleaned_up_on_converter_error(...):
    # Rastreia arquivos criados via NamedTemporaryFile
    # Injeta RuntimeError no converter
    # Verifica que nenhum arquivo permanece no disco
```

> **Nota:** O subagente de Task 3 acidentalmente commitou arquivos de cache do pip (`pip-metadata-*/`, `*.whl.metadata`) junto com as mudanças reais. O `.gitignore` foi atualizado na Task 7 para prevenir recorrência, mas os arquivos permanecem no histórico do commit `9755ceb`.

---

### Task 4 — Refactor: Flask → stdlib `http.server`

**Commit:** `9755ceb` *(combinado com Task 3 — lock de git durante execução paralela)*
**Arquivos:** `keep_alive.py`, `requirements.txt`, `tests/test_keep_alive.py`

**Problema:** Flask (`flask>=3.0.0`) era uma dependência pesada usada apenas para responder a dois endpoints simples de keep-alive no Render.

**Solução:** reescrever `keep_alive.py` usando apenas a stdlib:

```python
# ANTES (38 linhas com Flask)
from flask import Flask
app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

# DEPOIS (stdlib pura)
from http.server import BaseHTTPRequestHandler, HTTPServer

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass  # silencia logs
    def do_GET(self):
        if self.path == "/health":
            # retorna JSON {"status": "ok"}
        else:
            # retorna texto de status
```

**Testes com session-scoped fixture** (evita conflito de porta e garante independência entre testes):

```python
@pytest.fixture(scope="session", autouse=True)
def keep_alive_server():
    os.environ["PORT"] = str(TEST_PORT)  # porta 18080
    from keep_alive import start_keep_alive
    start_keep_alive()
    time.sleep(0.3)
    yield
```

Baseline com Flask passou → reescrita → testes passaram sem Flask.

---

### Task 5 — Refactor: extrair `_convert_and_send` (DRY)

**Commit:** `c1d82ea`
**Arquivos:** `bot.py`, `tests/test_bot.py`, `tests/conftest.py`

**Problema:** `handle_document` e `handle_url` tinham a mesma lógica de conversão duplicada (~30 linhas cada): executor, encode, send_document, delete status, handle error.

**Solução:** extrair helper privado:

```python
async def _convert_and_send(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    source: str,          # path local ou URL
    stem: str,            # nome base do arquivo .md
    status_msg,           # mensagem de status para editar em caso de erro
) -> None:
    try:
        loop = asyncio.get_running_loop()
        md_content = await loop.run_in_executor(
            None,
            lambda: get_converter().convert(source).document.export_to_markdown(),
        )
        await context.bot.send_document(filename=f"{stem}.md", ...)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Erro ao converter:\n`{str(e)[:300]}`")
```

**Adições neste commit:**
- `mock_status_message` fixture em `conftest.py` (com `edit_text` e `delete` como `AsyncMock`)
- Verificação de tamanho de arquivo (`> 20 MB`) em `handle_document`
- `try/finally` estendido para cobrir também `download_to_drive` (bug adicional detectado em code review)

---

### Task 6 — Refactor: `_stem_from_url` com urllib.parse

**Commit:** `d79d43c`
**Arquivos:** `bot.py`, `tests/test_bot.py`

**Problema:** derivação do stem de URL em `handle_url` usava `.replace()` encadeados em lista hardcoded de extensões — frágil e não testado:

```python
# ANTES (frágil)
url_path = text.rstrip("/").split("/")[-1].split("?")[0]
stem = url_path.replace(".pdf", "").replace(".html", "").replace(".htm", "") or "document"
```

**Solução:** usar `urllib.parse` e `pathlib.Path`:

```python
def _stem_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    stem = Path(path).stem if path else "document"
    return (stem or "document")[:60]
```

`handle_url` refatorado para usar `_stem_from_url` + `_convert_and_send`.

**Testes parametrizados (7 casos):**

```python
@pytest.mark.parametrize("url,expected", [
    ("https://example.com/report.pdf",         "report"),
    ("https://example.com/page.html",          "page"),
    ("https://example.com/path/to/doc.docx",   "doc"),
    ("https://example.com/",                   "document"),  # fallback
    ("https://example.com/no-extension",       "no-extension"),
    ("https://example.com/file.pdf?token=abc", "file"),      # ignora query string
    ("https://example.com/" + "a" * 100,       "a" * 60),   # trunca em 60 chars
])
```

---

### Task 7 — Verificação final e push

**Commits:** `d0f09a8`, `bf58c02`

**d0f09a8 — fix de qualidade:**
Fixture `mock_status_message` estava declarada em `conftest.py` mas nunca injetada nos testes que a precisavam. Os testes criavam `AsyncMock()` inline, tornando a fixture letra morta. Ambos os testes `test_convert_and_send_*` foram atualizados para recebê-la como parâmetro.

**bf58c02 — gitignore:**
Padrões `pip-*/` e `*.whl` adicionados ao `.gitignore` para evitar que cache do pip seja commitado futuramente (problema que ocorreu no commit 9755ceb).

**Suite final:** 13 testes, todos PASSED.

```
tests/test_bot.py::test_no_get_event_loop_in_bot                    PASSED
tests/test_bot.py::test_temp_file_cleaned_up_on_converter_error     PASSED
tests/test_bot.py::test_convert_and_send_sends_document             PASSED
tests/test_bot.py::test_convert_and_send_edits_status_on_error      PASSED
tests/test_bot.py::test_stem_from_url[...] × 7 casos               PASSED
tests/test_keep_alive.py::test_health_endpoint_returns_200          PASSED
tests/test_keep_alive.py::test_root_endpoint_returns_200            PASSED
```

---

## Histórico de Commits

| SHA | Tipo | Descrição |
|-----|------|-----------|
| `c55ae1d` | chore | initial commit — bot + docs + GitHub templates |
| `85ebb18` | test | setup infraestrutura de testes com pytest-asyncio |
| `136142a` | fix | substituir `get_event_loop()` por `get_running_loop()` |
| `9755ceb` | fix | temp file cleanup via `try/finally` + Flask → `http.server` |
| `c1d82ea` | refactor | extrair `_convert_and_send` + guard 20MB + DRY |
| `d79d43c` | refactor | `_stem_from_url` com `urllib.parse` |
| `d0f09a8` | test | conectar `mock_status_message` fixture |
| `bf58c02` | chore | adicionar `pip-*/` e `*.whl` ao `.gitignore` |

---

## Métricas da Sessão

| Métrica | Valor |
|---------|-------|
| Duração total | ~3h |
| Subagentes despachados | 18 |
| Tasks concluídas | 7/7 |
| Testes adicionados | 13 |
| Bugs corrigidos | 2 (get_event_loop, resource leak) |
| Dependências removidas | 1 (Flask) |
| Linhas de código (bot.py) | 221 → ~200 |
| Commits | 8 |

---

## Lições Aprendidas

**1. Execução paralela de subagentes exige cuidado com locks do git**
Tasks 3 e 4 foram executadas em paralelo (arquivos distintos), mas o agente de Task 3 fez `git add .` em vez de `git add <arquivo>`, capturando as mudanças de Task 4 e o cache do pip num único commit. Preferir sempre `git add <arquivo específico>`.

**2. `git filter-branch` não limpou o histórico como esperado**
O commit 9755ceb ainda contém os arquivos `pip-metadata-*/` e `*.whl.metadata` (ver `git log --stat`). A operação de limpeza não foi bem-sucedida. Para limpar adequadamente seria necessário `git filter-repo` + force push.

**3. Code review em duas etapas (spec + qualidade) captura problemas diferentes**
O spec reviewer identificou que `handle_url` não delegava para `_convert_and_send` em Task 5. O quality reviewer identificou que `mock_status_message` era fixture morta. Ambos os problemas foram corrigidos antes do merge final.

**4. Subagentes com `pytest-asyncio` em modo STRICT exigem `@pytest.mark.asyncio`**
O ambiente usa `asyncio_mode = STRICT` (padrão do pytest-asyncio 1.x). Todo teste async precisa do decorator explícito — sem ele, o teste é ignorado silenciosamente.
