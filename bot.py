"""
Main Bot Logic for PnProjects Audio Bot
Advanced audio processing with professional features and scalability
"""

import os
import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Optional

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import MessageNotModified

from client import PnProjects
from config import Config
from buttons import Buttons, HelpTexts
from forcesub import ForceSubscription
from database import DatabaseManager, InMemorySessionManager
from audio_processor import AdvancedAudioProcessor
from download_manager import DownloadManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = PnProjects()

db = DatabaseManager()
fallback_sessions = InMemorySessionManager()


async def get_user_session(user_id: int) -> Dict:
    """Get or create user session from database or memory"""
    if db.is_connected:
        session = await db.get_user_session(user_id)
        if session:
            return session

        new_session = await db.create_user_session(user_id)
        return new_session if new_session else _create_default_session(user_id)
    else:
        session = fallback_sessions.get_session(user_id)
        if session:
            return session
        return fallback_sessions.create_session(user_id)


async def update_user_session(user_id: int, updates: Dict) -> bool:
    """Update user session"""
    if db.is_connected:
        session = await db.get_user_session(user_id)
        if session:
            return await db.update_user_session(session['id'], updates)
        return False
    else:
        return fallback_sessions.update_session(user_id, updates)


async def delete_user_session(user_id: int):
    """Delete user session and cleanup files"""
    if db.is_connected:
        session = await db.get_user_session(user_id)
        if session:
            file_path = session.get('file_path')
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            await db.delete_user_session(session['id'])
    else:
        session = fallback_sessions.get_session(user_id)
        if session:
            file_path = session.get('file_path')
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            fallback_sessions.delete_session(user_id)


def _create_default_session(user_id: int) -> Dict:
    """Create default session structure"""
    return {
        'user_id': user_id,
        'file_path': None,
        'original_filename': None,
        'file_info': {},
        'settings': {
            'format': 'mp3',
            'bitrate': '320k',
            'sample_rate': 48000,
            'channels': 2,
            'bass_boost': 0,
            'normalize': False,
            'fade_in': 0,
            'fade_out': 0,
            'speed': 1.0,
            'eq': [],
            'effects': []
        }
    }


async def cleanup_expired_sessions():
    """Background task to cleanup expired sessions"""
    while True:
        try:
            await asyncio.sleep(Config.CLEANUP_INTERVAL_SECONDS)

            if db.is_connected:
                await db.cleanup_expired_sessions()
            else:
                fallback_sessions.cleanup_expired()

        except Exception as e:
            logger.exception("Error in cleanup task")


@bot.on_message(filters.command("start"))
async def start_command(client: PnProjects, message: Message):
    """Handle /start command"""
    if not await ForceSubscription.handle_force_sub(client, message):
        return

    welcome_text = f"""
**Welcome to {Config.BOT_NAME}**

Your professional audio processing companion with industry-grade features.

**What I Can Do:**
- Convert between 20+ audio formats
- Apply custom EQ with frequency control
- Professional audio effects via Pedalboard
- 3D binaural audio processing
- Normalize, compress, and enhance
- Fast async processing
- Persistent sessions

**Quick Start:**
Send any audio file and explore the features.

**Pro Tip:** Use /eq command for custom equalization.
"""
    await message.reply_text(
        welcome_text,
        reply_markup=Buttons.start_menu()
    )


@bot.on_message(filters.command("help"))
async def help_command(client: PnProjects, message: Message):
    """Handle /help command"""
    if not await ForceSubscription.handle_force_sub(client, message):
        return

    await message.reply_text(
        "**Help Center**\n\nChoose a topic to learn more:",
        reply_markup=Buttons.help_menu()
    )


@bot.on_message(filters.command("cancel"))
async def cancel_command(client: PnProjects, message: Message):
    """Handle /cancel command"""
    user_id = message.from_user.id
    await delete_user_session(user_id)
    await message.reply_text(
        "Operation cancelled. All data cleared.\n\n"
        "Send a new audio file to start again."
    )


