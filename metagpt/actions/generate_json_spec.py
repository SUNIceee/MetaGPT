# D:\metagpt\MetaGPT\metagpt\actions\generate_json_spec.py

import json
from typing import Any, Dict, List, Optional
from pydantic import Field, BaseModel

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.config2 import Config
from metagpt.prompts.my_custom_prompts.agent1_prompts import AGENT1_SYSTEM_DESIGN_PROMPT # 保持不变

# 定义你的 JSON 规范输出结构 (保持不变)
class JsonSpecification(BaseModel):
    name: str
    description: str
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    output: Dict[str, Any]
    exceptions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    examples: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class GenerateJsonSpecification(Action):

    name: str = "GenerateJsonSpecification"
    description: str = "Transforms natural language into a structured JSON formal specification for code generation."

    async def run(self, user_request: str) -> Message:
        prompt = AGENT1_SYSTEM_DESIGN_PROMPT.format(user_prompt=user_request)
        json_spec_str = await self.llm.aask(prompt, stream=False)
        logger.info(f"Generated raw JSON string for request: {user_request}")

        instruct_content_model = None
        cleaned_json_str = json_spec_str.strip()
        if cleaned_json_str.startswith("```json"):
            cleaned_json_str = cleaned_json_str[len("```json"):].strip()
        if cleaned_json_str.endswith("```"):
            cleaned_json_str = cleaned_json_str[:-len("```")].strip()

        try:
            spec_data = json.loads(cleaned_json_str)
            instruct_content_model = JsonSpecification(**spec_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response: {e}. Raw response: {json_spec_str}")
        except Exception as e:
            logger.error(f"Error creating JsonSpecification model: {e}. Raw data: {cleaned_json_str}")

        return Message(
            content=json_spec_str,
            instruct_content=instruct_content_model
        )