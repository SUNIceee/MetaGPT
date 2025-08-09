import json
from typing import Any, Dict, List, Optional

from pydantic import Field, BaseModel

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.schema import Message, AIMessage
from metagpt.config2 import Config
from metagpt.actions.generate_ltl_spec import GenerateLTLSpecification

class LTLDesignerAgent(Role):
    name: str = Field(default="LTLDesigner")
    profile: str = Field(default="LTL Formalization Expert")
    goal: str = "Transform natural language process descriptions into LTL formal specifications."
    constraints: str = "Output ONLY a well-structured LTL description, strictly adhering to the specified format. Do NOT include any extraneous remarks."

    def __init__(
        self,
        name: str = "LTLDesigner",
        profile: str = "LTL Formalization Expert",
        goal: str = "Generate a structured LTL specification for a process based on user requirements.",
        constraints: str = "The output must be a valid LTL description conforming to the specified format.",
        **kwargs,
    ):
        super().__init__(
            name=name,
            profile=profile,
            goal=goal,
            constraints=constraints,
            **kwargs
        )
        self.set_actions([GenerateLTLSpecification])

    async def _act(self) -> Message:
        user_request_content = None
        if hasattr(self.rc.todo, "content"):
            user_request_content = self.rc.todo.content
        elif isinstance(self.rc.todo, str):
            user_request_content = self.rc.todo
        elif self.rc.memory.get_latest_message():
             user_request_content = self.rc.memory.get_latest_message().content
        else:
            logger.warning("无法获取用户请求内容，LTLDesignerAgent 无法执行动作。")
            return Message(content="无法获取用户请求内容，任务终止。", role=self.profile)


        logger.info(f"{self.name}({self.profile}): 正在根据请求生成LTL规范: {user_request_content[:50]}...")

        generate_ltl_action = self.actions[0]

        result_msg = await generate_ltl_action.run(user_request_content)

        return result_msg