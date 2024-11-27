import google.generativeai as genai
import json

class GeminiThingamie:
    """
    Handles interaction with the Gemini API to process transcriptions and evaluate hooks.
    """

    def __init__(self, base_transcription: str, model_name="gemini-1.5-flash-latest"):
        """
        Initializes the GeminiThingamie.

        Args:
            model_name (str): The name of the Gemini model to use.
        """
        self.model_name = model_name
        self.base_transcription = base_transcription
    
    def set_base_transcription(self, base_transcription : str):
        self.base_transcription = base_transcription

    def process_transcription(self, transcription: str, hooks: dict):
        """
        Processes the transcription using Gemini and evaluates hooks.

        Args:
            transcription (str): The transcription text to process.
            hooks (dict): A dictionary of registered hooks.
        """
        schema_properties = {
            name: {
                "type": "object",
                "properties": {
                    "invoked": {"type": "boolean", "description": hook["description"]},
                    **hook.get("schema", {}),
                },
                "required": ["invoked"],
            }
            for name, hook in hooks.items()
        }

        schema = {
            "description": "Hook invocation status and response formats.",
            "type": "object",
            "properties": schema_properties,
            "required": list(hooks.keys()),
        }

        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                f"{self.base_transcription} {transcription}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            print(f"GeminiThingamie Response: {response}")

            for hook_name, hook_result in json.loads(response.text).items():
                if hook_result.get("invoked", False):
                    print(f"Hook '{hook_name}' was invoked. Executing callback.")
                    hooks[hook_name]["callback"](hook_result)
        except Exception as e:
            print(f"Error invoking GeminiThingamie: {e}")
