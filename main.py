# D:\metagpt\MetaGPT\main.py
import os
import asyncio
import sys
from metagpt.schema import Message
from metagpt.roles.designer_agent import DesignerAgent
#from metagpt.config2 import Config


async def main():

    #config = Config.default()
    #print("\n--- LLM 相关环境变量 ---")
    #for key, value in os.environ.items():
    #    if "OPENAI" in key.upper() or "LLM" in key.upper() or "DEEPSEEK" in key.upper():
    #        print(f"{key}: {value}")
    #print("------------------------\n")

    #print(f"当前 LLM 类型: {config.llm.api_type}")
    #print(f"模型: {config.llm.model}")
    #print(f"API 端点: {config.llm.base_url}")
    #print(f"API Key (完整): {config.llm.api_key}")

    #user_request = "生成一个空调遥控器说明。"
    # 从命令行或手动获取用户输入
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input("请输入你的用户需求（按回车结束）：")
    print(f"用户需求: {user_request}\n")

    designer_role = DesignerAgent()

    designer_role.rc.todo = user_request

    result_message = await designer_role._act()

    print("生成的 JSON 规范：\n")
    if result_message and result_message.instruct_content:
        print(result_message.instruct_content.model_dump_json(indent=2))
    elif result_message:
        print(result_message.content)
    else:
        print("未生成任何规范。")

    if result_message and (result_message.instruct_content or result_message.content):
        output_filename = "factorial_spec.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            if result_message.instruct_content:
                f.write(result_message.instruct_content.model_dump_json(indent=2))
            else:
                f.write(result_message.content)
        print(f"\n已保存为 {output_filename}")


if __name__ == "__main__":
    asyncio.run(main())