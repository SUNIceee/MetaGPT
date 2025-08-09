import json
from typing import Any, Dict, List, Optional
from pydantic import Field, BaseModel

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.config2 import Config
from metagpt.prompts.ltl_prompts import LTL_SYSTEM_DESIGN_PROMPT


# 这里我们不需要一个Pydantic模型来验证LTL输出，因为它是自由格式的文本
# 但我们仍然可以定义一个简单的模型来保持结构化
class LTLSpecification(BaseModel):
    ltl_description: str


class GenerateLTLSpecification(Action):
    name: str = "GenerateLTLSpecification"
    description: str = "Transforms natural language process descriptions into LTL formal specifications."

    async def run(self, user_request: str) -> Message:
        prompt = LTL_SYSTEM_DESIGN_PROMPT.format(user_prompt=user_request)
        ltl_spec_str = await self.llm.aask(prompt, stream=False)
        logger.info(f"Generated LTL string for request: {user_request}")

        # LTL输出是自由格式文本，不需要JSON解析和Pydantic验证
        instruct_content_model = None
        # 如果需要，这里可以添加一些后处理逻辑

        return Message(
            content=ltl_spec_str,
            instruct_content=instruct_content_model  # 或者 LTLSpecification(ltl_description=ltl_spec_str)
        )