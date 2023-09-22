import json
from typing import Union, List, Optional
from pandasai.helpers.df_info import DataFrameType
from pandasai.helpers.logger import Logger
from pandasai.prompts.clarification_questions_prompt import ClarificationQuestionPrompt
from pandasai.prompts.explain_prompt import ExplainPrompt
from pandasai.schemas.df_config import Config
from pandasai.smart_datalake import SmartDatalake


class Agent:
    """
    Agent class to improve the conversational experience in PandasAI
    """

    _lake: SmartDatalake = None
    _logger: Optional[Logger] = None
    _memory_size: int = None

    def __init__(
        self,
        dfs: Union[DataFrameType, List[DataFrameType]],
        config: Optional[Union[Config, dict]] = None,
        logger: Optional[Logger] = None,
        memory_size: int = 1,
    ):
        """
        Args:
            df (Union[SmartDataframe, SmartDatalake]): _description_
            memory_size (int, optional): _description_. Defaults to 1.
        """

        if not isinstance(dfs, list):
            dfs = [dfs]

        self._lake = SmartDatalake(dfs, config, logger)
        self._logger = self._lake.logger
        self._memory_size = memory_size

    def chat(self, query: str, output_type: Optional[str] = None):
        """
        Simulate a chat interaction with the assistant on Dataframe.
        """
        try:
            result = self._lake.chat(
                query,
                output_type=output_type,
                start_conversation=self._lake._memory.get_conversation(
                    self._memory_size
                ),
            )
            return result
        except Exception as exception:
            return (
                "Unfortunately, I was not able to get your answers, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )

    def clarification_questions(self) -> List[str]:
        """
        Generate clarification questions based on the data
        """
        try:
            prompt = ClarificationQuestionPrompt(
                self._lake.dfs, self._lake._memory.get_conversation(self._memory_size)
            )

            result = self._lake.llm.call(prompt)
            self._logger.log(
                f"""Clarification Questions:  {result}
                """
            )
            questions: list[str] = json.loads(result)
            return questions[:3]

        except Exception as exception:
            raise exception

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self._lake._memory.clear()

    def explain(self) -> str:
        """
        Returns the explanation of the code how it reached to the solution
        """
        try:
            prompt = ExplainPrompt(
                self._lake._memory.get_conversation(self._memory_size),
                self._lake.last_code_executed,
            )
            response = self._lake.llm.call(prompt)
            self._logger.log(
                f"""Explaination:  {response}
                """
            )
            return response
        except Exception as exception:
            return (
                "Unfortunately, I was not able to explain, "
                "because of the following error:\n"
                f"\n{exception}\n"
            )
