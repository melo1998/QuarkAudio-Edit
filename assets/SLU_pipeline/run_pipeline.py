"""
SmartGlasses 数据制作 Pipeline 主脚本

完整流程：
1. 生成对话内容（qwen3-max）
2. 合成 TTS 语音（CosyVoice2）
3. 按时间戳混合为4通道音频
4. 生成 TextGrid 标注
5. 生成 QA 多选题（qwen3-max）
6. 更新 data.jsonl 索引

用法：
    # 完整流程（需要 DASHSCOPE_API_KEY）
    python run_pipeline.py --mode full --num_samples 1

    # 仅生成对话和QA（不合成语音，用静音替代）
    python run_pipeline.py --mode text_only --num_samples 1

    # 基于现有 TextGrid 重新生成 QA
    python run_pipeline.py --mode qa_only --textgrid_path path/to/file.TextGrid

    # 指定场景
    python run_pipeline.py --mode full --scenario "两个朋友在讨论养猫的利弊"
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

# 添加当前目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textgrid_utils import dialogue_to_textgrid, save_textgrid, parse_textgrid
from dialogue_generator import (
    create_dialogue_client,
    generate_dialogue_content,
    extract_dialogue_from_textgrid,
    DIALOGUE_SCENARIOS,
)
from tts_synthesizer import (
    synthesize_dialogue_segments,
    get_pcm_duration,
    COSYVOICE2_VOICES,
)
from audio_mixer import (
    mix_dialogue_audio,
    add_background_noise,
    save_multichannel_wav,
    save_mono_wav,
)
from qa_generator import generate_qa_from_dialogue, save_qa_json


# ============ 项目路径配置 ============
PROJECT_ROOT = Path(r"D:\AliBaBa\Project\03_ai_glasses\SmartGlasses-Track1")
TRAIN_OUTPUT_DIR = PROJECT_ROOT / "Track1" / "Train" / "Synthetic"
DEV_OUTPUT_DIR = PROJECT_ROOT / "Track1" / "Dev" / "Synthetic"
DATA_JSONL_PATH = PROJECT_ROOT / "Track1" / "data.jsonl"


def get_next_chat_id(output_dir: Path, prefix: str = "synth") -> str:
    """获取下一个可用的 chat ID"""
    existing_ids = []
    audio_dir = output_dir / "audio"
    if audio_dir.exists():
        for f in audio_dir.glob("*.wav"):
            name = f.stem
            if name.startswith(prefix):
                try:
                    num = int(name.split("_")[1])
                    existing_ids.append(num)
                except (IndexError, ValueError):
                    pass

    next_num = max(existing_ids, default=-1) + 1
    return f"{prefix}_{next_num:04d}"


def setup_output_dirs(output_dir: Path):
    """创建输出目录结构"""
    (output_dir / "audio").mkdir(parents=True, exist_ok=True)
    (output_dir / "audio_mono").mkdir(parents=True, exist_ok=True)
    (output_dir / "textgrid").mkdir(parents=True, exist_ok=True)
    (output_dir / "QA").mkdir(parents=True, exist_ok=True)
    (output_dir / "cache").mkdir(parents=True, exist_ok=True)


def run_full_pipeline(
    chat_id: str,
    output_dir: Path,
    scenario: str = None,
    target_duration: int = 300,
    spk01_voice: str = "longxiaochun",
    spk02_voice: str = "longxiaoxia",
    num_questions: int = 12,
    skip_tts: bool = False,
    api_key: str = None,
):
    """
    执行完整的数据生成 pipeline。

    Args:
        chat_id: 对话ID（如 synth_0001）
        output_dir: 输出根目录
        scenario: 对话场景描述
        target_duration: 目标时长（秒）
        spk01_voice: 佩戴者音色
        spk02_voice: 非佩戴者音色
        num_questions: QA题目数量
        skip_tts: 是否跳过TTS（用静音替代）
        api_key: DashScope API Key
    """
    print(f"\n{'='*60}")
    print(f"  Pipeline Start: {chat_id}")
    print(f"{'='*60}")

    setup_output_dirs(output_dir)
    start_time = time.time()

    # ── Step 1: 生成对话内容 ──
    print("\n[Step 1/5] 生成对话内容...")
    client = create_dialogue_client(api_key=api_key)

    dialogue_data = generate_dialogue_content(
        client=client,
        scenario=scenario,
        target_duration_seconds=target_duration,
    )

    # 保存原始对话数据
    dialogue_json_path = output_dir / "cache" / f"{chat_id}_dialogue.json"
    with open(dialogue_json_path, "w", encoding="utf-8") as f:
        json.dump(dialogue_data, f, ensure_ascii=False, indent=2)

    num_segments = len(dialogue_data["segments"])
    actual_duration = dialogue_data["total_duration"]
    print(f"  ✓ 生成 {num_segments} 段对话, 时长 {actual_duration:.1f}s")
    print(f"  场景: {dialogue_data.get('scenario', 'N/A')}")

    # ── Step 2: TTS 语音合成 ──
    print(f"\n[Step 2/5] TTS 语音合成 ({'跳过，使用静音' if skip_tts else 'CosyVoice2'})...")

    if skip_tts:
        # 使用静音替代
        from tts_synthesizer import _generate_silence_pcm
        synthesized_pcm = {}
        for idx, seg in enumerate(dialogue_data["segments"]):
            if seg["text"].strip():
                duration = seg["end"] - seg["start"]
                synthesized_pcm[idx] = _generate_silence_pcm(duration, 16000)
        print(f"  ✓ 生成 {len(synthesized_pcm)} 段静音音频")
    else:
        cache_dir = str(output_dir / "cache" / chat_id)
        synthesized_pcm = synthesize_dialogue_segments(
            segments=dialogue_data["segments"],
            spk01_voice=spk01_voice,
            spk02_voice=spk02_voice,
            sample_rate=16000,
            cache_dir=cache_dir,
        )
        print(f"  ✓ 合成 {len(synthesized_pcm)} 段语音")

    # ── Step 3: 音频混合 ──
    print("\n[Step 3/5] 混合多通道音频...")

    # 根据实际 TTS 时长调整 segment 结束时间
    if not skip_tts:
        for idx in synthesized_pcm:
            actual_seg_duration = get_pcm_duration(synthesized_pcm[idx], 16000)
            seg = dialogue_data["segments"][idx]
            expected_duration = seg["end"] - seg["start"]
            if abs(actual_seg_duration - expected_duration) > 0.5:
                seg["end"] = round(seg["start"] + actual_seg_duration, 2)

        # 重新计算总时长
        max_end = max(seg["end"] for seg in dialogue_data["segments"])
        actual_duration = max(actual_duration, max_end + 0.5)
        dialogue_data["total_duration"] = actual_duration

    mixed_audio = mix_dialogue_audio(
        segments=dialogue_data["segments"],
        synthesized_pcm=synthesized_pcm,
        total_duration=actual_duration,
        sample_rate=16000,
        num_channels=4,
    )

    # 添加背景噪声
    mixed_audio = add_background_noise(mixed_audio, noise_level=0.003)

    # 保存4通道 WAV
    audio_path = output_dir / "audio" / f"{chat_id}.wav"
    save_multichannel_wav(mixed_audio, str(audio_path), 16000)

    # 保存单通道 WAV（取 channel 2，前方右侧麦克风信号最佳）
    mono_path = output_dir / "audio_mono" / f"{chat_id}.wav"
    save_mono_wav(mixed_audio, str(mono_path), 16000, channel_index=1)

    print(f"  ✓ 4ch WAV: {audio_path.name} ({actual_duration:.1f}s)")

    # ── Step 4: 生成 TextGrid ──
    print("\n[Step 4/5] 生成 TextGrid 标注...")

    textgrid = dialogue_to_textgrid(
        dialogue_segments=dialogue_data["segments"],
        total_duration=actual_duration,
    )
    textgrid_path = output_dir / "textgrid" / f"{chat_id}.TextGrid"
    save_textgrid(textgrid, str(textgrid_path))
    print(f"  ✓ TextGrid: {textgrid_path.name}")

    # ── Step 5: 生成 QA ──
    print("\n[Step 5/5] 生成 QA 多选题...")

    qa_data = generate_qa_from_dialogue(
        client=client,
        dialogue_data=dialogue_data,
        num_questions=num_questions,
    )
    qa_path = output_dir / "QA" / f"{chat_id}.json"
    save_qa_json(qa_data, str(qa_path))
    print(f"  ✓ QA: {qa_path.name} ({len(qa_data['questions'])} questions)")

    # ── 更新 data.jsonl ──
    relative_audio = f"Track1/Dev/Synthetic/audio/{chat_id}.wav"
    relative_textgrid = f"Track1/Dev/Synthetic/textgrid/{chat_id}.TextGrid"
    metadata = {
        "id": chat_id,
        "split": "Dev",
        "type": "chat",
        "main_speaker": dialogue_data.get("main_speaker", "spk01"),
        "duration": f"{actual_duration:.2f}",
        "mc_audio": relative_audio,
        "textgrid": relative_textgrid,
        "synthetic": True,
    }

    with open(DATA_JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
    print(f"  ✓ 更新 data.jsonl")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"  Pipeline Complete: {chat_id}")
    print(f"  耗时: {elapsed:.1f}s")
    print(f"  输出目录: {output_dir}")
    print(f"{'='*60}\n")

    return {
        "chat_id": chat_id,
        "dialogue_data": dialogue_data,
        "qa_data": qa_data,
        "audio_path": str(audio_path),
        "textgrid_path": str(textgrid_path),
        "qa_path": str(qa_path),
        "metadata": metadata,
    }


def run_qa_only(
    textgrid_path: str,
    output_dir: Path,
    chat_id: str = None,
    num_questions: int = 12,
    api_key: str = None,
):
    """仅基于现有 TextGrid 生成 QA"""
    print(f"\n[QA Only Mode] TextGrid: {textgrid_path}")

    if chat_id is None:
        chat_id = Path(textgrid_path).stem

    dialogue_data = extract_dialogue_from_textgrid(textgrid_path)
    print(f"  提取 {len(dialogue_data['segments'])} 段对话, "
          f"时长 {dialogue_data['total_duration']:.1f}s")

    client = create_dialogue_client(api_key=api_key)

    qa_data = generate_qa_from_dialogue(
        client=client,
        dialogue_data=dialogue_data,
        num_questions=num_questions,
    )

    setup_output_dirs(output_dir)
    qa_path = output_dir / "QA" / f"{chat_id}.json"
    save_qa_json(qa_data, str(qa_path))

    return qa_data


def main():
    parser = argparse.ArgumentParser(description="SmartGlasses 数据制作 Pipeline")
    parser.add_argument(
        "--mode",
        choices=["full", "text_only", "qa_only"],
        default="full",
        help="运行模式: full=完整流程, text_only=跳过TTS, qa_only=仅生成QA"
    )
    parser.add_argument("--num_samples", type=int, default=1, help="生成样本数量")
    parser.add_argument("--scenario", type=str, default=None, help="指定对话场景")
    parser.add_argument("--duration", type=int, default=300, help="目标时长(秒)")
    parser.add_argument("--num_questions", type=int, default=12, help="QA题目数量")
    parser.add_argument("--textgrid_path", type=str, default=None, help="TextGrid 路径(qa_only模式)")
    parser.add_argument("--spk01_voice", type=str, default="longxiaochun", help="佩戴者音色")
    parser.add_argument("--spk02_voice", type=str, default="longxiaoxia", help="非佩戴者音色")
    parser.add_argument("--api_key", type=str, default=None, help="DashScope API Key")
    parser.add_argument("--output_dir", type=str, default=None, help="输出目录")

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEV_OUTPUT_DIR

    if args.mode == "qa_only":
        if not args.textgrid_path:
            parser.error("--textgrid_path is required for qa_only mode")
        run_qa_only(
            textgrid_path=args.textgrid_path,
            output_dir=output_dir,
            num_questions=args.num_questions,
            api_key=args.api_key,
        )
    else:
        skip_tts = (args.mode == "text_only")

        for i in range(args.num_samples):
            chat_id = get_next_chat_id(output_dir)
            scenario = args.scenario if args.scenario else None

            print(f"\n>>> Generating sample {i+1}/{args.num_samples}: {chat_id}")

            run_full_pipeline(
                chat_id=chat_id,
                output_dir=output_dir,
                scenario=scenario,
                target_duration=args.duration,
                spk01_voice=args.spk01_voice,
                spk02_voice=args.spk02_voice,
                num_questions=args.num_questions,
                skip_tts=skip_tts,
                api_key=args.api_key,
            )


if __name__ == "__main__":
    main()
