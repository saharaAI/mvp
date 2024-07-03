# --- src/core_logic/task_manager.py ---
import re
from datetime import datetime
from .llm_interactions import LLMAgent

class TaskManager:
    """Manages the lifecycle of a task, from initiation to completion."""

    def __init__(self, llm_agent: LLMAgent): 
        self.llm_agent = llm_agent

    def start_task(self, objective, balance_sheet_data=None, use_search=False):
        """Starts a new task and manages its execution."""
        task_exchanges = []
        file_content_for_gpt = balance_sheet_data

        while True:
            previous_results = [result for _, result in task_exchanges]
            gpt_result, search_query = self.llm_agent.orchestrate_task(
                objective, file_content_for_gpt, previous_results, use_search
            )

            if "The task is complete:" in gpt_result:
                final_output = gpt_result.replace("The task is complete:", "").strip()
                break
            else:
                sub_task_prompt = gpt_result
                if file_content_for_gpt and not task_exchanges:
                    sub_task_prompt = f"{sub_task_prompt}\n\nFile content:\n{file_content_for_gpt}"
                sub_task_result = self.llm_agent.execute_sub_task(
                    sub_task_prompt, file_content_for_gpt, search_query
                )
                task_exchanges.append((sub_task_prompt, sub_task_result))
                file_content_for_gpt = None

        sub_task_results = [
            f"Orchestrator Prompt: {prompt}\nSub-agent Result: {result}"
            for prompt, result in task_exchanges
        ]

        return sub_task_results

    def generate_report(self, objective, sub_task_results):
        """Generates a refined report using the LLM."""
        sanitized_objective = re.sub(r"\W+", "_", objective)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        refined_output = self.llm_agent.provide_expert_insights("\n".join(sub_task_results))
        return refined_output
