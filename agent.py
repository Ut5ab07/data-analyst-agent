from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
import os
import re

from analyzer import load_data, get_dataset_info, execute_analysis


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def _retry_hint(error):
    """Extract a retry duration from an SDK error when one is provided."""
    message = str(error)
    match = re.search(r"(?:retry(?:[- ]after| in)|try again in)\s*([0-9]+(?:\.[0-9]+)?)\s*s", message, re.IGNORECASE)
    if match:
        return f" The API suggests waiting about {match.group(1)} seconds."
    return ""


def _gemini_error_message(error):
    """Convert an SDK or connection error into a short user-facing message."""
    status_code = getattr(error, "code", None) or getattr(error, "status_code", None)
    error_text = str(error).lower()

    if status_code == 429 or "429" in error_text or "rate limit" in error_text or "quota" in error_text:
        return "Gemini API limit reached. Please wait a little and try again." + _retry_hint(error)

    if isinstance(error, (ConnectionError, TimeoutError)) or "connection" in error_text or "timeout" in error_text:
        return "Could not connect to Gemini. Check your internet connection and try again."

    if isinstance(error, genai_errors.APIError):
        return "Gemini API request failed. Please try again."

    return "The Gemini request failed. Please try again."


def _request_gemini(prompt):
    """Make one Gemini request without retrying failed API calls automatically."""
    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )
        return {
            "success": True,
            "text": interaction.output_text.strip(),
            "error": None
        }
    except Exception as error:
        return {
            "success": False,
            "text": None,
            "error": _gemini_error_message(error)
        }


def analyze_question(df, question):
    """
    Analyze a user's question using Gemini and Pandas.
    Includes automatic error recovery.
    """

    # Get dataset information
    info = get_dataset_info(df)

    # Ask Gemini to generate analysis code
    prompt = f"""
You are a Python data analysis agent.

You are working with a Pandas DataFrame called `df`.

Here is information about the dataset:

{info}

The user asks:

{question}

Generate ONLY the Python code required to answer the user's question.

Rules:
- Use Pandas.
- The DataFrame is already available as `df`.
- Store the final answer in a variable called `result`.
- `pd` and `plt` are already available.
- If the question involves a comparison, ranking, distribution, trend, or explicitly asks for a chart/plot, create an appropriate visualization using Matplotlib.
- Store the Matplotlib figure in a variable called `fig`.
- If a visualization is not useful or not requested, set `fig = None`.
- Do not use plt.show().
- Do not use print().
- Do not use markdown.
- Do not include ```python.
- Do not explain the code.
"""

    generation = _request_gemini(prompt)
    if not generation["success"]:
        return {
            "success": False,
            "answer": generation["error"],
            "code": "",
            "error": generation["error"]
        }

    code = generation["text"]

    # Error recovery loop
    MAX_ATTEMPTS = 3

    for attempt in range(1, MAX_ATTEMPTS + 1):

        execution = execute_analysis(df, code)

        if execution["success"]:

            result = execution["result"]
            figure = execution["figure"]

            break

        # If this was the final attempt
        if attempt == MAX_ATTEMPTS:

            return {
                "success": False,
                "answer": "The agent could not complete the analysis.",
                "code": code,
                "figure": None,
                "error": execution["error"]
            }

        # Ask Gemini to fix the code
        correction_prompt = f"""
You are debugging Python Pandas code.

User question:

{question}

Dataset information:

{info}

Previous code:

{code}

The code produced this error:

{execution["error"]}

Fix the code so that it correctly answers the user's question.

Rules:
- Use Pandas.
- The DataFrame is available as `df`.
- `pd` and `plt` are already available.
- Store the final answer in a variable called `result`.
- If the original question requires or benefits from a visualization, create it and store it in `fig`.
- Otherwise set `fig = None`.
- Do not use plt.show().
- Return ONLY the corrected Python code.
- Do not use print().
- Do not include markdown.
- Do not include ```python.
- Do not explain anything.
"""

        correction = _request_gemini(correction_prompt)
        if not correction["success"]:
            return {
                "success": False,
                "answer": correction["error"],
                "code": code,
                "error": correction["error"]
            }

        code = correction["text"]

    # Ask Gemini to explain the result
    explanation_prompt = f"""
You are a data analysis assistant.

The user asked:

{question}

The Python analysis produced this result:

{result}

Explain the result clearly and concisely.

Rules:
- Directly answer the user's question.
- Include important numbers.
- Do not mention Python or Pandas.
- Do not explain the code.
- Do not make claims that are not supported by the result.
"""

    explanation = _request_gemini(explanation_prompt)
    if not explanation["success"]:
        return {
            "success": True,
            "answer": "The analysis completed, but Gemini could not generate an explanation.",
            "result": result,
            "code": code,
            "api_error": explanation["error"]
        }

    return {
        "success": True,
        "answer": explanation["text"],
        "result": result,
        "figure": figure,
        "code": code
    }


# Terminal testing
if __name__ == "__main__":

    df = load_data("data/sales.csv")

    print("Dataset loaded successfully!")

    print("\nDataset information:")
    print(get_dataset_info(df))

    question = input("\nWhat would you like to know about the dataset? ")

    response = analyze_question(df, question)

    print("\nAgent answer:")
    print(response["answer"])