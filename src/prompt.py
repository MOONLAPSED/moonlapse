import dataclasses
import logging
from openai import OpenAI
import os
import json
from pathlib import Path


base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
api_key = os.getenv("OPENAI_API_KEY")

# Validate API key (optional)
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(base_url=base_url, api_key=api_key)

@dataclasses.dataclass
class Prompt:
    prompt: str
    temperature: float = 0.3
    model: str = "nomic-ai/nomic-embed-text-v1.5-GGUF"
    output_dir: Path = Path.cwd().parent  # Default output directory is the parent directory

    def __post_init__(self):
        self.embedding = self.get_embedding(self.prompt, self.model)

    def get_embedding(self, text, model):
        try:
            text = text.replace("\n", " ")
            response = client.embeddings.create(input=[text], model=model)
            if response and response.data and response.data[0].embedding:
                return response.data[0].embedding
            else:
                raise ValueError("Failed to get embedding")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return None

    def generate_response(self, output_path: Path = None):
        try:
            messages = [{"role": "system", "content": "always answer thoughtfully."},
                        {"role": "user", "content": self.prompt}]
            completion = client.chat.completions.create(
                model="cognitivecomputations/dolphin-2.9-llama3-8b-gguf",
                messages=messages,
                temperature=self.temperature,
            )
            response = completion.choices[0].message.content

            # Save the response as a JSON file
            output_file = output_path or self.output_dir / f"{self.prompt[:20]}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({"prompt": self.prompt, "response": response}, f, indent=2)
            logging.info(f"Response saved to {output_file}")

            return response
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise e

    def __str__(self):
        return self.prompt