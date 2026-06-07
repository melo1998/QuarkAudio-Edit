"""
TTS 语音合成模块 - 通过 HTTP API 调用 CosyVoice2 合成佩戴者和非佩戴者语音
（不依赖 dashscope SDK，直接使用 requests 发送 HTTP 请求）
"""
import os
import json
import time
import struct
import wave
import requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path


# CosyVoice2 可用的中文音色
COSYVOICE2_VOICES = {
    "male": [
        "longxiaochun",      # 龙小淳 - 男声
        "longyuan",          # 龙元 - 男声
        "longhua",           # 龙华 - 男声
        "longjielidou",      # 龙杰力豆 - 男声
        "longcheng",         # 龙诚 - 男声（新闻播报风）
    ],
    "female": [
        "longxiaoxia",       # 龙小夏 - 女声
        "longlaotie",        # 龙老铁 - 女声
        "longshu",           # 龙书 - 女声（温柔）
        "longshuo",          # 龙硕 - 女声
        "longjing",          # 龙晶 - 女声
    ]
}

# DashScope TTS HTTP API 端点
TTS_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2audio/text-synthesis"


def synthesize_segment_cosyvoice2(
    text: str,
    voice: str = "longxiaochun",
    sample_rate: int = 16000,
    output_path: Optional[str] = None,
    api_key: Optional[str] = None,
) -> bytes:
    """
    使用 CosyVoice2 HTTP API 合成单段语音。

    Args:
        text: 要合成的文本
        voice: 音色名称
        sample_rate: 采样率
        output_path: 可选的输出文件路径
        api_key: DashScope API Key

    Returns:
        PCM 音频数据 (16bit, mono)
    """
    if api_key is None:
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        return _generate_silence_pcm(len(text) * 0.25, sample_rate)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "disable",
    }

    payload = {
        "model": "cosyvoice-v2",
        "input": {
            "text": text,
        },
        "parameters": {
            "voice": voice,
            "format": "wav",
            "sample_rate": sample_rate,
        }
    }

    try:
        response = requests.post(TTS_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "audio" in content_type or "octet-stream" in content_type:
                # 返回的是 WAV 文件，提取 PCM 数据
                wav_bytes = response.content
                if output_path:
                    with open(output_path, "wb") as f:
                        f.write(wav_bytes)
                pcm_data = _extract_pcm_from_wav_bytes(wav_bytes)
                return pcm_data
            else:
                # 可能返回了 JSON 错误
                error_info = response.json() if response.text else {}
                print(f"    [TTS API Error] {error_info}")
                return _generate_silence_pcm(len(text) * 0.25, sample_rate)
        else:
            print(f"    [TTS HTTP {response.status_code}] {response.text[:200]}")
            return _generate_silence_pcm(len(text) * 0.25, sample_rate)

    except Exception as exc:
        print(f"    [TTS Exception] {exc}")
        return _generate_silence_pcm(len(text) * 0.25, sample_rate)


def _extract_pcm_from_wav_bytes(wav_bytes: bytes) -> bytes:
    """从 WAV 文件字节中提取 PCM 数据"""
    import io
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        return wf.readframes(wf.getnframes())


def synthesize_dialogue_segments(
    segments: List[Dict],
    spk01_voice: str = "longxiaochun",
    spk02_voice: str = "longxiaoxia",
    sample_rate: int = 16000,
    cache_dir: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[int, bytes]:
    """
    批量合成对话中所有语音段。

    Args:
        segments: 对话段落列表 [{speaker, start, end, text}, ...]
        spk01_voice: 佩戴者音色
        spk02_voice: 非佩戴者音色
        sample_rate: 采样率
        cache_dir: 缓存目录

    Returns:
        {segment_index: pcm_bytes} 映射
    """
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)

    voice_map = {
        "spk01": spk01_voice,
        "spk02": spk02_voice
    }

    synthesized = {}
    total_segments = len([s for s in segments if s["text"].strip()])

    for idx, seg in enumerate(segments):
        text = seg["text"].strip()
        if not text:
            continue

        speaker = seg["speaker"]
        voice = voice_map.get(speaker, spk01_voice)

        # 检查缓存
        cache_path = None
        if cache_dir:
            cache_path = os.path.join(cache_dir, f"seg_{idx:04d}_{speaker}.wav")
            if os.path.exists(cache_path):
                pcm_data = _load_wav_as_pcm(cache_path)
                synthesized[idx] = pcm_data
                print(f"  [Cache] Segment {idx}/{total_segments}: {text[:20]}...")
                continue

        print(f"  [TTS] Segment {idx}/{total_segments} ({speaker}): {text[:30]}...")

        try:
            pcm_data = synthesize_segment_cosyvoice2(
                text=text,
                voice=voice,
                sample_rate=sample_rate,
                api_key=api_key,
            )
            synthesized[idx] = pcm_data

            if cache_path:
                _save_pcm_as_wav(pcm_data, cache_path, sample_rate)

            # 避免 API 限流
            time.sleep(0.3)

        except Exception as exc:
            print(f"  [ERROR] Segment {idx} TTS failed: {exc}")
            # 用静音替代
            expected_duration = seg["end"] - seg["start"]
            synthesized[idx] = _generate_silence_pcm(expected_duration, sample_rate)

    return synthesized


def _generate_silence_pcm(duration_seconds: float, sample_rate: int = 16000) -> bytes:
    """生成指定时长的静音 PCM 数据"""
    num_samples = int(duration_seconds * sample_rate)
    return struct.pack(f"<{num_samples}h", *([0] * num_samples))


def _save_pcm_as_wav(pcm_data: bytes, filepath: str, sample_rate: int = 16000):
    """将 PCM 数据保存为 WAV 文件"""
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)


def _load_wav_as_pcm(filepath: str) -> bytes:
    """从 WAV 文件加载 PCM 数据"""
    with wave.open(filepath, "rb") as wf:
        return wf.readframes(wf.getnframes())


def get_pcm_duration(pcm_data: bytes, sample_rate: int = 16000) -> float:
    """计算 PCM 数据的时长（秒）"""
    num_samples = len(pcm_data) // 2  # 16bit = 2 bytes per sample
    return num_samples / sample_rate


if __name__ == "__main__":
    # 测试静音生成
    silence = _generate_silence_pcm(1.0, 16000)
    print(f"1s silence: {len(silence)} bytes, "
          f"duration: {get_pcm_duration(silence):.2f}s")

    # 测试 WAV 保存
    test_output = os.path.join(
        os.path.dirname(__file__), "output", "test_silence.wav"
    )
    os.makedirs(os.path.dirname(test_output), exist_ok=True)
    _save_pcm_as_wav(silence, test_output, 16000)
    print(f"Saved test WAV: {test_output}")
