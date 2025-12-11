"""
Interactive Button Layouts for PnProjects Audio Bot
Professional and feature-rich inline keyboard interfaces
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config


class Buttons:
    """Centralized button layout management"""

    @staticmethod
    def start_menu():
        """Main start menu buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Start Converting", callback_data="how_to_use"),
                InlineKeyboardButton("Help", callback_data="help_main")
            ],
            [
                InlineKeyboardButton("Features", callback_data="features"),
                InlineKeyboardButton("Formats", callback_data="supported_formats")
            ],
            [
                InlineKeyboardButton("Developer", url="https://t.me/PnProjects")
            ]
        ])

    @staticmethod
    def help_menu():
        """Modular help menu with feature categories"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Commands", callback_data="help_commands"),
                InlineKeyboardButton("Features", callback_data="help_features")
            ],
            [
                InlineKeyboardButton("Settings", callback_data="help_settings"),
                InlineKeyboardButton("Formats", callback_data="help_formats")
            ],
            [
                InlineKeyboardButton("EQ Guide", callback_data="help_eq"),
                InlineKeyboardButton("Effects", callback_data="help_effects")
            ],
            [
                InlineKeyboardButton("3D Audio", callback_data="help_3d"),
                InlineKeyboardButton("Examples", callback_data="help_examples")
            ],
            [
                InlineKeyboardButton("FAQ", callback_data="help_faq")
            ],
            [
                InlineKeyboardButton("Main Menu", callback_data="main_menu")
            ]
        ])

    @staticmethod
    def back_to_help():
        """Back to help button"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Back to Help", callback_data="help_main")]
        ])

    @staticmethod
    def format_selection():
        """Format selection menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("MP3", callback_data="format_mp3"),
                InlineKeyboardButton("M4A", callback_data="format_m4a"),
                InlineKeyboardButton("AAC", callback_data="format_aac")
            ],
            [
                InlineKeyboardButton("FLAC", callback_data="format_flac"),
                InlineKeyboardButton("WAV", callback_data="format_wav"),
                InlineKeyboardButton("ALAC", callback_data="format_alac")
            ],
            [
                InlineKeyboardButton("OGG", callback_data="format_ogg"),
                InlineKeyboardButton("OPUS", callback_data="format_opus"),
                InlineKeyboardButton("WMA", callback_data="format_wma")
            ],
            [
                InlineKeyboardButton("More Formats...", callback_data="format_more")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def more_formats():
        """Additional format selection"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("APE", callback_data="format_ape"),
                InlineKeyboardButton("WavPack", callback_data="format_wv"),
                InlineKeyboardButton("TTA", callback_data="format_tta")
            ],
            [
                InlineKeyboardButton("AIFF", callback_data="format_aiff"),
                InlineKeyboardButton("WebM", callback_data="format_webm"),
                InlineKeyboardButton("AC3", callback_data="format_ac3")
            ],
            [
                InlineKeyboardButton("Back", callback_data="process_convert_0")
            ]
        ])

    @staticmethod
    def bitrate_selection():
        """Bitrate selection menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("128k", callback_data="bitrate_128k"),
                InlineKeyboardButton("192k", callback_data="bitrate_192k"),
                InlineKeyboardButton("256k", callback_data="bitrate_256k")
            ],
            [
                InlineKeyboardButton("320k (Best)", callback_data="bitrate_320k"),
                InlineKeyboardButton("500k", callback_data="bitrate_500k")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def sample_rate_selection():
        """Sample rate selection menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("22.05 kHz", callback_data="sample_22050"),
                InlineKeyboardButton("44.1 kHz (CD)", callback_data="sample_44100")
            ],
            [
                InlineKeyboardButton("48 kHz (Pro)", callback_data="sample_48000"),
                InlineKeyboardButton("96 kHz (Hi-Res)", callback_data="sample_96000")
            ],
            [
                InlineKeyboardButton("192 kHz (Studio)", callback_data="sample_192000")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def channel_selection():
        """Audio channel selection menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Mono (1)", callback_data="channels_1"),
                InlineKeyboardButton("Stereo (2)", callback_data="channels_2")
            ],
            [
                InlineKeyboardButton("5.1 Surround", callback_data="channels_6"),
                InlineKeyboardButton("7.1 Surround", callback_data="channels_8")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def bass_boost_selection():
        """Bass boost level selection"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("+1 dB", callback_data="bass_1"),
                InlineKeyboardButton("+2 dB", callback_data="bass_2"),
                InlineKeyboardButton("+3 dB", callback_data="bass_3")
            ],
            [
                InlineKeyboardButton("+4 dB", callback_data="bass_4"),
                InlineKeyboardButton("+5 dB (Max)", callback_data="bass_5")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def effects_menu():
        """Pedalboard effects menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Reverb", callback_data="effect_reverb"),
                InlineKeyboardButton("Chorus", callback_data="effect_chorus")
            ],
            [
                InlineKeyboardButton("Phaser", callback_data="effect_phaser"),
                InlineKeyboardButton("Compressor", callback_data="effect_compressor")
            ],
            [
                InlineKeyboardButton("Delay", callback_data="effect_delay"),
                InlineKeyboardButton("Distortion", callback_data="effect_distortion")
            ],
            [
                InlineKeyboardButton("Limiter", callback_data="effect_limiter"),
                InlineKeyboardButton("Bitcrush", callback_data="effect_bitcrush")
            ],
            [
                InlineKeyboardButton("Done", callback_data="confirm_process")
            ]
        ])

    @staticmethod
    def audio_3d_menu():
        """3D audio configuration menu"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Front Center", callback_data="3d_0_0"),
                InlineKeyboardButton("Left", callback_data="3d_-90_0")
            ],
            [
                InlineKeyboardButton("Right", callback_data="3d_90_0"),
                InlineKeyboardButton("Behind", callback_data="3d_180_0")
            ],
            [
                InlineKeyboardButton("Custom", callback_data="3d_custom")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def processing_options(user_id: int):
        """Processing options for uploaded audio"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Convert Format", callback_data=f"process_convert_{user_id}"),
                InlineKeyboardButton("Change Bitrate", callback_data=f"process_bitrate_{user_id}")
            ],
            [
                InlineKeyboardButton("Apply Effects", callback_data=f"process_effects_{user_id}"),
                InlineKeyboardButton("3D Audio", callback_data=f"process_3d_{user_id}")
            ],
            [
                InlineKeyboardButton("Normalize", callback_data=f"process_normalize_{user_id}"),
                InlineKeyboardButton("Bass Boost", callback_data=f"process_bass_{user_id}")
            ],
            [
                InlineKeyboardButton("Use EQ Command", callback_data="show_eq_help"),
                InlineKeyboardButton("File Info", callback_data=f"process_info_{user_id}")
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def confirm_processing():
        """Confirmation buttons for processing"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Confirm & Process", callback_data="confirm_process"),
                InlineKeyboardButton("Cancel", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def continue_or_cancel():
        """Continue editing or cancel buttons"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Continue Editing", callback_data="continue_editing"),
                InlineKeyboardButton("Done", callback_data="cancel_operation")
            ]
        ])

    @staticmethod
    def cancel_button():
        """Simple cancel button"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Cancel", callback_data="cancel_operation")]
        ])

    @staticmethod
    def back_to_main():
        """Back to main menu button"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
        ])


class HelpTexts:
    """Help text content for different sections"""

    COMMANDS = """