@bot.on_message(filters.command("eq"))
async def eq_command(client: PnProjects, message: Message):
    """
    Handle custom EQ command
    Format: /eq --100hz +3db --1khz -2db --5khz +1.5db
    """
    if not await ForceSubscription.handle_force_sub(client, message):
        return

    user_id = message.from_user.id
    session = await get_user_session(user_id)

    if not session.get('file_path'):
        await message.reply_text(
            "Please send an audio file first, then reply to it with /eq command."
        )
        return

    try:
        eq_pattern = r'--(\d+\.?\d*)([kmKM]?)hz\s+([+-]\d+\.?\d*)db'
        matches = re.findall(eq_pattern, message.text, re.IGNORECASE)

        if not matches:
            await message.reply_text(
                "**EQ Command Format:**\n\n"
                "`/eq --20hz +2db --100hz +3db --1khz -1db --5khz +2db`\n\n"
                "**Examples:**\n"
                "- `--20hz +3db` - Boost bass at 20Hz by 3dB\n"
                "- `--1khz -2db` - Cut mids at 1kHz by 2dB\n"
                "- `--10khz +1.5db` - Boost highs at 10kHz by 1.5dB\n\n"
                "**Frequency range:** 20Hz to 40kHz\n"
                "**Gain range:** -20dB to +20dB"
            )
            return

        eq_settings = []
        for freq_val, freq_unit, gain_val in matches:
            freq = float(freq_val)

            if freq_unit.lower() == 'k':
                freq *= 1000

            gain = float(gain_val)

            if not (20 <= freq <= 40000):
                await message.reply_text(
                    f"Frequency {freq}Hz is out of range (20Hz - 40kHz)"
                )
                return

            if not (-20 <= gain <= 20):
                await message.reply_text(
                    f"Gain {gain}dB is out of range (-20dB to +20dB)"
                )
                return

            eq_settings.append({'freq': freq, 'gain': gain, 'q': 1.0})

        if not eq_settings:
            await message.reply_text("No valid EQ settings found.")
            return

        settings = session.get('settings', {})
        settings['eq'] = eq_settings

        await update_user_session(user_id, {'settings': settings})

        eq_summary = '\n'.join([
            f"- {eq['freq']}Hz: {eq['gain']:+.1f}dB"
            for eq in eq_settings
        ])

        await message.reply_text(
            f"**EQ Settings Applied:**\n\n{eq_summary}\n\n"
            "Ready to process?",
            reply_markup=Buttons.confirm_processing()
        )

    except Exception as e:
        logger.exception("Error parsing EQ command")
        await message.reply_text(f"Error parsing EQ command: {str(e)}")


@bot.on_message(filters.audio | filters.document | filters.voice)
async def handle_audio(client: PnProjects, message: Message):
    """Handle audio file uploads with robust download"""
    if not await ForceSubscription.handle_force_sub(client, message):
        return

    user_id = message.from_user.id
    status_msg = await message.reply_text("Preparing to download audio file...")

    try:
        if message.audio:
            file = message.audio
        elif message.voice:
            file = message.voice
        elif message.document:
            file = message.document
        else:
            await status_msg.edit_text("No audio file found.")
            return

        if file.file_size > Config.MAX_FILE_SIZE:
            await status_msg.edit_text(
                f"File too large. Maximum size: "
                f"{AdvancedAudioProcessor.format_size(Config.MAX_FILE_SIZE)}"
            )
            return

        timestamp = int(datetime.now().timestamp())

        file_path = await DownloadManager.download_with_progress(
            client, message, status_msg, user_id, timestamp
        )

        if not file_path:
            await status_msg.edit_text("Download failed. Please try again.")
            return

        audio_info = await AdvancedAudioProcessor.get_audio_info(file_path)

        original_filename = getattr(file, 'file_name', f'audio_{timestamp}')

        session = await get_user_session(user_id)
        await update_user_session(user_id, {
            'file_path': file_path,
            'original_filename': original_filename,
            'file_info': audio_info
        })

        info_text = f"""
**Audio File Received**

**File Information:**
Format: `{audio_info.get('format', 'unknown').upper()}`
Codec: `{audio_info.get('codec', 'unknown').upper()}`
Bitrate: `{audio_info.get('bitrate', 0)} kbps`
Sample Rate: `{audio_info.get('sample_rate', 0)} Hz`
Channels: `{audio_info.get('channels', 0)}`
Duration: `{AdvancedAudioProcessor.format_duration(audio_info.get('duration', 0))}`
Size: `{AdvancedAudioProcessor.format_size(audio_info.get('size', 0))}`

**What would you like to do?**
"""

        await status_msg.edit_text(
            info_text,
            reply_markup=Buttons.processing_options(user_id)
        )

    except Exception as e:
        logger.exception("Error handling audio")
        await status_msg.edit_text(f"Error: {str(e)}")


