# --- src/core_logic/llm_interaction.py ---
import openai
import json
import re

class LLMAgent:
    """Handles interaction with Large Language Models (LLMs) for financial analysis."""

    def __init__(self, orchestrator_model, executor_model, expert_model):
        self.orchestrator_model = orchestrator_model
        self.executor_model = executor_model
        self.expert_model = expert_model
        self.system_messages = {
            "orchestrator": (
                "You are a financial task orchestrator. Your goal is to meticulously break down "
                "complex financial analysis objectives into manageable sub-tasks and craft detailed prompts "
                "for other specialized agents to execute those tasks. Ensure to incorporate insights from the "
                "'expert' and validate the 'executor's' outputs."
            ),
            "expert": (
                "You are a seasoned financial analyst specializing in balance sheet analysis. Your role is to "
                "provide in-depth insights and interpretations of balance sheet data, identifying key trends, "
                "risks, and opportunities."
            ),
            "executor": (
                "You are a meticulous financial task executor. Your primary goal is to accurately perform calculations "
                "and provide specific answers based on the given financial data and the instructions provided in the prompt."
            )
        }

    def generate_response(self, prompt, model):
        """Generates a response from the LLM based on the agent's role and the given prompt."""
        full_prompt = f"{self.system_messages[model]}\n{prompt}"
        try:
            response = openai.Completion.create(
                model=model,
                prompt=full_prompt,
                max_tokens=500
            )
            return response.choices[0].text.strip()
        except openai.error.OpenAIError as e:
            print(f"Error with OpenAI API: {e}")
            return "An error occurred while generating the response."

    def orchestrate_task(self, objective, balance_sheet_data, previous_results=None, use_search=False):
        """Orchestrates the financial analysis task."""
        previous_results_text = "\n".join(previous_results) if previous_results else "None"

        prompt = (
            f"Objective: {objective}\n"
            f"Balance Sheet Data:\n{balance_sheet_data}\n\n"
            f"Previous Sub-task Results:\n{previous_results_text}\n\n"
            "Based on the objective and the balance sheet data, determine the next sub-task "
            "and create a concise and detailed prompt for the 'executor' agent. "
            "Incorporate any relevant insights from previous results."
        )

        if use_search:
            prompt += " If additional information is required, also generate a search query to find it."

        response_text = self.generate_response(prompt, model=self.orchestrator_model)

        search_query = None
        if use_search:
            search_query = self._extract_search_query(response_text)

        return response_text, search_query

    def _extract_search_query(self, response_text):
        """Extracts the search query from the response (if any)."""
        json_match = re.search(r'{.*}', response_text, re.DOTALL)
        if json_match:
            json_string = json_match.group()
            try:
                return json.loads(json_string).get("search_query", None)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
        return None

    def execute_sub_task(self, prompt, balance_sheet_data, search_results=None):
        """Executes a sub-task related to financial analysis."""
        if search_results:
            prompt = f"{prompt}\n\nSearch Results:\n{search_results}"
        
        prompt = f"{prompt}\n\nUse the provided Balance Sheet Data:\n{balance_sheet_data}\n\n"

        return self.generate_response(prompt, model=self.executor_model) 

    def provide_expert_insights(self, balance_sheet_data):
        """Generates expert insights based on the balance sheet data."""
        prompt = f"Analyze the following balance sheet data and provide your expert insights:\n{balance_sheet_data}"
        return self.generate_response(prompt, model=self.expert_model)