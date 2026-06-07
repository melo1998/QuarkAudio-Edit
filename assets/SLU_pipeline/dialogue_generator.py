"""
对话内容生成模块 - 调用 qwen3-max 生成智能眼镜场景对话
"""
import json
import random
import os
from typing import List, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    print("请安装 openai: pip install openai")
    raise


# 对话场景模板库
DIALOGUE_SCENARIOS = [
    "两个朋友在讨论最近看的电影，一个非常喜欢，另一个觉得很一般，产生了激烈的讨论",
    "一对情侣在讨论周末去哪里旅游，意见不一致，一个想去海边，一个想去山里",
    "两个同事在午餐时间讨论工作项目的进展和遇到的困难",
    "一个人在给朋友推荐一家新开的餐厅，描述食物的味道和环境",
    "两个邻居在讨论小区里最近发生的事情，比如停车问题或者噪音",
    "两个大学同学在聚会时回忆大学时光，讨论各自的近况",
    "一个人在向朋友抱怨家里电器坏了的烦恼，讨论是修还是换",
    "两个家长在接孩子放学时讨论孩子的教育问题",
    "两个朋友在讨论最近的健身计划和饮食控制",
    "一对夫妻在讨论家里的装修方案，对颜色和风格有不同看法",
    "两个朋友在讨论要不要养宠物，分析利弊",
    "两个同事在茶水间讨论公司最近的人事变动和加薪政策",
    "一个人在向朋友倾诉最近的感情烦恼，寻求建议",
    "两个朋友在逛超市时讨论今晚做什么菜",
    "两个人在散步时讨论最近天气变化和穿衣搭配",
    "一对母女在讨论女儿的职业选择和未来规划",
    "两个朋友在讨论最近买的电子产品的使用体验",
    "两个人在等公交时闲聊各自的通勤经历",
    "两个朋友在讨论要不要一起报名学习某个新技能",
    "一对夫妻在讨论孩子的暑假安排",
]


def create_dialogue_client(
    api_key: Optional[str] = None,
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
) -> OpenAI:
    """创建 API 客户端"""
    if api_key is None:
        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        raise ValueError(
            "请设置 DASHSCOPE_API_KEY 环境变量或传入 api_key 参数。"
            "获取方式: https://dashscope.console.aliyun.com/"
        )
    import httpx
    # 检测系统代理
    proxy_url = _detect_system_proxy()
    # 使用自定义 httpx client，增加超时并配置代理
    http_client = httpx.Client(
        timeout=httpx.Timeout(connect=60.0, read=300.0, write=60.0, pool=60.0),
        verify=True,
        follow_redirects=True,
        proxy=proxy_url,
    )
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=300.0,
        max_retries=5,
        http_client=http_client,
    )


def _detect_system_proxy() -> Optional[str]:
    """自动检测 Windows 系统代理设置"""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        )
        proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if proxy_enable:
            proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
            proxy_url = f"http://{proxy_server}"
            print(f"  [Proxy] Detected system proxy: {proxy_url}")
            return proxy_url
    except Exception:
        pass
    return None


