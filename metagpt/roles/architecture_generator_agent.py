from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.actions.generate_architecture_action import GenerateArchitectureAction

class ArchitectureGeneratorAgent(Role):
    name: str = "ArchitectureGenerator"
    profile: str = "Software Architect"
    goal: str = "Design a robust and well-structured code architecture based on business processes."
    constraints: str = "Output must be a structured document detailing the architecture, following the specified format."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateArchitectureAction])

    async def _act(self) -> Message:
        # 假设输入包含业务流程和LTL规范，以特定格式传递
        user_input = self.rc.todo

        if not isinstance(user_input, dict) or 'description' not in user_input or 'ltl' not in user_input:
            logger.error("Invalid input format. Expected a dictionary with 'description' and 'ltl' keys.")
            return Message(content="Invalid input format.", role="architect")

        description = user_input['description']
        ltl_spec = user_input['ltl']

        logger.info("Starting architecture generation process...")
        generate_action = self.actions[0]
        architecture_message = await generate_action.run(
            business_process_description=description,
            ltl_specification=ltl_spec
        )

        return architecture_message