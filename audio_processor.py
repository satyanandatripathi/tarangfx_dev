"""
Advanced Audio Processor for PnProjects Audio Bot
Includes Pedalboard effects, custom EQ, 3D audio, and professional processing
"""

import os
import logging
import subprocess
import json
import asyncio
import numpy as np
import soundfile as sf
import librosa
import pyloudnorm as pyln
from typing import Dict, List, Tuple, Optional
from pedalboard import (
    Pedalboard, Reverb, Chorus, Phaser, Distortion, Compressor,
    Gain, LowpassFilter, HighpassFilter, PeakFilter, LowShelfFilter,
    HighShelfFilter, Limiter, Delay, Bitcrush
)
from pedalboard.io import AudioFile

logger = logging.getLogger(__name__)


class AdvancedAudioProcessor:
    """Professional audio processing with industry-standard tools"""

    @staticmethod
    async def get_audio_info(file_path: str) -> Dict:
        """Extract detailed audio information using FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            data = json.loads(stdout.decode())

            audio_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'audio'),
                {}
            )
            format_info = data.get('format', {})

            return {
                'codec': audio_stream.get('codec_name', 'unknown'),
                'bitrate': int(audio_stream.get('bit_rate', 0)) // 1000 if audio_stream.get('bit_rate') else 0,
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': audio_stream.get('channels', 0),
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'format': format_info.get('format_name', 'unknown')
            }
        except Exception as e:
            logger.exception("Error getting audio info")
            return {}

    @staticmethod
    async def apply_eq(
        input_file: str,
        output_file: str,
        eq_settings: List[Dict[str, float]],
        sample_rate: int = 48000
    ) -> bool:
        """
        Apply custom parametric EQ with specified frequencies and gains
        eq_settings: [{"freq": 100, "gain": 2.0}, {"freq": 1000, "gain": -1.5}, ...]
        """
        try:
            audio, sr = sf.read(input_file)
            if sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
                sr = sample_rate

            board = Pedalboard()

            for eq in eq_settings:
                freq = eq.get('freq', 1000)
                gain_db = eq.get('gain', 0)
                q = eq.get('q', 1.0)

                if 20 <= freq <= 40000 and -20 <= gain_db <= 20:
                    if freq < 200:
                        board.append(LowShelfFilter(cutoff_frequency_hz=freq, gain_db=gain_db))
                    elif freq > 8000:
                        board.append(HighShelfFilter(cutoff_frequency_hz=freq, gain_db=gain_db))
                    else:
                        board.append(PeakFilter(cutoff_frequency_hz=freq, gain_db=gain_db, q=q))

            if len(audio.shape) == 1:
                audio = audio.reshape(-1, 1)

            processed = board(audio.T, sr)

            sf.write(output_file, processed.T, sr)
            logger.info("EQ applied successfully: %d bands", len(eq_settings))
            return True

        except Exception as e:
            logger.exception("Error applying EQ")
            return False

    @staticmethod
    async def apply_pedalboard_effects(
        input_file: str,
        output_file: str,
        effects: List[str],
        sample_rate: int = 48000
    ) -> bool:
        """
        Apply Pedalboard effects
        Available effects: reverb, chorus, phaser, distortion, compressor, delay, bitcrush
        """
        try:
            audio, sr = sf.read(input_file)
            if sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
                sr = sample_rate

            board = Pedalboard()

            for effect in effects:
                effect_lower = effect.lower()

                if effect_lower == 'reverb':
                    board.append(Reverb(room_size=0.5, damping=0.5, wet_level=0.33))
                elif effect_lower == 'chorus':
                    board.append(Chorus(rate_hz=1.0, depth=0.25, centre_delay_ms=7.0, feedback=0.0, mix=0.5))
                elif effect_lower == 'phaser':
                    board.append(Phaser(rate_hz=1.0, depth=0.5, centre_frequency_hz=1300.0, feedback=0.0, mix=0.5))
                elif effect_lower == 'distortion':
                    board.append(Distortion(drive_db=25))
                elif effect_lower == 'compressor':
                    board.append(Compressor(threshold_db=-16, ratio=4, attack_ms=1.0, release_ms=100))
                elif effect_lower == 'delay':
                    board.append(Delay(delay_seconds=0.25, feedback=0.3, mix=0.5))
                elif effect_lower == 'bitcrush':
                    board.append(Bitcrush(bit_depth=8))
                elif effect_lower == 'limiter':
                    board.append(Limiter(threshold_db=-1.0, release_ms=100))

            if len(audio.shape) == 1:
                audio = audio.reshape(-1, 1)

            processed = board(audio.T, sr)

            sf.write(output_file, processed.T, sr)
            logger.info("Pedalboard effects applied: %s", ', '.join(effects))
            return True

        except Exception as e:
            logger.exception("Error applying effects")
            return False

    @staticmethod
    async def normalize_audio(
        input_file: str,
        output_file: str,
        target_lufs: float = -14.0,
        sample_rate: int = 48000
    ) -> bool:
        """Normalize audio to target LUFS using industry standard"""
        try:
            audio, sr = sf.read(input_file)
            if sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
                sr = sample_rate

            meter = pyln.Meter(sr)

            if len(audio.shape) == 1:
                loudness = meter.integrated_loudness(audio)
            else:
                loudness = meter.integrated_loudness(audio)

            normalized_audio = pyln.normalize.loudness(audio, loudness, target_lufs)

            sf.write(output_file, normalized_audio, sr)
            logger.info("Audio normalized to %.1f LUFS", target_lufs)
            return True

        except Exception as e:
            logger.exception("Error normalizing audio")
            return False

    @staticmethod
    async def create_3d_audio(
        input_file: str,
        output_file: str,
        azimuth: float = 0,
        elevation: float = 0,
        sample_rate: int = 48000
    ) -> bool:
        """
        Create 3D binaural audio using HRTF simulation
        azimuth: horizontal angle (-180 to 180)
        elevation: vertical angle (-90 to 90)
        """
        try:
            audio, sr = sf.read(input_file)
            if sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
                sr = sample_rate

            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            delay_samples = int(0.0006 * sr * np.sin(np.radians(azimuth)))
            itd = np.abs(delay_samples)

            ild_db = 10 * np.cos(np.radians(azimuth))
            ild_linear = 10 ** (ild_db / 20)

            left = np.copy(audio)
            right = np.copy(audio)

            if azimuth > 0:
                left = np.pad(left, (itd, 0), mode='constant')[:len(audio)]
                right = right * ild_linear
                left = left / ild_linear
            else:
                right = np.pad(right, (itd, 0), mode='constant')[:len(audio)]
                left = left * ild_linear
                right = right / ild_linear

            board = Pedalboard([
                Reverb(room_size=0.3, damping=0.5, wet_level=0.1)
            ])

            stereo = np.stack([left, right], axis=0)
            processed = board(stereo, sr)

            sf.write(output_file, processed.T, sr)
            logger.info("3D audio created with azimuth=%.1f, elevation=%.1f", azimuth, elevation)
            return True

        except Exception as e:
            logger.exception("Error creating 3D audio")
            return False

    @staticmethod
    async def convert_audio(
        input_file: str,
        output_file: str,
        output_format: str = 'mp3',
        bitrate: str = '320k',
        sample_rate: int = 48000,
        channels: int = 2,
        bass_boost: int = 0,
        normalize: bool = False,
        fade_in: float = 0,
        fade_out: float = 0,
        speed: float = 1.0
    ) -> bool:
        """Enhanced audio conversion with FFmpeg"""
        try:
            cmd = ['ffmpeg', '-i', input_file, '-y']

            filters = []

            if bass_boost > 0:
                filters.append(f'equalizer=f=100:width_type=h:width=200:g={bass_boost}')

            if normalize:
                filters.append('loudnorm=I=-16:TP=-1.5:LRA=11')

            if fade_in > 0:
                filters.append(f'afade=t=in:st=0:d={fade_in}')

            if fade_out > 0:
                info = await AdvancedAudioProcessor.get_audio_info(input_file)
                duration = info.get('duration', 0)
                if duration > 0:
                    filters.append(f'afade=t=out:st={duration - fade_out}:d={fade_out}')

            if speed != 1.0:
                filters.append(f'atempo={speed}')

            if filters:
                cmd.extend(['-af', ','.join(filters)])

            codec_map = {
                'mp3': 'libmp3lame',
                'm4a': 'aac',
                'aac': 'aac',
                'ogg': 'libvorbis',
                'opus': 'libopus',
                'flac': 'flac',
                'wav': 'pcm_s16le',
                'alac': 'alac',
                'wma': 'wmav2',
                'ac3': 'ac3',
                'webm': 'libopus'
            }

            codec = codec_map.get(output_format.lower(), 'copy')
            if codec != 'copy':
                cmd.extend(['-c:a', codec])

            lossless_formats = ['flac', 'wav', 'alac', 'ape', 'wv', 'tta', 'aiff']
            if output_format.lower() not in lossless_formats:
                cmd.extend(['-b:a', bitrate])

            cmd.extend(['-ar', str(sample_rate)])
            cmd.extend(['-ac', str(channels)])

            if output_format.lower() == 'mp3':
                cmd.extend(['-q:a', '0'])
            elif output_format.lower() in ['aac', 'm4a']:
                cmd.extend(['-movflags', '+faststart'])
            elif output_format.lower() == 'flac':
                cmd.extend(['-compression_level', '8'])

            cmd.append(output_file)

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.exception("Error converting audio")
            return False

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
