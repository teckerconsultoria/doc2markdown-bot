import ast
import os
import pathlib
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.mark.asyncio
async def test_temp_file_cleaned_up_on_converter_error():
    """Temp file deve ser deletado mesmo quando o converter lança exceção."""
    import sys
    from unittest.mock import MagicMock

    # Mock docling before importing bot to avoid torch DLL issues
    sys.modules['docling'] = MagicMock()
    sys.modules['docling.document_converter'] = MagicMock()

    # Mock environment variables before importing bot
    with patch.dict(os.environ, {"BOT_TOKEN": "fake_token"}):
        from bot import handle_document
        from telegram import Update, Message, Document, Chat, User
        from telegram.ext import ContextTypes

        created_files = []

        original_named_temp = __import__('tempfile').NamedTemporaryFile

        def tracking_tempfile(**kwargs):
            f = original_named_temp(**kwargs)
            created_files.append(f.name)
            return f

        # Mock update, context, etc.
        mock_user = MagicMock(spec=User)
        mock_user.id = 12345

        mock_chat = MagicMock(spec=Chat)
        mock_chat.id = 67890

        mock_doc = MagicMock(spec=Document)
        mock_doc.file_id = "test_file_id"
        mock_doc.file_name = "test.pdf"
        mock_doc.file_size = 1024  # abaixo do limite de 20 MB

        mock_message = MagicMock(spec=Message)
        mock_message.document = mock_doc
        mock_message.from_user = mock_user
        mock_message.reply_text = AsyncMock()

        mock_update = MagicMock(spec=Update)
        mock_update.message = mock_message
        mock_update.effective_chat = mock_chat

        mock_tg_file = AsyncMock()
        mock_tg_file.download_to_drive = AsyncMock()

        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.bot.get_file = AsyncMock(return_value=mock_tg_file)

        with patch("tempfile.NamedTemporaryFile", side_effect=tracking_tempfile), \
             patch("bot.get_converter") as mock_conv, \
             patch("bot.is_allowed", return_value=True):
            mock_conv.return_value.convert.side_effect = RuntimeError("converter explodiu")
            await handle_document(mock_update, mock_context)

        # Verificar que todos os temp files criados foram deletados
        for path in created_files:
            assert not os.path.exists(path), f"Temp file {path} não foi deletado após exceção"


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
    import sys
    from unittest.mock import MagicMock

    # Mock docling before importing bot
    sys.modules['docling'] = MagicMock()
    sys.modules['docling.document_converter'] = MagicMock()

    with patch.dict(os.environ, {"BOT_TOKEN": "fake_token"}):
        from bot import _stem_from_url
        assert _stem_from_url(url) == expected