@bot.on_callback_query()
async def handle_callbacks(client: PnProjects, callback_query: CallbackQuery):
    """Handle all callback queries with proper error handling"""
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data not in ["check_sub"] and not data.startswith("help_"):
        if not await ForceSubscription.handle_force_sub(client, callback_query.message):
            await callback_query.answer("Please join the channel first.", show_alert=True)
            return

    try:
        if data == "check_sub":
            await ForceSubscription.handle_check_subscription(client, callback_query)
            return

        elif data == "main_menu":
            await callback_query.message.edit_text(
                "**Main Menu**\n\nWhat would you like to do?",
                reply_markup=Buttons.start_menu()
            )

        elif data.startswith("help_"):
            await handle_help_callbacks(callback_query, data)

        elif data.startswith("process_"):
            await handle_process_callbacks(callback_query, data, user_id)

        elif data.startswith("format_"):
            await handle_format_selection(callback_query, data, user_id)

        elif data.startswith("bitrate_"):
            await handle_bitrate_selection(callback_query, data, user_id)

        elif data.startswith("sample_"):
            await handle_sample_rate_selection(callback_query, data, user_id)

        elif data.startswith("channels_"):
            await handle_channel_selection(callback_query, data, user_id)

        elif data.startswith("bass_"):
            await handle_bass_boost_selection(callback_query, data, user_id)

        elif data.startswith("effect_"):
            await handle_effect_selection(callback_query, data, user_id)

        elif data == "confirm_process":
            await process_audio(client, callback_query, user_id)
            return

        elif data == "continue_editing":
            session = await get_user_session(user_id)
            await callback_query.message.edit_text(
                "**Continue Editing**\n\nWhat would you like to do next?",
                reply_markup=Buttons.processing_options(user_id)
            )

        elif data == "cancel_operation":
            await delete_user_session(user_id)
            await callback_query.message.edit_text(
                "Operation cancelled.\n\nSend a new audio file to start again."
            )

        await callback_query.answer()

    except MessageNotModified:
        await callback_query.answer()
    except Exception as e:
        logger.exception("Error in callback")
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)


async def handle_help_callbacks(callback_query: CallbackQuery, data: str):
    """Handle help menu callbacks"""
    help_map = {
        "help_main": ("**Help Center**\n\nChoose a topic:", Buttons.help_menu()),
        "help_commands": (HelpTexts.COMMANDS, Buttons.back_to_help()),
        "help_features": (HelpTexts.FEATURES, Buttons.back_to_help()),
        "help_settings": (HelpTexts.SETTINGS, Buttons.back_to_help()),
        "help_formats": (HelpTexts.FORMATS, Buttons.back_to_help()),
        "help_examples": (HelpTexts.EXAMPLES, Buttons.back_to_help()),
        "help_faq": (HelpTexts.FAQ, Buttons.back_to_help()),
    }

    if data in help_map:
        text, markup = help_map[data]
        await callback_query.message.edit_text(text, reply_markup=markup)


