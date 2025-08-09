from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.prompts.architecture_prompts import ARCHITECTURE_PROMPT

class GenerateArchitectureAction(Action):
    name: str = "GenerateArchitecture"
    description: str = "Generates a layered code architecture document from a business process and LTL specification."

    async def run(self, business_process_description: str, ltl_specification: str) -> Message:
        prompt = ARCHITECTURE_PROMPT.format(
            business_process_description=business_process_description,
            ltl_specification=ltl_specification
        )
        logger.info("Generating code architecture...")
        architecture_doc = await self.llm.aask(prompt, stream=False)

        return Message(content=architecture_doc, role="architect")