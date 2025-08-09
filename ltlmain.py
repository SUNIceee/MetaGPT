import os
import asyncio
import sys
from metagpt.schema import Message
from metagpt.roles.ltl_agent import LTLDesignerAgent # 导入新的角色
from metagpt.config2 import Config


async def main():

    config = Config.default()
    # 打印API Key以便调试，但出于安全考虑，在生产环境中不建议这样做
    #print(f"API Key (完整): {config.llm.api_key}")

    # 从命令行或手动获取用户输入
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input("请输入你的自然语言流程需求（按回车结束）：")
    print(f"用户需求: {user_request}\n")

    ltl_designer_role = LTLDesignerAgent()

    ltl_designer_role.rc.todo = user_request

    result_message = await ltl_designer_role._act()

    print("生成的 LTL 规范：\n")
    if result_message and result_message.content:
        print(result_message.content)
    else:
        print("未生成任何规范。")

    if result_message and result_message.content:
        output_filename = "ltl_spec.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result_message.content)
        print(f"\n已保存为 {output_filename}")


if __name__ == "__main__":
    asyncio.run(main())