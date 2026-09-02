from google import genai
from dotenv import load_dotenv
import os

from analyzer import load_data, get_dataset_info, execute_analysis

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))

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

#Displaying the generated code

print("\nGenerated code:")
print(code)

#Executing the generated code

result = execute_analysis(df, code)

#Asking gemini to explain the result

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