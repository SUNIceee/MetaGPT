# D:\metagpt\MetaGPT\metagpt\roles\designer_agent.py

import json
from typing import Any, Dict, List, Optional

from pydantic import Field, BaseModel

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message, AIMessage
from metagpt.config2 import Config
from metagpt.actions.generate_json_spec import GenerateJsonSpecification, JsonSpecification

class DesignerAgent(Role):
    name: str = Field(default="DesignerAI")
    profile: str = Field(default="System Designer")
    goal: str = "Transform natural language requests into JSON formal specifications for code generation"
    constraints: str = "Output ONLY a well-formed, directly parsable JSON string, strictly adhering to the defined structure. Do NOT include any explanatory text or extraneous remarks."

    def __init__(
        self,
        name: str = "Designer",
        profile: str = "System Designer",
        goal: str = "Generate a structured JSON specification for a Python function based on user requirements.",
        constraints: str = "The output must be a valid JSON object conforming to the JsonSpecification schema.",
        **kwargs,
    ):
        super().__init__(
            name=name,
            profile=profile,
            goal=goal,
            constraints=constraints,
            **kwargs
        )
        self.set_actions([GenerateJsonSpecification])

    async def _act(self) -> Message:
        user_request_content = None
        if hasattr(self.rc.todo, "content"):
            user_request_content = self.rc.todo.content
        elif isinstance(self.rc.todo, str):
            user_request_content = self.rc.todo
        elif self.rc.memory.get_latest_message():
             user_request_content = self.rc.memory.get_latest_message().content
        else:
            logger.warning("无法获取用户请求内容，DesignerAgent 无法执行动作。")
            return Message(content="无法获取用户请求内容，任务终止。", role=self.profile)


        logger.info(f"{self.name}({self.profile}): 正在根据请求生成JSON规范: {user_request_content[:50]}...")

        generate_spec_action = self.actions[0]

        result_msg = await generate_spec_action.run(user_request_content)

        return result_msg
