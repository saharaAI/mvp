# --- src/core_logic/llm_interactions.py ---
import requests
import json
import re

class LLMAgent:
    """Handles interaction with Large Language Models (LLMs) for financial analysis using the Gemini model."""

    def __init__(self, orchestrator_model, executor_model, expert_model, api_key):
        self.orchestrator_model = orchestrator_model
        self.executor_model = executor_model
        self.expert_model = expert_model
        self.api_url = "https://api.gemini.com/v1/completions"  # Replace with the correct Gemini API URL
        self.api_key = api_key

        self.system_messages = {
            "orchestrator": (
                "You are a financial task orchestrator. Your goal is to decompose complex financial objectives "
                "into manageable sub-tasks. Create detailed prompts for other specialized agents to execute these tasks. "
                "Incorporate relevant insights from the 'expert' and validate the outputs provided by the 'executor'."
            ),
            "expert": (
                "You are a financial analyst specializing in balance sheet analysis. Provide comprehensive insights and "
                "interpretations of the balance sheet data, focusing on key trends, risks, and opportunities."
            ),
            "executor": (
                "You are a financial task executor. Accurately perform calculations and provide detailed answers based on "
                "the financial data and instructions given in the prompt."
            )
        }

    def generate_response(self, prompt, model):
        """Generates a response from the LLM based on the agent's role and the given prompt."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "prompt": f"{self.system_messages[model]}\n{prompt}",
            "max_tokens": 500
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            return response_json.get("choices", [{}])[0].get("text", "").strip()
        except requests.RequestException as e:
            print(f"Error with Gemini API: {e}")
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