def generate_dialogue_content(
    client: OpenAI,
    scenario: Optional[str] = None,
    target_duration_seconds: int = 300,
    model: str = "qwen3-max"
) -> Dict:
    """
    调用 qwen3-max 生成对话内容，包含详细的时间戳信息。

    返回格式:
    {
        "scenario": "场景描述",
        "total_duration": 300.0,
        "main_speaker": "spk01",
        "segments": [
            {"speaker": "spk01", "start": 0.0, "end": 3.5, "text": "你好啊"},
            {"speaker": "spk02", "start": 3.8, "end": 6.2, "text": "你好"},
            ...
        ]
    }
    """
    if scenario is None:
        scenario = random.choice(DIALOGUE_SCENARIOS)

    system_prompt = """你是一个专业的中文对话数据生成器，用于智能眼镜语音对话场景的数据增强。

你需要生成非常真实自然的中文日常对话，模拟智能眼镜佩戴者（spk01）与对面的人（spk02）之间的面对面交流。

关键要求：
1. 对话必须完全使用中文，内容要非常真实、口语化，包含：
   - 语气词（嗯、啊、哦、呃、那个、就是说）
   - 重复和犹豫（"我我我觉得"、"就是就是"）
   - 打断和抢话（两人说话时间有少量重叠）
   - 自然的语速变化（有的句子短促，有的句子拖长）
   
2. 每句话需要标注精确的起止时间（秒），注意：
   - 句与句之间有自然的停顿（0.2-2.0秒不等）
   - 偶尔两个人的说话时间会有短暂重叠（0.1-0.5秒）
   - 说话语速大约每秒3-5个字（考虑停顿和语气词）
   - 长句子持续2-8秒，短回应0.3-1.5秒
   
3. 对话特征：
   - 两人说话量大致均衡，但可以有主导方
   - 包含情绪起伏（兴奋、不满、无奈、开心等）
   - 包含具体的数字、人名、地名等细节信息
   - 对话逻辑连贯，有主题展开和转折

请以严格的JSON格式输出，不要包含任何其他文字。"""

    user_prompt = f"""请生成一段约{target_duration_seconds}秒的中文日常对话。

场景设定：{scenario}

spk01 是智能眼镜佩戴者，spk02 是对面和他/她交流的人。

请严格按照以下JSON格式输出（不要输出其他内容）：
{{
    "scenario": "简短场景描述",
    "total_duration": {target_duration_seconds},
    "main_speaker": "spk01",
    "segments": [
        {{"speaker": "spk01", "start": 0.5, "end": 3.2, "text": "第一句话内容"}},
        {{"speaker": "spk02", "start": 3.5, "end": 5.8, "text": "回应内容"}},
        ...更多对话段落，确保覆盖整个{target_duration_seconds}秒时长...
    ]
}}

要求：
- segments 按时间顺序排列
- 最后一个 segment 的 end 时间应接近 {target_duration_seconds}
- 生成至少60个以上的对话段落
- 包含丰富的情绪变化和口语特征"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.9,
        max_tokens=16000,
        extra_body={"enable_thinking": False}
    )

    response_text = response.choices[0].message.content.strip()

    # 清理可能的 markdown 代码块标记
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("```", 1)[0]
    response_text = response_text.strip()

    dialogue_data = json.loads(response_text)
    dialogue_data = validate_and_fix_dialogue(dialogue_data, target_duration_seconds)

    return dialogue_data


def validate_and_fix_dialogue(dialogue_data: Dict, target_duration: int) -> Dict:
    """验证并修复对话数据的时间一致性"""
    segments = dialogue_data.get("segments", [])
    if not segments:
        raise ValueError("生成的对话没有任何段落")

    # 按开始时间排序
    segments.sort(key=lambda x: x["start"])

    # 修复时间问题
    fixed_segments = []
    for i, seg in enumerate(segments):
        start = round(float(seg["start"]), 2)
        end = round(float(seg["end"]), 2)

        if end <= start:
            text_len = len(seg["text"])
            end = round(start + max(0.5, text_len * 0.25), 2)

        if start < 0:
            start = 0.0

        fixed_segments.append({
            "speaker": seg["speaker"],
            "start": start,
            "end": end,
            "text": seg["text"]
        })

    dialogue_data["segments"] = fixed_segments
    dialogue_data["total_duration"] = max(
        target_duration,
        max(seg["end"] for seg in fixed_segments) + 0.5
    )

    return dialogue_data


def extract_dialogue_from_textgrid(textgrid_path: str) -> Dict:
    """
    从现有 TextGrid 提取对话内容，用于参考或重新生成QA。
    """
    from textgrid_utils import parse_textgrid

    tg = parse_textgrid(textgrid_path)
    segments = []
    for tier in tg.tiers:
        for iv in tier.get_speech_intervals():
            segments.append({
                "speaker": tier.name,
                "start": iv.xmin,
                "end": iv.xmax,
                "text": iv.text
            })

    segments.sort(key=lambda x: x["start"])

    return {
        "scenario": "extracted_from_textgrid",
        "total_duration": tg.xmax,
        "main_speaker": "spk01",
        "segments": segments
    }


if __name__ == "__main__":
    # 测试从现有 TextGrid 提取对话
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    textgrid_path = r".\Dev\Part1\textgrid\chat_0330.TextGrid"
    dialogue = extract_dialogue_from_textgrid(textgrid_path)
    print(f"Extracted {len(dialogue['segments'])} segments, "
          f"duration: {dialogue['total_duration']:.2f}s")
    for seg in dialogue["segments"][:5]:
        print(f"  [{seg['start']:.2f}-{seg['end']:.2f}] {seg['speaker']}: {seg['text'][:30]}")
