# -------------------------------------------------------------------
# llm_api.py (UPDATED FOR OPENAI >= 1.0.0)
# Wrapper for calling OpenAI LLMs for CODE4LOGIC
# -------------------------------------------------------------------

import time
import os
from openai import AzureOpenAI # type: ignore
from openai import OpenAI # type: ignore


class LLMClient:
    """
    Wrapper around OpenAI's new Chat Completions API.

    Usage:
        llm = LLMClient(model="gpt-4o-mini")
        output_code = llm.generate_code(prompt_text)
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        # self.client = OpenAI(
        #     api_key= os.getenv("OPENAI_API_KEY")
        # )
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if endpoint and "/openai/" in endpoint:
            endpoint = endpoint.split("/openai/")[0]
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
        )

    # -------------------------------------------------------------------
    # Main call method
    # -------------------------------------------------------------------
    def generate_code(self, prompt: str, max_retries: int = 5) -> str:
        """
        Send a prompt to the LLM and return the generated code.

        Args:
            prompt: Full prompt containing demos + query
            max_retries: Retry attempts on API failure
        """

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(  # NEW
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                )

                return response.choices[0].message.content

            except Exception as e:
                print(f"[LLM API ERROR] Attempt {attempt}/{max_retries}")
                print("Error:", str(e))
                time.sleep(1 + attempt)

        raise RuntimeError("LLM API failed after maximum retries.")

    # -------------------------------------------------------------------
    # Allow direct call: llm(prompt)
    # -------------------------------------------------------------------
    def __call__(self, prompt: str) -> str:
        return self.generate_code(prompt)


# -------------------------------------------------------------------
# Manual test
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Testing updated LLM API...")

    client = LLMClient(model="gpt-4o-mini")

    test_prompt = "Write a simple Python function that prints Hello World."
    output = client.generate_code(test_prompt)

    print("Model Output:\n", output)
