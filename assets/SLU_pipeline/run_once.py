"""
快速启动脚本 - 运行单个 pipeline 实例并将日志写入文件
直接执行: python run_once.py
"""
import os
import sys
import traceback

# 设置 API Key（如果环境变量未设置）
if not os.environ.get("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = ""

# 设置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
os.chdir(PROJECT_ROOT)

LOG_FILE = os.path.join(SCRIPT_DIR, "output", "pipeline_log.txt")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 重定向输出到文件和终端
class TeeWriter:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = TeeWriter(LOG_FILE)

try:
    from pathlib import Path
    from run_pipeline import run_full_pipeline, DEV_OUTPUT_DIR, get_next_chat_id, setup_output_dirs

    output_dir = DEV_OUTPUT_DIR
    chat_id = get_next_chat_id(output_dir)

    print(f"=== Pipeline Run ===")
    print(f"Chat ID: {chat_id}")
    print(f"Output Dir: {output_dir}")
    print(f"Mode: text_only (skip TTS, use silence)")
    print()

    result = run_full_pipeline(
        chat_id=chat_id,
        output_dir=output_dir,
        scenario="两个朋友在讨论最近看的一部电影，一个非常喜欢觉得是神作，另一个觉得很一般剧情太老套，两人争论不休",
        target_duration=300,
        num_questions=12,
        skip_tts=True,  # 先跳过TTS，用静音验证流程
        api_key=os.environ["DASHSCOPE_API_KEY"],
    )

    print("\n=== Pipeline Result ===")
    print(f"Audio: {result['audio_path']}")
    print(f"TextGrid: {result['textgrid_path']}")
    print(f"QA: {result['qa_path']}")
    print(f"QA Questions: {len(result['qa_data']['questions'])}")
    print("\n=== DONE ===")

except Exception:
    traceback.print_exc()
    print("\n=== FAILED ===")
