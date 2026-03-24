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


@pytest.fixture
def mock_status_message():
    """Mock para mensagem de status durante conversão."""
    msg = MagicMock()
    msg.edit_text = AsyncMock()
    msg.delete = AsyncMock()
    return msg
