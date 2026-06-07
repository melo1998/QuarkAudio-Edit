"""TextGrid 解析与生成工具模块"""
import re
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Interval:
    """一个时间区间段"""
    xmin: float
    xmax: float
    text: str

    @property
    def duration(self) -> float:
        return self.xmax - self.xmin

    def is_silence(self) -> bool:
        return self.text.strip() == ""


@dataclass
class SpeakerTier:
    """一个说话人的所有时间段"""
    name: str
    xmin: float
    xmax: float
    intervals: List[Interval] = field(default_factory=list)

    def get_speech_intervals(self) -> List[Interval]:
        """获取所有有语音的区间"""
        return [iv for iv in self.intervals if not iv.is_silence()]

    def total_speech_duration(self) -> float:
        return sum(iv.duration for iv in self.get_speech_intervals())


@dataclass
class TextGrid:
    """完整的 TextGrid 数据结构"""
    xmin: float
    xmax: float
    tiers: List[SpeakerTier] = field(default_factory=list)

    def get_tier_by_name(self, name: str) -> SpeakerTier:
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise ValueError(f"Tier '{name}' not found")

    def get_all_speech_segments(self) -> List[Tuple[str, Interval]]:
        """获取所有说话段，按时间排序，返回 (speaker_name, interval)"""
        segments = []
        for tier in self.tiers:
            for iv in tier.get_speech_intervals():
                segments.append((tier.name, iv))
        segments.sort(key=lambda x: x[1].xmin)
        return segments


def parse_textgrid(filepath: str, encoding: str = "utf-8") -> TextGrid:
    """解析 Praat TextGrid 文件"""
    with open(filepath, "r", encoding=encoding) as f:
        content = f.read()

    # 解析全局 xmin/xmax
    global_xmin = float(re.search(r'^xmin\s*=\s*([\d.]+)', content, re.MULTILINE).group(1))
    global_xmax = float(re.search(r'^xmax\s*=\s*([\d.]+)', content, re.MULTILINE).group(1))

    tg = TextGrid(xmin=global_xmin, xmax=global_xmax)

    # 按 item [N] 分割 tiers
    tier_blocks = re.split(r'item\s*\[\d+\]\s*:', content)[1:]

    for block in tier_blocks:
        name_match = re.search(r'name\s*=\s*"([^"]*)"', block)
        tier_name = name_match.group(1) if name_match else "unknown"

        tier_xmin_match = re.search(r'xmin\s*=\s*([\d.]+)', block)
        tier_xmax_match = re.search(r'xmax\s*=\s*([\d.]+)', block)
        tier_xmin = float(tier_xmin_match.group(1)) if tier_xmin_match else global_xmin
        tier_xmax = float(tier_xmax_match.group(1)) if tier_xmax_match else global_xmax

        tier = SpeakerTier(name=tier_name, xmin=tier_xmin, xmax=tier_xmax)

        # 解析 intervals
        interval_blocks = re.split(r'intervals\s*\[\d+\]\s*:', block)[1:]
        for iv_block in interval_blocks:
            iv_xmin = float(re.search(r'xmin\s*=\s*([\d.]+)', iv_block).group(1))
            iv_xmax = float(re.search(r'xmax\s*=\s*([\d.]+)', iv_block).group(1))
            text_match = re.search(r'text\s*=\s*"([^"]*)"', iv_block)
            text = text_match.group(1) if text_match else ""
            tier.intervals.append(Interval(xmin=iv_xmin, xmax=iv_xmax, text=text))

        tg.tiers.append(tier)

    return tg


def generate_textgrid(textgrid: TextGrid) -> str:
    """从 TextGrid 数据结构生成 Praat TextGrid 文件内容"""
    lines = []
    lines.append('File type = "ooTextFile"')
    lines.append('Object class = "TextGrid"')
    lines.append('')
    lines.append(f'xmin = {textgrid.xmin} ')
    lines.append(f'xmax = {textgrid.xmax} ')
    lines.append('tiers? <exists> ')
    lines.append(f'size = {len(textgrid.tiers)} ')
    lines.append('item []: ')

    for tier_idx, tier in enumerate(textgrid.tiers, 1):
        lines.append(f'    item [{tier_idx}]:')
        lines.append(f'        class = "IntervalTier" ')
        lines.append(f'        name = "{tier.name}" ')
        lines.append(f'        xmin = {tier.xmin} ')
        lines.append(f'        xmax = {tier.xmax} ')
        lines.append(f'        intervals: size = {len(tier.intervals)} ')

        for iv_idx, interval in enumerate(tier.intervals, 1):
            lines.append(f'        intervals [{iv_idx}]:')
            lines.append(f'            xmin = {interval.xmin} ')
            lines.append(f'            xmax = {interval.xmax} ')
            lines.append(f'            text = "{interval.text}" ')

    return '\n'.join(lines)


def save_textgrid(textgrid: TextGrid, filepath: str, encoding: str = "utf-8"):
    """保存 TextGrid 到文件"""
    content = generate_textgrid(textgrid)
    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


def dialogue_to_textgrid(
    dialogue_segments: List[dict],
    total_duration: float
) -> TextGrid:
    """
    将对话段落列表转换为 TextGrid。

    dialogue_segments 格式:
    [
        {"speaker": "spk01", "start": 0.0, "end": 3.5, "text": "你好啊"},
        {"speaker": "spk02", "start": 3.8, "end": 6.2, "text": "你好"},
        ...
    ]
    """
    speaker_names = sorted(set(seg["speaker"] for seg in dialogue_segments))
    if len(speaker_names) < 2:
        speaker_names = ["spk01", "spk02"]

    tg = TextGrid(xmin=0, xmax=total_duration)

    for speaker_name in speaker_names:
        speaker_segments = [s for s in dialogue_segments if s["speaker"] == speaker_name]
        speaker_segments.sort(key=lambda x: x["start"])

        intervals = []
        current_time = 0.0

        for seg in speaker_segments:
            start = round(seg["start"], 2)
            end = round(seg["end"], 2)

            if start > current_time + 0.01:
                intervals.append(Interval(xmin=current_time, xmax=start, text=""))

            intervals.append(Interval(xmin=start, xmax=end, text=seg["text"]))
            current_time = end

        if current_time < total_duration:
            intervals.append(Interval(xmin=current_time, xmax=total_duration, text=""))

        tier = SpeakerTier(
            name=speaker_name,
            xmin=0,
            xmax=total_duration,
            intervals=intervals
        )
        tg.tiers.append(tier)

    return tg


if __name__ == "__main__":
    # 测试解析现有 TextGrid
    import sys
    test_path = r"D:\AliBaBa\Project\03_ai_glasses\SmartGlasses-Track1\Track1\Dev\Part1\textgrid\chat_0330.TextGrid"
    tg = parse_textgrid(test_path)
    print(f"Duration: {tg.xmax:.2f}s, Tiers: {len(tg.tiers)}")
    for tier in tg.tiers:
        speech = tier.get_speech_intervals()
        print(f"  {tier.name}: {len(speech)} speech segments, "
              f"total speech: {tier.total_speech_duration():.2f}s")
        for seg in speech[:3]:
            print(f"    [{seg.xmin:.2f}-{seg.xmax:.2f}] {seg.text}")
