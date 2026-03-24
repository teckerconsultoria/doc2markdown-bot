import os
import logging
import tempfile
import asyncio
from pathlib import Path
from urllib.parse import urlparse

from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

from docling.document_converter import DocumentConverter

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
ALLOWED_CHAT_IDS = {
    int(cid.strip())
    for cid in os.environ.get("ALLOWED_CHAT_IDS", "").split(",")
    if cid.strip()
}

# ── Supported extensions ──────────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".md", ".html", ".xhtml", ".csv",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp",
    ".adoc", ".asciidoc", ".tex",
}

SUPPORTED_LIST = (
    "*Documentos:* PDF, DOCX, XLSX, PPTX, HTML, CSV, MD, AsciiDoc, LaTeX\n"
    "*Imagens:* PNG, JPG, TIFF, BMP, WEBP"
)

# ── Docling converter (singleton) ─────────────────────────────────────────────
_converter: DocumentConverter | None = None

def get_converter() -> DocumentConverter:
    global _converter
    if _converter is None:
        logger.info("Inicializando DocumentConverter (pode demorar na primeira vez)...")
        _converter = DocumentConverter()
        logger.info("DocumentConverter pronto.")
    return _converter


# ── Auth guard ────────────────────────────────────────────────────────────────
def is_allowed(update: Update) -> bool:
    if not ALLOWED_CHAT_IDS:
        return True  # sem whitelist configurada → aberto
    return update.effective_chat.id in ALLOWED_CHAT_IDS


async def deny(update: Update) -> None:
    await update.message.reply_text("⛔ Acesso não autorizado.")


# ── Conversion helper ─────────────────────────────────────────────────────────
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


def _stem_from_url(url: str) -> str:
    """Deriva um nome de arquivo stem a partir de uma URL."""
    path = urlparse(url).path.rstrip("/")
    stem = Path(path).stem if path else "document"
    return (stem or "document")[:60]


# ── Handlers ──────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return await deny(update)

    await update.message.reply_text(
        "👋 *Doc2Markdown Bot*\n\n"
        "Envie um arquivo ou cole uma URL e eu converto para Markdown.\n\n"
        f"{SUPPORTED_LIST}\n\n"
        "Use /help para mais informações.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return await deny(update)

    await update.message.reply_text(
        "📖 *Como usar:*\n\n"
        "• *Arquivo:* envie diretamente no chat\n"
        "• *URL:* cole o link como mensagem de texto\n\n"
        f"*Formatos suportados:*\n{SUPPORTED_LIST}\n\n"
        "O bot retorna um arquivo `.md` pronto para download.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file uploads."""
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
        tmp_path = tmp.name

    try:
        await tg_file.download_to_drive(tmp_path)
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


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle URL messages."""
    if not is_allowed(update):
        return await deny(update)

    text = update.message.text.strip()

    # Basic URL check
    if not (text.startswith("http://") or text.startswith("https://")):
        await update.message.reply_text(
            "💬 Envie um arquivo ou uma URL começando com `http://` ou `https://`.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    status = await update.message.reply_text("⏳ Convertendo URL...")
    stem = _stem_from_url(text)
    await _convert_and_send(update=update, context=context, source=text, stem=stem, status_msg=status)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    from keep_alive import start_keep_alive
    start_keep_alive()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    logger.info("Bot iniciado. Aguardando mensagens...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
