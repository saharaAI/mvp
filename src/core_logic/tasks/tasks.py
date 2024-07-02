# --- src/core_logic/tasks/tasks.py ---
import re
import json
import zipfile
import io
from datetime import datetime
from src.core_logic.agents.agents import LLMAgent # Adjust import path if needed

class TaskManager:
    """Manages the lifecycle of a task, from initiation to completion."""

    def __init__(self, llm_agent: LLMAgent): 
        self.llm_agent = llm_agent

    def start_task(self, objective, file_content=None, use_search=False):
        """Starts a new task and manages its execution."""
        task_exchanges = []
        gpt_tasks = []
        file_content_for_gpt = file_content  # Track file content for sub-tasks

        while True:
            previous_results = [result for _, result in task_exchanges]
            if not task_exchanges:
                gpt_result, file_content_for_gpt, search_query = self.llm_agent.orchestrate_task(
                    objective, file_content, previous_results, use_search
                )
            else:
                gpt_result, _, search_query = self.llm_agent.orchestrate_task(
                    objective, previous_results=previous_results, use_search=use_search
                )

            if "The task is complete:" in gpt_result:
                final_output = gpt_result.replace("The task is complete:", "").strip()
                break
            else:
                sub_task_prompt = gpt_result
                if file_content_for_gpt and not gpt_tasks:
                    sub_task_prompt = (
                        f"{sub_task_prompt}\n\nFile content:\n{file_content_for_gpt}"
                    )
                sub_task_result = self.llm_agent.execute_sub_task(
                    sub_task_prompt, search_query, gpt_tasks, use_search
                )
                gpt_tasks.append({"task": sub_task_prompt, "result": sub_task_result})
                task_exchanges.append((sub_task_prompt, sub_task_result))
                file_content_for_gpt = None  # Reset file content after first use

        sub_task_results = [
            f"Orchestrator Prompt: {prompt}\nSub-agent Result: {result}"
            for prompt, result in task_exchanges
        ]

        return sub_task_results

    def generate_report(self, objective, sub_task_results):
        """Generates a refined report using the LLM."""
        sanitized_objective = re.sub(r"\W+", "_", objective)
        timestamp = datetime.now().strftime("%H-%M-%S")
        refined_output = self.llm_agent.refine_output(
            objective, sub_task_results, timestamp, sanitized_objective
        )

        return refined_output