# Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir bugs, remover dependência desnecessária (Flask) e eliminar duplicação de código no bot Telegram.

**Architecture:** Refatoração incremental guiada por testes — cada bug é coberto por teste antes de ser corrigido. Nenhuma funcionalidade nova é adicionada.

**Tech Stack:** Python 3.10+, python-telegram-bot 20.x, pytest, pytest-asyncio, pytest-mock, docling

---

## Problemas Identificados

| # | Arquivo | Problema | Severidade |
|---|---------|----------|------------|
| 1 | `bot.py:126,169` | `asyncio.get_event_loop()` deprecated no Python 3.10+ | Bug |
| 2 | `bot.py:131` | `os.unlink(tmp_path)` não está em `try/finally` — temp file vaza em exceções | Bug |
| 3 | `keep_alive.py` | Flask como dependência só para 2 rotas simples | Desnecessário |
| 4 | `bot.py:98,151` | Lógica de conversão duplicada entre `handle_document` e `handle_url` | DRY |
| 5 | `bot.py:175-179` | Derivação do `stem` de URL com `.replace()` encadeados frágeis | Qualidade |
| 6 | `bot.py:98` | Nenhuma verificação de tamanho de arquivo | Robustez |

---

## File Structure

```
doc2markdown-bot/
├── bot.py                          MODIFY — corrigir bugs, extrair helper
├── keep_alive.py                   MODIFY — substituir Flask por http.server
├── requirements.txt                MODIFY — remover flask, adicionar dev deps
└── tests/
    ├── __init__.py                 CREATE
    ├── conftest.py                 CREATE — fixtures compartilhadas
    ├── test_bot.py                 CREATE — testes de handlers e helpers
    └── test_keep_alive.py          CREATE — testes do servidor HTTP
```

---

## Task 1: Setup de testes

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Adicionar dependências de teste ao requirements.txt**

```text
docling
python-telegram-bot==20.*
flask>=3.0.0
pytest
pytest-asyncio
pytest-mock
```

Nota: `flask` permanece aqui — será removida na Task 4 Step 4, após os testes de baseline.

- [ ] **Step 2: Criar `tests/__init__.py`**

```python
```
(arquivo vazio)

- [ ] **Step 3: Criar `tests/conftest.py` com fixtures básicas**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_chat.id = 12345
    update.message.reply_text = AsyncMock()
    update.message.document = MagicMock()
    update.message.document.file_name = "test.pdf"
    update.message.document.file_id = "file123"
    update.message.document.file_size = 1024
    return update


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.bot.get_file = AsyncMock()
    context.bot.send_document = AsyncMock()
    return context
```

- [ ] **Step 4: Verificar que pytest encontra os testes**

```bash
py -m pytest tests/ --collect-only
```
Esperado: `no tests ran` (sem erros de import)

- [ ] **Step 5: Commit**

```bash
git add tests/ requirements.txt
git commit -m "test: setup infraestrutura de testes com pytest-asyncio"
```

---

## Task 2: Corrigir `asyncio.get_event_loop()` deprecated

**Files:**
- Modify: `bot.py:126,169`
- Modify: `tests/test_bot.py`

- [ ] **Step 1: Escrever teste que falha com a implementação atual**

Criar `tests/test_bot.py`:

```python
import ast
import pathlib
import pytest

# Caminho absoluto relativo a este arquivo de teste (tests/test_bot.py → bot.py)
BOT_PATH = pathlib.Path(__file__).parent.parent / "bot.py"


def test_no_get_event_loop_in_bot():
    """bot.py não deve conter asyncio.get_event_loop() (deprecated Python 3.10+)."""
    source = BOT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "get_event_loop":
            pytest.fail(
                f"bot.py linha {node.lineno}: use asyncio.get_running_loop() "
                f"em vez de asyncio.get_event_loop()"
            )
```

- [ ] **Step 2: Rodar o teste para confirmar falha**

```bash
py -m pytest tests/test_bot.py::test_no_get_event_loop_in_bot -v
```
Esperado: `FAILED — bot.py linha 126: use asyncio.get_running_loop()`

- [ ] **Step 3: Corrigir `bot.py` — substituir as duas ocorrências**

Em `handle_document` (linha ~126):
```python
# ANTES
loop = asyncio.get_event_loop()
md_content = await loop.run_in_executor(...)

# DEPOIS
loop = asyncio.get_running_loop()
md_content = await loop.run_in_executor(...)
```

Em `handle_url` (linha ~169):
```python
# ANTES
loop = asyncio.get_event_loop()
md_content = await loop.run_in_executor(...)

