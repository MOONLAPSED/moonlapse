# Make sure to `pip install openai` first
from openai import OpenAI
import openai
import logging
import os

# Load configuration from environment variables (recommended for production)
base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:1234/v1")
api_key = os.getenv("OPENAI_API_KEY")

# Validate API key (optional)
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(base_url=base_url, api_key=api_key)


def get_embedding(text, model="nomic-ai/nomic-embed-text-v1.5-GGUF"):
    """
    Retrieves embedding for a given text using the OpenAI API.

    Args:
        text (str): The text to get the embedding for.
        model (str, optional): The OpenAI model to use for embedding creation. Defaults to "nomic-ai/nomic-embed-text-v1.5-GGUF".

    Returns:
        list: A list containing the embedding vector.

    Raises:
        Exception: If an error occurs during the API call or data processing.
    """

    try:
        text = text.replace("\n", " ")
        response = client.embeddings.create(input=[text], model=model)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        return response.data[0].embedding
    except Exception as e:
        # Log the error with details
        logging.error(f"Error retrieving embedding: {e}")
        raise

def generate_response(prompt_obj="cwd:/cognosis-t=0-prompt:custom|", temperature=0.3):
    """
    Generates a response for a given prompt using the OpenAI API.

    Args:
        prompt_obj (str): The prompt to generate the response for.
        temperature (float, optional): The temperature to use for the response generation. Defaults to 0.3.

    Returns:
        str: The generated response.

    Raises:
        Exception: If an error occurs during the API call or data processing.
    """
    try:
        completion = client.chat.completions.create(
            model="cognitivecomputations/dolphin-2.9-llama3-8b-gguf",
            messages=[{"role": "system", "content": "always answer thoughtfully."}],
            #prompt=prompt_obj,
            temperature=temperature,
        )
        # Assuming response.choices[0].message holds the generated text content
        return completion.choices[0].message
    except Exception as e:
        # Log the error with details
        logging.error(f"Error generating response: {e}")
        raise

if __name__ == "__main__":
    print(generate_response())