**Available Commands**

**Basic Commands:**
/start - Start the bot
/help - Display help menu
/cancel - Cancel operation and clear session

**Advanced Commands:**
/eq - Apply custom parametric EQ

**EQ Command Usage:**
`/eq --100hz +3db --1khz -2db --5khz +1.5db`

Reply to an audio file with this command to apply custom equalization.

**How to Use:**
1. Send audio file
2. Reply to file with /eq command
3. Specify frequencies and gains
4. Process and receive result

All commands support inline buttons for easy navigation.
"""

    FEATURES = """
**Bot Features**

**Format Conversion:**
- 20+ audio formats supported
- Lossy and lossless formats
- High-quality codec support

**Audio Processing:**
- Custom parametric EQ (20Hz - 40kHz)
- Professional effects via Pedalboard
- Loudness normalization (LUFS)
- Bass boost and enhancement
- Fade in/out effects
- Speed adjustment

**Effects Library:**
- Reverb (room simulation)
- Chorus (doubling effect)
- Phaser (sweeping effect)
- Compressor (dynamics control)
- Delay (echo effect)
- Distortion (overdrive)
- Limiter (peak control)
- Bitcrush (lo-fi effect)

**3D Audio:**
- Binaural HRTF processing
- Spatial audio positioning
- Headphone-optimized output

**Advanced:**
- Persistent sessions (5 min)
- Multiple operations per file
- Batch-style workflow
- Industry-standard processing
"""

    SETTINGS = """
**Audio Settings Guide**

**Bitrate:**
- 128k: Good for speech
- 192k: Standard quality
- 256k: High quality
- 320k: Premium quality
- 500k+: Audiophile grade

**Sample Rate:**
- 22.05 kHz: Voice only
- 44.1 kHz: CD quality
- 48 kHz: Professional
- 96 kHz: Hi-Resolution
- 192 kHz: Studio master

**Channels:**
- Mono (1): Single channel
- Stereo (2): Standard music
- 5.1: Surround sound
- 7.1: Full surround

**EQ Settings:**
- Frequency: 20Hz - 40kHz
- Gain: -20dB to +20dB
- Q factor: 0.5 - 10.0

**Effects:**
Each effect has pro-grade defaults optimized for music production.
"""

    FORMATS = """
**Supported Audio Formats**