# DEPOIS
loop = asyncio.get_running_loop()
md_content = await loop.run_in_executor(...)
```

- [ ] **Step 4: Rodar o teste para confirmar aprovação**

```bash
py -m pytest tests/test_bot.py::test_no_get_event_loop_in_bot -v
```
Esperado: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add bot.py tests/test_bot.py
git commit -m "fix: substituir get_event_loop() por get_running_loop() (deprecated Python 3.10+)"
```

---

## Task 3: Corrigir vazamento de temp file

**Files:**
- Modify: `bot.py:117-131`
- Modify: `tests/test_bot.py`

- [ ] **Step 1: Escrever teste que verifica cleanup em caso de exceção**

Adicionar em `tests/test_bot.py`:

```python
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from bot import handle_document


@pytest.mark.asyncio
async def test_temp_file_cleaned_up_on_converter_error(mock_update, mock_context):
    """Temp file deve ser deletado mesmo quando o converter lança exceção."""
    created_files = []

    original_named_temp = __import__('tempfile').NamedTemporaryFile

    def tracking_tempfile(**kwargs):
        f = original_named_temp(**kwargs)
        created_files.append(f.name)
        return f

    mock_tg_file = AsyncMock()
    mock_tg_file.download_to_drive = AsyncMock()
    mock_context.bot.get_file.return_value = mock_tg_file

    with patch("tempfile.NamedTemporaryFile", side_effect=tracking_tempfile), \
         patch("bot.get_converter") as mock_conv:
        mock_conv.return_value.convert.side_effect = RuntimeError("converter explodiu")
        await handle_document(mock_update, mock_context)

    for path in created_files:
        assert not os.path.exists(path), f"Temp file {path} não foi deletado após exceção"
```

- [ ] **Step 2: Rodar o teste para confirmar falha**

```bash
py -m pytest tests/test_bot.py::test_temp_file_cleaned_up_on_converter_error -v
```
Esperado: `FAILED — AssertionError: Temp file ... não foi deletado após exceção`

- [ ] **Step 3: Corrigir `handle_document` com `try/finally`**

```python
# ANTES
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    await tg_file.download_to_drive(tmp.name)
    tmp_path = tmp.name

loop = asyncio.get_running_loop()
md_content = await loop.run_in_executor(
    None, lambda: get_converter().convert(tmp_path).document.export_to_markdown()
)

os.unlink(tmp_path)

# DEPOIS
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    await tg_file.download_to_drive(tmp.name)
    tmp_path = tmp.name

try:
    loop = asyncio.get_running_loop()
    md_content = await loop.run_in_executor(
        None, lambda: get_converter().convert(tmp_path).document.export_to_markdown()
    )
finally:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
```

- [ ] **Step 4: Rodar o teste para confirmar aprovação**

```bash
py -m pytest tests/test_bot.py::test_temp_file_cleaned_up_on_converter_error -v
```
Esperado: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add bot.py tests/test_bot.py
git commit -m "fix: garantir limpeza de temp file em try/finally para evitar resource leak"
```

---

## Task 4: Substituir Flask por http.server stdlib

**Files:**
- Modify: `keep_alive.py`
- Modify: `requirements.txt` — remover `flask>=3.0.0`
- Create: `tests/test_keep_alive.py`

- [ ] **Step 1: Escrever testes para o servidor keep-alive**

Criar `tests/test_keep_alive.py`:

```python
import os
import time
import urllib.request
import pytest

TEST_PORT = 18080
BASE_URL = f"http://localhost:{TEST_PORT}"


@pytest.fixture(scope="session", autouse=True)
def keep_alive_server():
    """Sobe o servidor uma única vez para toda a sessão de testes."""
    os.environ["PORT"] = str(TEST_PORT)
    from keep_alive import start_keep_alive
    start_keep_alive()
    time.sleep(0.3)  # aguardar thread subir
    yield  # testes rodam aqui
    # servidor é daemon — encerra automaticamente com o processo


def test_health_endpoint_returns_200():
    """GET /health deve retornar 200 com body contendo 'ok'."""
    with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
        assert resp.status == 200
        assert "ok" in resp.read().decode()


def test_root_endpoint_returns_200():
    """GET / deve retornar 200."""
    with urllib.request.urlopen(f"{BASE_URL}/") as resp:
        assert resp.status == 200
```

- [ ] **Step 2: Rodar testes para confirmar aprovação com Flask (baseline)**

```bash
py -m pytest tests/test_keep_alive.py -v
```
Esperado: `PASSED` (Flask ainda presente)

- [ ] **Step 3: Reescrever `keep_alive.py` sem Flask**

```python
"""
Keep-alive HTTP server para evitar que o Render free tier durma o serviço.

Usa apenas a stdlib (http.server) — sem dependência de Flask.
"""

