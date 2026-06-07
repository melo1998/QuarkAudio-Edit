"""
音频合并模块 - 将分段 TTS 音频按时间戳混合为4通道 WAV
"""
import struct
import wave
import numpy as np
import os
from typing import Dict, List, Optional


def mix_dialogue_audio(
    segments: List[Dict],
    synthesized_pcm: Dict[int, bytes],
    total_duration: float,
    sample_rate: int = 16000,
    num_channels: int = 4
) -> np.ndarray:
    """
    将合成的语音段按时间戳混合到多通道音频中。

    智能眼镜4通道麦克风阵列布局：
    - Channel 1 (mic1): 右镜腿后方
    - Channel 2 (mic2): 右镜腿前方
    - Channel 3 (mic3): 左镜腿前方
    - Channel 4 (mic4): 左镜腿后方

    佩戴者(spk01)的声音主要来自近场，4个麦克风都能清晰采集到，
    但各通道会有微小的时间延迟和幅度差异。
    非佩戴者(spk02)的声音来自对面，前方麦克风(ch2,ch3)信号较强。

    Args:
        segments: 对话段落列表
        synthesized_pcm: {segment_index: pcm_bytes} 映射
        total_duration: 总时长（秒）
        sample_rate: 采样率
        num_channels: 通道数

    Returns:
        np.ndarray shape=(num_samples, num_channels), dtype=int16
    """
    total_samples = int(total_duration * sample_rate)
    mixed_audio = np.zeros((total_samples, num_channels), dtype=np.float64)

    for idx, seg in enumerate(segments):
        if idx not in synthesized_pcm:
            continue

        pcm_data = synthesized_pcm[idx]
        if not pcm_data:
            continue

        # 将 PCM bytes 转为 numpy array
        mono_signal = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float64)

        start_sample = int(seg["start"] * sample_rate)
        segment_samples = len(mono_signal)

        # 确保不超出总时长
        available_space = total_samples - start_sample
        if available_space <= 0:
            continue
        actual_samples = min(segment_samples, available_space)
        mono_signal = mono_signal[:actual_samples]

        speaker = seg["speaker"]

        if speaker == "spk01":
            # 佩戴者：近场，所有通道都有较强信号
            # 各通道增益和延迟模拟真实麦克风阵列
            channel_gains = [0.90, 0.95, 0.95, 0.90]  # 前方稍强
            channel_delays = [2, 0, 0, 2]  # 前方微延迟较小（samples）
        else:
            # 非佩戴者：远场，前方通道信号更强
            channel_gains = [0.50, 0.80, 0.80, 0.50]  # 前方通道更强
            channel_delays = [5, 2, 2, 5]  # 前后方延迟差异更大

        for ch_idx in range(num_channels):
            gain = channel_gains[ch_idx]
            delay = channel_delays[ch_idx]

            # 应用增益
            channel_signal = mono_signal * gain

            # 应用延迟
            target_start = start_sample + delay
            target_end = target_start + len(channel_signal)

            if target_start >= total_samples:
                continue
            if target_end > total_samples:
                channel_signal = channel_signal[:total_samples - target_start]
                target_end = total_samples

            # 混合到对应通道（累加，允许重叠）
            mixed_audio[target_start:target_end, ch_idx] += channel_signal

    # 归一化防止溢出
    max_val = np.max(np.abs(mixed_audio))
    if max_val > 32767:
        mixed_audio = mixed_audio * (32767 / max_val) * 0.95

    return mixed_audio.astype(np.int16)


def add_background_noise(
    audio: np.ndarray,
    noise_level: float = 0.005,
    sample_rate: int = 16000
) -> np.ndarray:
    """添加轻微的背景噪声使音频更自然"""
    noise = np.random.normal(0, noise_level * 32767, audio.shape)
    noisy_audio = audio.astype(np.float64) + noise

    max_val = np.max(np.abs(noisy_audio))
    if max_val > 32767:
        noisy_audio = noisy_audio * (32767 / max_val) * 0.95

    return noisy_audio.astype(np.int16)


def save_multichannel_wav(
    audio: np.ndarray,
    filepath: str,
    sample_rate: int = 16000
):
    """
    保存多通道 WAV 文件。

    Args:
        audio: np.ndarray shape=(num_samples, num_channels), dtype=int16
        filepath: 输出文件路径
        sample_rate: 采样率
    """
    num_samples, num_channels = audio.shape

    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)  # 16bit
        wf.setframerate(sample_rate)

        # interleave channels: [ch1_s1, ch2_s1, ..., ch1_s2, ch2_s2, ...]
        interleaved = audio.flatten(order="C")  # row-major = per-sample interleave
        wf.writeframes(interleaved.tobytes())

    print(f"  Saved {num_channels}ch WAV: {filepath} "
          f"({num_samples / sample_rate:.2f}s, {os.path.getsize(filepath) / 1024:.0f}KB)")


def save_mono_wav(
    audio: np.ndarray,
    filepath: str,
    sample_rate: int = 16000,
    channel_index: int = 0
):
    """从多通道音频提取单通道保存"""
    if audio.ndim == 2:
        mono = audio[:, channel_index]
    else:
        mono = audio

    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(mono.astype(np.int16).tobytes())


if __name__ == "__main__":
    # 简单测试：生成一个空的4通道音频
    test_duration = 10.0
    sample_rate = 16000
    num_samples = int(test_duration * sample_rate)
    test_audio = np.zeros((num_samples, 4), dtype=np.int16)
    test_audio = add_background_noise(test_audio, noise_level=0.002)

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_4ch.wav")
    save_multichannel_wav(test_audio, output_path, sample_rate)
    print("Test 4ch WAV generated successfully")
