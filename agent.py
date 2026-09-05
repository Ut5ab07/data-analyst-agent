from google import genai
from dotenv import load_dotenv
import os

from analyzer import load_data, get_dataset_info, execute_analysis


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


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
- Do not use print().
- Do not use markdown.
- Do not include ```python.
- Do not explain the code.
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    code = interaction.output_text.strip()

    # Error recovery loop
    MAX_ATTEMPTS = 3

    for attempt in range(1, MAX_ATTEMPTS + 1):

        execution = execute_analysis(df, code)

        if execution["success"]:

            result = execution["result"]

            break

        # If this was the final attempt
        if attempt == MAX_ATTEMPTS:

            return {
                "success": False,
                "answer": "The agent could not complete the analysis.",
                "code": code,
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
- Store the final answer in a variable called `result`.
- Return ONLY the corrected Python code.
- Do not use print().
- Do not include markdown.
- Do not include ```python.
- Do not explain anything.
"""

        correction = client.interactions.create(
            model="gemini-3.6-flash",
            input=correction_prompt
        )

        code = correction.output_text.strip()

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

    explanation = client.interactions.create(
        model="gemini-3.6-flash",
        input=explanation_prompt
    )

    return {
        "success": True,
        "answer": explanation.output_text,
        "result": result,
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