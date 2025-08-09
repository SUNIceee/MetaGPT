import asyncio
import json
from metagpt.config2 import Config
from metagpt.roles.architecture_generator_agent import ArchitectureGeneratorAgent


async def main():
    """
    程序主入口，用于接收用户输入的业务流程描述和LTL规范，
    然后调用 ArchitectureGeneratorAgent 来生成代码架构设计文档。
    """

    # 提示用户输入业务流程描述
    print("请输入您的业务流程描述（以一个空行结束输入）：")
    business_process_lines = []
    while True:
        line = input()
        if not line:
            break
        business_process_lines.append(line)
    business_process = "\n".join(business_process_lines)

    # 提示用户输入LTL规范
    print("\n请输入您的LTL规范（以一个空行结束输入）：")
    ltl_specification_lines = []
    while True:
        line = input()
        if not line:
            break
        ltl_specification_lines.append(line)
    ltl_specification = "\n".join(ltl_specification_lines)

    # 将输入打包成字典，传递给agent
    input_data = {
        "description": business_process,
        "ltl": ltl_specification
    }

    # 初始化并运行agent
    # 注意：确保 ArchitectureGeneratorAgent 已经根据之前的指导进行了修正
    architect_agent = ArchitectureGeneratorAgent()
    architect_agent.rc.todo = input_data

    print("\nArchitecture generation started...")

    try:
        result_message = await architect_agent._act()

        if result_message and result_message.content:
            print("\n--- Generated Code Architecture Document ---\n")
            print(result_message.content)

            with open("generated_architecture.md", "w", encoding="utf-8") as f:
                f.write(result_message.content)
            print("\nArchitecture document saved to generated_architecture.md")
        else:
            print("Failed to generate architecture document. The agent returned an empty or invalid message.")
    except Exception as e:
        print(f"An error occurred during the architecture generation process: {e}")


if __name__ == "__main__":
    asyncio.run(main())