**Lossy (Compressed):**
- MP3 - Universal format
- M4A/AAC - High efficiency
- OGG Vorbis - Open source
- OPUS - Best quality/size
- WMA - Windows format
- AC3 - Dolby Digital
- AMR - Mobile format

**Lossless (Uncompressed):**
- FLAC - Popular lossless
- WAV - Standard PCM
- ALAC - Apple Lossless
- APE - Monkey's Audio
- WavPack - Hybrid
- TTA - True Audio
- AIFF - Professional

**Other:**
- WebM Audio
- DTS Surround
- And more...
"""

    EQ_GUIDE = """
**Parametric EQ Guide**

**Command Format:**
`/eq --[frequency]hz [gain]db`

**Examples:**

**Bass Boost:**
`/eq --60hz +4db --100hz +3db`

**Vocal Clarity:**
`/eq --200hz -1db --3khz +2db --5khz +1db`

**Brightness:**
`/eq --8khz +2db --12khz +1.5db`

**Full Mix:**
`/eq --40hz +2db --200hz -1db --1khz +1db --5khz +2db --10khz +1db`

**Tips:**
- Use 'k' suffix for kHz: --1khz, --5khz
- Boost/cut in small increments (1-3dB)
- Test on reference tracks
- Cut before boost for clarity

**Frequency Ranges:**
- Sub-bass: 20-60Hz
- Bass: 60-250Hz
- Low-mids: 250Hz-500Hz
- Mids: 500Hz-2kHz
- High-mids: 2-6kHz
- Presence: 6-8kHz
- Brilliance: 8-20kHz
"""

    EFFECTS_GUIDE = """
**Effects Guide**

**Reverb:**
Adds room ambience and space
Best for: Vocals, instruments
Settings: Room size 0.5, Wet 33%

**Chorus:**
Thickens sound with doubling
Best for: Guitars, synths
Settings: Rate 1Hz, Depth 0.25

**Phaser:**
Sweeping frequency effect
Best for: Creative coloring
Settings: Rate 1Hz, Depth 0.5

**Compressor:**
Controls dynamics
Best for: All tracks
Settings: Threshold -16dB, Ratio 4:1

**Delay:**
Echo/repeat effect
Best for: Vocals, leads
Settings: 250ms, Feedback 0.3

**Distortion:**
Adds harmonic saturation
Best for: Guitars, creative FX
Settings: Drive 25dB

**Limiter:**
Prevents clipping
Best for: Mastering
Settings: Threshold -1dB

**Bitcrush:**
Lo-fi digital degradation
Best for: Creative effects
Settings: 8-bit depth

**Tips:**
- Apply effects in order
- Less is often more
- Use A/B comparison
- Save presets mentally
"""

    AUDIO_3D_GUIDE = """
**3D Audio Processing**

**What is Binaural Audio?**
3D audio uses HRTF (Head-Related Transfer Function) to create spatial positioning for headphone listening.

**Available Positions:**
- Front Center (0°)
- Left (-90°)
- Right (+90°)
- Behind (180°)
- Custom angles

**How It Works:**
1. Mono/stereo input
2. HRTF processing
3. ITD (time delay)
4. ILD (level difference)
5. Binaural stereo output

**Best For:**
- Podcasts
- ASMR content
- Spatial music
- Gaming audio
- Virtual reality

**Tips:**
- Use headphones
- Source matters
- Mono inputs work best
- Experiment with angles
"""

    EXAMPLES = """
**Usage Examples**

**Example 1: Format Conversion**
1. Send audio file
2. Click "Convert Format"
3. Select MP3
4. Choose 320k bitrate
5. Process

**Example 2: Custom EQ**
1. Send audio file
2. Reply: `/eq --60hz +3db --3khz +2db`
3. Wait for processing
4. Receive equalized file

**Example 3: Apply Effects**
1. Send audio file
2. Click "Apply Effects"
3. Select: Reverb, Compressor
4. Confirm processing
5. Get processed file

**Example 4: 3D Audio**
1. Send audio file
2. Click "3D Audio"
3. Select "Left" position
4. Process for binaural output

**Example 5: Multi-Step**
1. Send file
2. Apply EQ
3. Continue editing
4. Add effects
5. Final conversion
"""

    FAQ = """
**Frequently Asked Questions**

**Q: Maximum file size?**
A: 2GB per file

**Q: Processing time?**
A: 10-60 seconds depending on size and operations

**Q: Are files stored?**
A: No, auto-deleted after processing

**Q: Session timeout?**
A: 5 minutes of inactivity

**Q: Can I apply multiple effects?**
A: Yes, select multiple from effects menu

**Q: Best format for quality?**
A: FLAC for lossless, MP3 320k for lossy

**Q: How does EQ work?**
A: Parametric EQ with custom frequency/gain control

**Q: Is 3D audio real?**
A: Yes, uses HRTF for binaural processing

**Q: Can I undo operations?**
A: Original file persists during session

**Q: Database required?**
A: No, works with in-memory fallback

**Q: Concurrent users?**
A: Designed for millions with Supabase
"""


