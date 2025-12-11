"""
Download Manager for PnProjects Audio Bot
Robust file downloading with retry logic and progress tracking
"""

import os
import logging
import asyncio
from typing import Optional
from datetime import datetime
from pyrogram import Client
from pyrogram.types import Message
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from pyrogram.errors import FloodWait

logger = logging.getLogger(__name__)


class DownloadManager:
    """Manages file downloads with retry and progress tracking"""

    @staticmethod
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, FloodWait))
    )
    async def download_with_retry(
        client: Client,
        message: Message,
        file_name: str,
        progress_callback=None
    ) -> Optional[str]:
        """
        Download file with automatic retry on failure
        Returns path to downloaded file or None
        """
        try:
            file_path = await client.download_media(
                message,
                file_name=file_name,
                progress=progress_callback
            )

            if file_path and os.path.exists(file_path):
                logger.info("Downloaded file: %s (size: %d bytes)", file_path, os.path.getsize(file_path))
                return file_path
            else:
                logger.error("Download completed but file not found: %s", file_name)
                return None

        except FloodWait as e:
            logger.warning("FloodWait: sleeping for %d seconds", e.value)
            await asyncio.sleep(e.value)
            raise

        except Exception as e:
            logger.exception("Download error")
            raise

    @staticmethod
    async def download_with_progress(
        client: Client,
        message: Message,
        status_message: Message,
        user_id: int,
        timestamp: int
    ) -> Optional[str]:
        """
        Download file with progress updates to user
        Returns downloaded file path or None
        """

        last_update_time = 0

        async def progress(current, total):
            nonlocal last_update_time
            current_time = asyncio.get_event_loop().time()

            if current_time - last_update_time < 2:
                return

            last_update_time = current_time

            percentage = current * 100 / total
            progress_bar = DownloadManager._create_progress_bar(percentage)

            try:
                await status_message.edit_text(
                    f"Downloading file...\n\n"
                    f"{progress_bar}\n"
                    f"Progress: {percentage:.1f}%\n"
                    f"Size: {DownloadManager._format_bytes(current)} / "
                    f"{DownloadManager._format_bytes(total)}"
                )
            except Exception:
                pass

        try:
            if message.audio:
                file = message.audio
                file_ext = 'mp3'
            elif message.voice:
                file = message.voice
                file_ext = 'ogg'
            elif message.document:
                file = message.document
                file_name = getattr(file, 'file_name', 'audio')
                file_ext = file_name.split('.')[-1] if '.' in file_name else 'audio'
            else:
                logger.error("No audio file found in message")
                return None

            download_path = os.path.join(
                'downloads',
                f"{user_id}_{timestamp}_input.{file_ext}"
            )

            file_path = await DownloadManager.download_with_retry(
                client,
                message,
                download_path,
                progress
            )

            if file_path:
                await status_message.edit_text("Download complete! Analyzing audio...")

            return file_path

        except Exception as e:
            logger.exception("Error in download with progress")
            await status_message.edit_text(
                f"Download failed: {str(e)}\n\n"
                "Please try again or send a smaller file."
            )
            return None

    @staticmethod
    def _create_progress_bar(percentage: float, length: int = 20) -> str:
        """Create visual progress bar"""
        filled = int(length * percentage / 100)
        empty = length - filled
        return f"[{'=' * filled}{' ' * empty}]"

    @staticmethod
    def _format_bytes(bytes_size: float) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
