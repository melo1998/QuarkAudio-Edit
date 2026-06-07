"""
QA 问题生成模块 - 调用 qwen3-max 基于对话内容生成多选题
"""
import json
import os
from typing import List, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    print("请安装 openai: pip install openai")
    raise


def generate_qa_from_dialogue(
    client: OpenAI,
    dialogue_data: Dict,
    num_questions: int = 12,
    model: str = "qwen3-max"
) -> Dict:
    """
    基于对话内容生成 SLU 多选题。

    参考 SmartGlasses Challenge 的 QA 题目风格：
    - 声学特征分析题（语速、语调、音量、停顿）
    - 情绪态度判断题
    - 说话人识别题
    - 事实细节推理题（数字计算、因果关系）
    - 语用意图分析题（反语、讽刺、试探）
    - 对话动态分析题（抢话、打断、话语权）

    Args:
        client: OpenAI 客户端
        dialogue_data: 对话数据
        num_questions: 生成题目数量
        model: 模型名称

    Returns:
        {"questions": [{question, options:[{label, text}], answer}, ...]}
    """
    # 构建对话转录文本
    transcript_lines = []
    for seg in dialogue_data["segments"]:
        speaker_label = "佩戴者" if seg["speaker"] == "spk01" else "非佩戴者"
        transcript_lines.append(
            f"[{seg['start']:.2f}-{seg['end']:.2f}] {speaker_label}({seg['speaker']}): {seg['text']}"
        )
    transcript = "\n".join(transcript_lines)

    system_prompt = """你是一个专业的智能眼镜语音对话理解评测题目设计专家。

你的任务是基于给定的对话转录（含精确时间戳、说话人标注），设计高质量的多选题来评估语音语言理解（SLU）能力。

题目类型应覆盖以下维度：

1. **声学特征分析题**（约30%）：
   - 分析特定时间段内说话人的语速变化、语调升降、音量变化、停顿模式
   - 对比两个时间段的声学特征差异
   - 分析非语言声音（叹气、笑声、结巴、清嗓）

2. **情绪态度判断题**（约25%）：
   - 判断特定时间段说话人的情绪状态
   - 分析情绪转变的过程和原因
   - 区分表面情绪和深层心理

3. **事实细节推理题**（约20%）：
   - 基于对话提到的数字进行计算推理
   - 因果关系推断
   - 具体事件的细节还原

4. **语用意图分析题**（约15%）：
   - 识别反语、讽刺、夸张等修辞手法
   - 分析说话人的真实意图vs表面含义
   - 分析对话策略（试探、妥协、施压）

5. **对话动态分析题**（约10%）：
   - 说话人识别（基于音色差异）
   - 话语重叠和抢话现象分析
   - 对话主导权的转换

题目设计要求：
- 每题4个选项(A/B/C/D)，只有1个正确答案
- 干扰项必须合理但可区分，不能太离谱
- 引用具体时间段时使用 [start-end] 格式
- 选项文本要详细具体，避免过于笼统
- 正确答案的分布要均匀（不要集中在某个选项）
- 难度适中偏高，需要结合声学和语义信息才能判断

请以严格JSON格式输出，不要包含其他文字。"""

    user_prompt = f"""以下是一段智能眼镜佩戴者与对面人的对话转录，总时长约{dialogue_data['total_duration']:.0f}秒：

{transcript}

请基于以上对话内容，生成{num_questions}道高质量的多选题。

输出格式：
{{
    "questions": [
        {{
            "question": "问题描述（可引用具体时间段）",
            "options": [
                {{"label": "A", "text": "选项A的详细描述"}},
                {{"label": "B", "text": "选项B的详细描述"}},
                {{"label": "C", "text": "选项C的详细描述"}},
                {{"label": "D", "text": "选项D的详细描述"}}
            ],
            "answer": "正确答案的标签字母"
        }},
        ...共{num_questions}道题
    ]
}}

注意：
1. 答案分布要均匀(A/B/C/D各约25%)
2. 至少3道题涉及具体时间段的声学特征分析
3. 至少2道题涉及数字推理或事实细节
4. 至少2道题涉及情绪态度判断
5. 至少1道题涉及语用意图分析（反语/讽刺等）"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=16000,
        extra_body={"enable_thinking": False}
    )

    response_text = response.choices[0].message.content.strip()

    # 清理 markdown 代码块标记
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("```", 1)[0]
    response_text = response_text.strip()

    qa_data = json.loads(response_text)
    qa_data = validate_qa_data(qa_data)

    return qa_data


def validate_qa_data(qa_data: Dict) -> Dict:
    """验证并修复 QA 数据格式"""
    questions = qa_data.get("questions", [])
    validated = []

    for question_item in questions:
        question_text = question_item.get("question", "")
        options = question_item.get("options", [])
        answer = question_item.get("answer", "")

        if not question_text or len(options) != 4:
            continue

        # 确保选项标签正确
        expected_labels = ["A", "B", "C", "D"]
        fixed_options = []
        for i, opt in enumerate(options):
            fixed_options.append({
                "label": expected_labels[i],
                "text": opt.get("text", "")
            })

        # 确保答案有效
        if answer not in expected_labels:
            answer = "A"

        validated.append({
            "question": question_text,
            "options": fixed_options,
            "answer": answer
        })

    return {"questions": validated}


def save_qa_json(qa_data: Dict, filepath: str):
    """保存 QA 数据为 JSON 文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved QA: {filepath} ({len(qa_data['questions'])} questions)")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from dialogue_generator import extract_dialogue_from_textgrid

    # 从现有 TextGrid 提取对话
    textgrid_path = r"D:\AliBaBa\Project\03_ai_glasses\SmartGlasses-Track1\Track1\Dev\Part1\textgrid\chat_0330.TextGrid"
    dialogue = extract_dialogue_from_textgrid(textgrid_path)
    print(f"Extracted dialogue: {len(dialogue['segments'])} segments")
    print("To generate QA, set DASHSCOPE_API_KEY and run the main pipeline.")
