from __future__ import annotations

import asyncio
import logging
import time

import discord

from agent.controller import AgentController
from config.settings import load_settings
from security.guards import SecurityError, ensure_allowed_user


LOGGER = logging.getLogger(__name__)


def run_bot() -> None:
    settings = load_settings()
    controller = AgentController(settings)
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        LOGGER.info("Logged in as %s", client.user)

    @client.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        LOGGER.info(
            "Discord message received: author_id=%s channel_id=%s content_length=%s",
            message.author.id,
            message.channel.id,
            len(message.content or ""),
        )
        try:
            ensure_allowed_user(message.author.id, settings.discord_allowed_user_id)
        except SecurityError:
            LOGGER.warning(
                "Discord message rejected: unauthorized author_id=%s",
                message.author.id,
            )
            return

        if message.attachments:
            LOGGER.info("Discord request rejected: attachments are disabled")
            await message.channel.send(
                "Discord file transfer is disabled. Use the configured OneDrive folder."
            )
            return

        if not message.content.strip():
            LOGGER.warning(
                "Discord message had no readable text. Check Message Content Intent."
            )
            await message.channel.send(
                "I received the message but could not read its text. "
                "Check the Discord Message Content Intent setting."
            )
            return

        started = time.monotonic()
        acknowledgement = await message.channel.send(
            "Command received. Processing..."
        )
        LOGGER.info("Discord command processing started")
        async with message.channel.typing():
            try:
                response = await asyncio.to_thread(controller.handle, message.content)
            except FileExistsError as exc:
                response = f"OCR stopped. Overwrite protection: {exc}"
            except Exception as exc:
                LOGGER.exception("Request failed")
                response = f"Request failed safely: {type(exc).__name__}: {exc}"
        elapsed = time.monotonic() - started
        LOGGER.info(
            "Discord command processing finished: elapsed_seconds=%.2f",
            elapsed,
        )
        try:
            await acknowledgement.delete()
        except discord.HTTPException:
            LOGGER.warning("Could not remove processing acknowledgement")
        for chunk in _discord_chunks(response):
            await message.channel.send(chunk)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    client.run(settings.discord_bot_token, log_handler=None)


def _discord_chunks(text: str, limit: int = 1900) -> list[str]:
    chunks = []
    remaining = text
    while len(remaining) > limit:
        split = remaining.rfind("\n", 0, limit)
        split = split if split > 0 else limit
        chunks.append(remaining[:split])
        remaining = remaining[split:].lstrip("\n")
    if remaining:
        chunks.append(remaining)
    return chunks or [""]
