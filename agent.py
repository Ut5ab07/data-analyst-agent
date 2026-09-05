from google import genai
from dotenv import load_dotenv
import os

from analyzer import load_data, get_dataset_info, execute_analysis

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# Loading The Dataset

df=load_data("data/sales.csv")
print("Dataset loaded successfully!")

#Getting Dataset Information

info = get_dataset_info(df)

print("\nDataset information:")
print(info)


#Getting User question

question = input("\n What would you like to know about the dataset?:")

#Asking Gemini to generate code 

prompt = f"""
You are a Python data analyst agemt.
You are working with a Pandas DataFrame called `df`
Here is information about the dataset:
{info}

The user askes: 
{question}

Generate only the python code required to answer the user's question.
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
    input=prompt,
)

code = interaction.output_text.strip()

#Error Recovery Loop

MAX_ATTEMPT = 3

for attempt in range(1, MAX_ATTEMPT + 1):

    print(f"\n Attempt {attempt}")
    print("Generated code:")
    print(code)

    execution = execute_analysis(df, code)

    # Success
    if execution["success"]:
        result = execution["result"]

        print("\nAnalysis Result:")
        print(result)

        break

    #Error 
    print("\nExecution Error:")
    print(execution["error"])

    if attempt == MAX_ATTEMPT:
        print("\n The agent could not complete the analysis.")

        break

    # Asking Gemini to fix the code
    correction_prompt = f"""
You are debuggin Python Pandas code.
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
- Do not explain anything
"""


    correction = client.interactions.create(
        model="gemini-3.6-flash",
        input=correction_prompt
    )

    code = correction.output_text.strip()


# -----------------------------
# Generate final explanation
# -----------------------------

if execution["success"]:

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

    print("\nAgent answer:")
    print(explanation.output_text)