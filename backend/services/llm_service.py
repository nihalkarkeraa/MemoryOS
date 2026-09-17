import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "phi3:mini"


class LLMService:

    def __init__(
        self,
        ollama_url=OLLAMA_URL,
        model_name=MODEL_NAME
    ):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2
    ):
        """
        Send a prompt to the local Ollama model.

        Returns the generated response as a string.

        If Ollama returns an error, the response body is included
        in the exception so that the actual Ollama error can be
        diagnosed.
        """

        if not isinstance(prompt, str):
            raise ValueError(
                "Prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Prompt cannot be empty."
            )

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        try:

            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=300
            )

            # --------------------------------------------------
            # Handle Ollama HTTP errors while preserving
            # Ollama's actual error message.
            # --------------------------------------------------

            if not response.ok:

                try:
                    error_body = response.json()

                except ValueError:
                    error_body = response.text

                raise RuntimeError(
                    "Ollama returned an HTTP error.\n"
                    f"Status code: {response.status_code}\n"
                    f"Response: {error_body}"
                )

        except requests.exceptions.Timeout as error:

            raise RuntimeError(
                "Ollama request timed out after 300 seconds."
            ) from error

        except requests.exceptions.ConnectionError as error:

            raise RuntimeError(
                "Could not connect to Ollama at "
                f"{self.ollama_url}. "
                "Make sure Ollama is running."
            ) from error

        except requests.exceptions.RequestException as error:

            raise RuntimeError(
                f"Failed to communicate with Ollama: {error}"
            ) from error

        # ------------------------------------------------------
        # Parse successful response
        # ------------------------------------------------------

        try:

            result = response.json()

        except ValueError as error:

            raise RuntimeError(
                "Ollama returned an invalid JSON response.\n"
                f"Response: {response.text}"
            ) from error

        generated_response = result.get(
            "response",
            ""
        )

        if not isinstance(
            generated_response,
            str
        ):

            raise RuntimeError(
                "Ollama response field is not a string."
            )

        return generated_response.strip()


llm_service = LLMService()