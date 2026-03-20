"""
Model configuration and Google Gemini client setup for LexSimple.
All Gemini models are accessed via the Google Generative AI SDK.

The call_gemini() function wraps the Gemini response into an
OpenAI-compatible object so that all existing agent code can keep using
`response.choices[0].message.content` and `msg.tool_calls` unchanged.
"""

import os
import json
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Model name constants
# ---------------------------------------------------------------------------
GEMINI_PRO   = "gemini-2.5-flash"       # Reasoning / heavy tasks
GEMINI_FLASH = "gemini-2.5-flash-lite"  # Fast / lightweight tasks


# ---------------------------------------------------------------------------
# OpenAI-compatible response shim
# ---------------------------------------------------------------------------
class _FunctionCall:
    """Mimics openai.types.FunctionCall."""
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


class _ToolCall:
    """Mimics openai.types.ToolCall."""
    def __init__(self, fn_name: str, fn_args: str):
        self.function = _FunctionCall(fn_name, fn_args)


class _Message:
    """Mimics openai.types.ChatCompletionMessage."""
    def __init__(self, content: str | None, tool_calls: list[_ToolCall] | None):
        self.content = content
        self.tool_calls = tool_calls if tool_calls else None


class _Choice:
    """Mimics openai.types.Choice."""
    def __init__(self, message: _Message):
        self.message = message


class _ChatCompletion:
    """Mimics openai.types.ChatCompletion."""
    def __init__(self, choices: list[_Choice]):
        self.choices = choices


def _wrap_response(gemini_response) -> _ChatCompletion:
    """Convert a Gemini GenerateContentResponse into an OpenAI-shaped object."""
    content = None
    tool_calls: list[_ToolCall] = []

    # Iterate over response parts
    if gemini_response.candidates:
        for part in gemini_response.candidates[0].content.parts:
            if part.function_call:
                fc = part.function_call
                # Convert proto MapComposite to plain dict then JSON string
                args_dict = dict(fc.args) if fc.args else {}
                tool_calls.append(
                    _ToolCall(fc.name, json.dumps(args_dict))
                )
            elif part.text:
                content = (content or "") + part.text

    message = _Message(content=content, tool_calls=tool_calls or None)
    return _ChatCompletion(choices=[_Choice(message=message)])


# ---------------------------------------------------------------------------
# Google GenAI client factory
# ---------------------------------------------------------------------------
def get_client() -> genai.Client:
    """Return a Google GenAI client configured with the API key."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Export it before running: export GEMINI_API_KEY='your-key'"
        )
    return genai.Client(api_key=api_key)


def call_gemini(
    messages: list[dict],
    model: str = GEMINI_PRO,
    tools: list[dict] | None = None,
    json_mode: bool = False,
    temperature: float = 0.3,
) -> _ChatCompletion:
    """
    Convenience wrapper to call a Gemini model via Google GenAI SDK.

    Returns an OpenAI-compatible response object so existing agent code
    can keep using response.choices[0].message.content / .tool_calls.

    Args:
        messages:    Chat messages (system + user + assistant history).
        model:       Which Gemini variant to use.
        tools:       Optional list of OpenAI-format function-calling tool schemas.
        json_mode:   If True, force structured JSON output.
        temperature: Sampling temperature (lower = more deterministic).
    """
    client = get_client()

    # Build config
    config_kwargs: dict = {
        "temperature": temperature,
    }
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    # Convert OpenAI-format tool schemas to Gemini function declarations
    gemini_tools = None
    if tools:
        func_declarations = []
        for tool in tools:
            fn = tool.get("function", {})
            params = fn.get("parameters", {})
            func_declarations.append(types.FunctionDeclaration(
                name=fn.get("name", ""),
                description=fn.get("description", ""),
                parameters=params,
            ))
        gemini_tools = [types.Tool(function_declarations=func_declarations)]
        config_kwargs["tools"] = gemini_tools

    config = types.GenerateContentConfig(**config_kwargs)

    # Convert OpenAI-style messages to Gemini format
    system_instruction = None
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            system_instruction = content
        elif role == "assistant":
            contents.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text=content)]
            ))
        else:
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=content)]
            ))

    if system_instruction:
        config.system_instruction = system_instruction

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return _wrap_response(response)