import json
import os
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # silencia logs de acesso
        pass

    def do_GET(self):
        if self.path == "/health":
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = b"Doc2Markdown Bot \xe2\x80\x94 online \xe2\x9c\x85"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def start_keep_alive() -> None:
    """Inicia o servidor HTTP em uma thread daemon."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), _Handler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Keep-alive server rodando na porta %d", port)
```

- [ ] **Step 4: Remover flask de `requirements.txt`**

```text
docling
python-telegram-bot==20.*
pytest
pytest-asyncio
pytest-mock
```

- [ ] **Step 5: Rodar testes novamente para confirmar aprovação sem Flask**

```bash
py -m pytest tests/test_keep_alive.py -v
```
Esperado: `PASSED`

- [ ] **Step 6: Rodar todos os testes**

```bash
py -m pytest tests/ -v
```
Esperado: todos `PASSED`

- [ ] **Step 7: Commit**

```bash
git add keep_alive.py requirements.txt tests/test_keep_alive.py
git commit -m "refactor: substituir Flask por http.server stdlib no keep_alive"
```

---

## Task 5: Extrair helper `_convert_and_send` (DRY)

**Files:**
- Modify: `bot.py`
- Modify: `tests/test_bot.py`

- [ ] **Step 1: Escrever teste para o helper isolado**

Adicionar em `tests/test_bot.py`:

```python
@pytest.mark.asyncio
async def test_convert_and_send_sends_document(mock_update, mock_context):
    """_convert_and_send deve chamar send_document com o conteúdo correto."""
    from bot import _convert_and_send

    with patch("bot.get_converter") as mock_conv:
        mock_conv.return_value.convert.return_value.document.export_to_markdown.return_value = (
            "# Hello"
        )
        await _convert_and_send(
            update=mock_update,
            context=mock_context,
            source="/tmp/fake.pdf",
            stem="fake",
            status_msg=AsyncMock(),
        )

    mock_context.bot.send_document.assert_called_once()
    call_kwargs = mock_context.bot.send_document.call_args.kwargs
    assert call_kwargs["filename"] == "fake.md"


@pytest.mark.asyncio
async def test_convert_and_send_edits_status_on_error(mock_update, mock_context):
    """_convert_and_send deve editar a mensagem de status em caso de erro."""
    from bot import _convert_and_send

    status_msg = AsyncMock()
    status_msg.edit_text = AsyncMock()

    with patch("bot.get_converter") as mock_conv:
        mock_conv.return_value.convert.side_effect = RuntimeError("falhou")
        await _convert_and_send(
            update=mock_update,
            context=mock_context,
            source="/tmp/fake.pdf",
            stem="fake",
            status_msg=status_msg,
        )

    status_msg.edit_text.assert_called_once()
    assert "Erro" in status_msg.edit_text.call_args.args[0]
```

- [ ] **Step 2: Rodar testes para confirmar falha (`_convert_and_send` não existe)**

```bash
py -m pytest tests/test_bot.py::test_convert_and_send_sends_document -v
```
Esperado: `FAILED — ImportError: cannot import name '_convert_and_send'`

- [ ] **Step 3: Extrair `_convert_and_send` em `bot.py`**

Adicionar função após `get_converter()`:

```python
async def _convert_and_send(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    source: str,
    stem: str,
    status_msg,
) -> None:
    """Converte `source` (path ou URL) para Markdown e envia ao chat."""
    try:
        loop = asyncio.get_running_loop()
        md_content = await loop.run_in_executor(
            None,
            lambda: get_converter().convert(source).document.export_to_markdown(),
        )

        md_bytes = md_content.encode("utf-8")
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=md_bytes,
            filename=f"{stem}.md",
            caption=f"✅ `{stem}.md`\n_{len(md_content):,} caracteres_",
            parse_mode=ParseMode.MARKDOWN,
        )
        await status_msg.delete()

    except Exception as e:
        logger.exception("Erro ao converter %s", source)
        await status_msg.edit_text(
            f"❌ Erro ao converter:\n`{str(e)[:300]}`",
            parse_mode=ParseMode.MARKDOWN,
        )
```

Simplificar `handle_document` para usar o helper (mantendo o `try/finally` do temp file):

```python
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return await deny(update)

    doc: Document = update.message.document
    file_name = doc.file_name or "document"
    suffix = Path(file_name).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        await update.message.reply_text(
            f"❌ Formato `{suffix}` não suportado.\n\n{SUPPORTED_LIST}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if doc.file_size and doc.file_size > 20 * 1024 * 1024:  # 20 MB
        await update.message.reply_text("❌ Arquivo muito grande. Limite: 20 MB.")
        return

    status = await update.message.reply_text("⏳ Convertendo...")
    tg_file = await context.bot.get_file(doc.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        await tg_file.download_to_drive(tmp.name)
        tmp_path = tmp.name

    try:
        await _convert_and_send(
            update=update,
            context=context,
            source=tmp_path,
            stem=Path(file_name).stem,
            status_msg=status,
        )
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

Simplificar `handle_url`:

```python
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return await deny(update)

    text = update.message.text.strip()

    if not (text.startswith("http://") or text.startswith("https://")):
        await update.message.reply_text(
            "💬 Envie um arquivo ou uma URL começando com `http://` ou `https://`.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    status = await update.message.reply_text("⏳ Convertendo URL...")
    stem = _stem_from_url(text)
    await _convert_and_send(update=update, context=context, source=text, stem=stem, status_msg=status)
```

- [ ] **Step 4: Rodar todos os testes**

```bash
py -m pytest tests/ -v
```
Esperado: todos `PASSED`

- [ ] **Step 5: Commit**

```bash
git add bot.py tests/test_bot.py
git commit -m "refactor: extrair _convert_and_send eliminando duplicação entre handlers"
```

---

## Task 6: Corrigir derivação do stem de URL

**Files:**
- Modify: `bot.py`
- Modify: `tests/test_bot.py`

- [ ] **Step 1: Escrever testes para `_stem_from_url`**

Adicionar em `tests/test_bot.py`:

```python
from bot import _stem_from_url


@pytest.mark.parametrize("url,expected", [
    ("https://example.com/report.pdf", "report"),
    ("https://example.com/page.html", "page"),
    ("https://example.com/path/to/doc.docx", "doc"),
    ("https://example.com/", "document"),
    ("https://example.com/no-extension", "no-extension"),
    ("https://example.com/file.pdf?token=abc", "file"),
    # Path sem extensão: Path.stem == Path.name, então "a"*100 → truncado em 60
    ("https://example.com/" + "a" * 100, "a" * 60),
])
def test_stem_from_url(url, expected):
    assert _stem_from_url(url) == expected
```

- [ ] **Step 2: Rodar testes para confirmar falha**

```bash
py -m pytest tests/test_bot.py::test_stem_from_url -v
```
Esperado: `FAILED — ImportError: cannot import name '_stem_from_url'`

- [ ] **Step 3: Adicionar `_stem_from_url` em `bot.py`**

Adicionar import no topo:
```python
from urllib.parse import urlparse
```

Adicionar função:
```python
def _stem_from_url(url: str) -> str:
    """Deriva um nome de arquivo stem a partir de uma URL."""
    path = urlparse(url).path.rstrip("/")
    stem = Path(path).stem if path else "document"
    return (stem or "document")[:60]
```

- [ ] **Step 4: Rodar todos os testes**

```bash
py -m pytest tests/ -v
```
Esperado: todos `PASSED`

- [ ] **Step 5: Commit**

```bash
git add bot.py tests/test_bot.py
git commit -m "refactor: substituir stem URL por _stem_from_url com urllib.parse"
```

---

## Task 7: Verificação final

- [ ] **Step 1: Rodar suite completa**

```bash
py -m pytest tests/ -v --tb=short
```
Esperado: todos `PASSED`, zero warnings

- [ ] **Step 2: Verificar que não há mais `get_event_loop` no código**

```bash
py -m pytest tests/test_bot.py::test_no_get_event_loop_in_bot -v
```
Esperado: `PASSED` (teste AST da Task 2 já cobre isso)

- [ ] **Step 3: Verificar que flask não está em requirements.txt**

```bash
py -m pytest tests/test_keep_alive.py -v
```
Esperado: `PASSED` — se os testes passam sem Flask instalado, a remoção foi bem-sucedida

- [ ] **Step 4: Push final**

```bash
git push origin master
```

---

## Resumo das mudanças

| Arquivo | Antes | Depois |
|---------|-------|--------|
| `bot.py` | 221 linhas, 2 bugs, código duplicado | ~200 linhas, limpo, testado |
| `keep_alive.py` | depende de Flask | stdlib pura |
| `requirements.txt` | 3 deps (inclui Flask) | 2 deps de produção + 3 de teste |
| `tests/` | inexistente | 4 arquivos, cobertura dos casos críticos |