async def handle_process_callbacks(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle processing option callbacks"""
    if data.startswith("process_convert_"):
        await callback_query.message.edit_text(
            "**Format Conversion**\n\nSelect output format:",
            reply_markup=Buttons.format_selection()
        )
    elif data.startswith("process_bitrate_"):
        await callback_query.message.edit_text(
            "**Bitrate Selection**\n\nChoose bitrate quality:",
            reply_markup=Buttons.bitrate_selection()
        )
    elif data.startswith("process_effects_"):
        await callback_query.message.edit_text(
            "**Audio Effects**\n\nChoose effects to apply:",
            reply_markup=Buttons.effects_menu()
        )
    elif data.startswith("process_3d_"):
        await callback_query.message.edit_text(
            "**3D Audio**\n\nCreate binaural 3D audio:",
            reply_markup=Buttons.audio_3d_menu()
        )


async def handle_format_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle format selection"""
    if data == "format_more":
        await callback_query.message.edit_text(
            "**More Formats**\n\nSelect format:",
            reply_markup=Buttons.more_formats()
        )
        return

    format_code = data.replace("format_", "")
    await update_user_session(user_id, {
        'settings': {'format': format_code}
    })

    await callback_query.answer(f"Format set to {format_code.upper()}")
    await callback_query.message.edit_text(
        f"**Format Selected: {Config.get_format_display_name(format_code)}**\n\n"
        "Choose bitrate:",
        reply_markup=Buttons.bitrate_selection()
    )


async def handle_bitrate_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle bitrate selection"""
    bitrate = data.replace("bitrate_", "")
    session = await get_user_session(user_id)
    settings = session.get('settings', {})
    settings['bitrate'] = bitrate

    await update_user_session(user_id, {'settings': settings})
    await callback_query.answer(f"Bitrate set to {bitrate}")

    await callback_query.message.edit_text(
        f"**Settings Configured**\n\n"
        f"Format: `{settings.get('format', 'mp3').upper()}`\n"
        f"Bitrate: `{bitrate}`\n\n"
        "Ready to process?",
        reply_markup=Buttons.confirm_processing()
    )


async def handle_sample_rate_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle sample rate selection"""
    sample = data.replace("sample_", "")
    session = await get_user_session(user_id)
    settings = session.get('settings', {})
    settings['sample_rate'] = int(sample)

    await update_user_session(user_id, {'settings': settings})
    await callback_query.answer(f"Sample rate set to {sample} Hz")


async def handle_channel_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle channel selection"""
    channels = int(data.replace("channels_", ""))
    session = await get_user_session(user_id)
    settings = session.get('settings', {})
    settings['channels'] = channels

    await update_user_session(user_id, {'settings': settings})
    await callback_query.answer(f"Channels set to {channels}")


async def handle_bass_boost_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle bass boost selection"""
    boost = int(data.replace("bass_", ""))
    session = await get_user_session(user_id)
    settings = session.get('settings', {})
    settings['bass_boost'] = boost

    await update_user_session(user_id, {'settings': settings})
    await callback_query.answer(f"Bass boost set to +{boost} dB")


async def handle_effect_selection(callback_query: CallbackQuery, data: str, user_id: int):
    """Handle effect selection"""
    effect = data.replace("effect_", "")
    session = await get_user_session(user_id)
    settings = session.get('settings', {})

    effects = settings.get('effects', [])
    if effect not in effects:
        effects.append(effect)
        settings['effects'] = effects
        await update_user_session(user_id, {'settings': settings})
        await callback_query.answer(f"{effect.title()} added")
    else:
        await callback_query.answer(f"{effect.title()} already added")


async def process_audio(client: PnProjects, callback_query: CallbackQuery, user_id: int):
    """Process audio with configured settings"""
    session = await get_user_session(user_id)
    input_file = session.get('file_path')

    if not input_file or not os.path.exists(input_file):
        await callback_query.message.edit_text(
            "File not found. Please send your audio file again."
        )
        await delete_user_session(user_id)
        return

    settings = session.get('settings', {})
    timestamp = int(datetime.now().timestamp())
    output_format = settings.get('format', 'mp3')

    try:
        await callback_query.message.edit_text("Processing audio... Please wait.")

        temp_files = []

        current_file = input_file

        if settings.get('eq'):
            eq_file = f"downloads/{user_id}_{timestamp}_eq.wav"
            success = await AdvancedAudioProcessor.apply_eq(
                current_file, eq_file, settings['eq']
            )
            if success:
                current_file = eq_file
                temp_files.append(eq_file)
            else:
                await callback_query.message.edit_text("EQ processing failed.")
                return

        if settings.get('effects'):
            effects_file = f"downloads/{user_id}_{timestamp}_effects.wav"
            success = await AdvancedAudioProcessor.apply_pedalboard_effects(
                current_file, effects_file, settings['effects']
            )
            if success:
                current_file = effects_file
                temp_files.append(effects_file)

        if settings.get('normalize'):
            norm_file = f"downloads/{user_id}_{timestamp}_norm.wav"
            success = await AdvancedAudioProcessor.normalize_audio(
                current_file, norm_file
            )
            if success:
                current_file = norm_file
                temp_files.append(norm_file)

        output_file = f"downloads/{user_id}_{timestamp}_output.{output_format}"

        success = await AdvancedAudioProcessor.convert_audio(
            input_file=current_file,
            output_file=output_file,
            output_format=output_format,
            bitrate=settings.get('bitrate', '320k'),
            sample_rate=settings.get('sample_rate', 48000),
            channels=settings.get('channels', 2),
            bass_boost=settings.get('bass_boost', 0),
            normalize=False,
            fade_in=settings.get('fade_in', 0),
            fade_out=settings.get('fade_out', 0),
            speed=settings.get('speed', 1.0)
        )

        if not success or not os.path.exists(output_file):
            await callback_query.message.edit_text("Processing failed. Try different settings.")
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
            return

        await callback_query.message.edit_text("Uploading processed audio...")

        file_size = os.path.getsize(output_file)
        caption = f"""
**Processing Complete**

**Settings Used:**
Format: `{output_format.upper()}`
Bitrate: `{settings.get('bitrate', '320k')}`
Sample Rate: `{settings.get('sample_rate', 48000)} Hz`
Size: `{AdvancedAudioProcessor.format_size(file_size)}`
"""

        if settings.get('eq'):
            caption += f"\nEQ Bands: `{len(settings['eq'])}`"
        if settings.get('effects'):
            caption += f"\nEffects: `{', '.join(settings['effects'])}`"

        await client.send_audio(
            chat_id=callback_query.message.chat.id,
            audio=output_file,
            caption=caption
        )

        if os.path.exists(output_file):
            os.remove(output_file)
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

        await callback_query.message.edit_text(
            "**Processing Complete**\n\n"
            "Your file has been sent above.\n\n"
            "Want to do more with this file?",
            reply_markup=Buttons.continue_or_cancel()
        )

    except Exception as e:
        logger.exception("Error processing audio")
        await callback_query.message.edit_text(f"Error: {str(e)}")


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Starting %s...", Config.BOT_NAME)
    logger.info("=" * 50)

    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_expired_sessions())

    bot.run()
