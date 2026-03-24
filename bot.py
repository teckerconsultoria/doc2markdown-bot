import os
import logging
import tempfile
import asyncio
from pathlib import Path

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
            f"❌ Formato `{suffix}` não suportado.\n\n"
            f"{SUPPORTED_LIST}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    status = await update.message.reply_text("⏳ Convertendo...")

    try:
        # Download to temp file
        tg_file = await context.bot.get_file(doc.file_id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        # Convert in thread (CPU-bound)
        loop = asyncio.get_running_loop()
        md_content = await loop.run_in_executor(
            None, lambda: get_converter().convert(tmp_path).document.export_to_markdown()
        )

        os.unlink(tmp_path)

        # Send .md file
        stem = Path(file_name).stem
        md_bytes = md_content.encode("utf-8")

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=md_bytes,
            filename=f"{stem}.md",
            caption=f"✅ `{file_name}` → `{stem}.md`\n_{len(md_content):,} caracteres_",
            parse_mode=ParseMode.MARKDOWN,
        )
        await status.delete()

    except Exception as e:
        logger.exception("Erro ao converter arquivo %s", file_name)
        await status.edit_text(f"❌ Erro ao converter `{file_name}`:\n`{str(e)[:300]}`", parse_mode=ParseMode.MARKDOWN)


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

    status = await update.message.reply_text(f"⏳ Convertendo URL...")

    try:
        loop = asyncio.get_running_loop()
        md_content = await loop.run_in_executor(
            None, lambda: get_converter().convert(text).document.export_to_markdown()
        )

        # Derive filename from URL
        url_path = text.rstrip("/").split("/")[-1].split("?")[0]
        stem = (
            url_path.replace(".pdf", "").replace(".html", "").replace(".htm", "")
            or "document"
        )
        stem = stem[:60]  # truncate

        md_bytes = md_content.encode("utf-8")

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=md_bytes,
            filename=f"{stem}.md",
            caption=f"✅ URL convertida → `{stem}.md`\n_{len(md_content):,} caracteres_",
            parse_mode=ParseMode.MARKDOWN,
        )
        await status.delete()

    except Exception as e:
        logger.exception("Erro ao converter URL %s", text)
        await status.edit_text(f"❌ Erro ao converter URL:\n`{str(e)[:300]}`", parse_mode=ParseMode.MARKDOWN)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    # Start keep-alive server in background thread
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
