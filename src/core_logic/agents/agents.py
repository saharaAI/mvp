# --- src/core_logic/agents/agents.py ---
from litellm import completion
import re
import json
from datetime import datetime

class LLMAgent:
    """Handles interaction with Large Language Models (LLMs)."""

    def __init__(self, orchestrator_model, sub_agent_model, refiner_model):
        self.orchestrator_model = orchestrator_model
        self.sub_agent_model = sub_agent_model
        self.refiner_model = refiner_model

    def orchestrate_task(self, objective, file_content=None, previous_results=None, use_search=False):
        """Orchestrates the task breakdown and sub-task generation."""
        previous_results_text = "\n".join(previous_results) if previous_results else "None"

        messages = [
            {"role": "system", "content": "You are a detailed and meticulous assistant... (rest of your system message)"},
            {"role": "user", "content": f"Based on the following objective{' and file content' if file_content else ''}, ... (rest of your user message)"}
        ]

        if use_search:
            messages.append({"role": "user", "content": "Please also generate a JSON object containing a single 'search_query' ... (rest of your search message)"})

        response = completion(model=self.orchestrator_model, messages=messages)
        response_text = response['choices'][0]['message']['content']

        search_query = None
        if use_search:
            search_query = self._extract_search_query(response_text)

        return response_text, file_content, search_query

    def _extract_search_query(self, response_text):
        """Helper method to extract search query from response."""
        json_match = re.search(r'{.*}', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group()
            try:
                return json.loads(json_string)["search_query"]
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}") 
        return None

    def execute_sub_task(self, prompt, search_query=None, previous_gpt_tasks=None, use_search=False, continuation=False):
        """Executes a sub-task using the sub-agent model."""
        if previous_gpt_tasks is None:
            previous_gpt_tasks = []

        continuation_prompt = "Continuing from the previous answer, please complete the response."
        system_message = (
            "You are an expert assistant... (Your system message)"
        )
        if continuation:
            prompt = continuation_prompt

        qna_response = None # Placeholder for future search functionality
        if search_query and use_search:
            print(f"Search query: {search_query}")
            # TODO: Implement actual search functionality

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        if qna_response:
            messages.append({"role": "user", "content": f"\nSearch Results:\n{qna_response}"})

        response = completion(model=self.sub_agent_model, messages=messages)
        response_text = response['choices'][0]['message']['content']

        if len(response_text) >= 4000:
            print("Output may be truncated. Attempting to continue the response.")
            response_text += self.execute_sub_task(
                prompt, search_query, previous_gpt_tasks, use_search, continuation=True
            )

        return response_text

    def refine_output(self, objective, sub_task_results, filename, projectname, continuation=False):
        """Refines the final output using the refiner model."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Objective: " + objective + "\n\nSub-task results:\n" + "\n".join(sub_task_results) + "\n\nPlease review and refine the sub-task results into a cohesive final output... (Rest of your message)"}
                ]
            }
        ]
        response = completion(model=self.refiner_model, messages=messages)
        response_text = response['choices'][0]['message']['content']

        if len(response_text) >= 4000 and not continuation:
            print("Output may be truncated. Attempting to continue the response.")
            response_text += "\n" + self.refine_output(
                objective, sub_task_results + [response_text], filename, projectname, continuation=True
            )
        return response_text