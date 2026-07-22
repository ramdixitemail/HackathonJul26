import ollama

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)


class OllamaClient:

    def __init__(self):

        self.client = ollama.Client(
            host=OLLAMA_BASE_URL
        )

        self.model = OLLAMA_MODEL

    def generate(self, prompt):
        print("\n" + "=" * 80)
        print("PROMPT SENT TO OLLAMA")
        print("=" * 80)
        print(prompt)
        print("=" * 80)

        response = self.client.chat(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )

        return response["message"]["content"]