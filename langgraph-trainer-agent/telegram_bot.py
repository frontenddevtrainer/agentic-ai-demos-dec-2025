from __future__ import annotations

import asyncio
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from config import load_settings
from rag_agent import answer_question, build_graph


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("trainer-bot")


def _is_group_chat(update: Update) -> bool:
    chat = update.effective_chat
    if not chat:
        return False
    return chat.type in {"group", "supergroup"}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:


    print(update.effective_chat.id, update.message)


    # if update.message is None or update.message.from_user is None:
    #     return
    # if update.message.from_user.is_bot:
    #     return
    # if not _is_group_chat(update):
    #     return
    

    settings = context.bot_data["settings"]
    # if settings.telegram_allowed_chat_id is not None:
    #     if update.effective_chat is None:
    #         return
    #     if update.effective_chat.id != settings.telegram_allowed_chat_id:
    #         return

    text = update.message.text or ""
    if not text.strip():
        return

    graph = context.bot_data["graph"]
    answer = await asyncio.to_thread(answer_question, graph, text)
    if not answer:
        return
    
    print(answer)

    await update.message.reply_text(answer)


def main() -> None:
    load_dotenv()
    settings = load_settings()
    graph = build_graph(settings)

    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )

    application.bot_data["graph"] = graph
    application.bot_data["settings"] = settings

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("AgenticAI Trainer bot started")
    application.run_polling()


if __name__ == "__main__":
    main()