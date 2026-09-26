# AI Data Analysis Agent

An AI-powered data analysis application that allows users to upload CSV datasets and ask questions about their data using natural language. The system uses Google Gemini to generate Pandas analysis code, executes the code on the uploaded dataset, recovers from execution errors when possible, and returns the result with a natural-language explanation and visualization.

## Overview

Traditional data analysis often requires users to know Python, Pandas, and the structure of a dataset before they can extract useful information.

This project provides a simple interface where users can upload a CSV file and ask questions such as:

- Which region has the highest sales?
- What is the average profit?
- Which category generated the most revenue?
- Show total sales by region.
- Show the trend of sales over time.

The agent translates the natural-language question into Python/Pandas code, executes the generated code, and presents the result in a readable form.

The project was built as an educational MVP to explore the use of LLMs in data-analysis workflows and agent-style systems.

---

## Key Features

- Upload and analyze CSV datasets using natural-language questions.
- Generate and execute Pandas analysis code using Gemini.
- Automatically detect and recover from code execution errors.
- Generate natural-language insights and visualizations from analysis results.
- Preview datasets, inspect results, and view generated code through a Streamlit interface.

---

## Working Flow

The complete workflow is:

```text
User uploads CSV
       |
       v
Streamlit application
       |
       v
Pandas loads the dataset
       |
       v
Dataset information is extracted
(rows, columns, data types, missing values)
       |
       v
User asks a natural-language question
       |
       v
Gemini generates Pandas analysis code
       |
       v
Python executes the generated code
       |
       +----------------------+
       |                      |
     Error                  Success
       |                      |
       v                      v
Send error back          Store result
to Gemini                    |
       |                      |
       v                      v
Gemini generates       Generate chart
corrected code          if appropriate
       |                      |
       +----------+-----------+
                  |
                  v
        Gemini explains result
                  |
                  v
          Streamlit displays
          answer and result
```

The system follows an agent-style loop:

```text
Reason -> Act -> Observe -> Correct
```

Gemini determines an analysis approach and generates code. Python executes that code. The execution result is observed, and if an error occurs, the error is sent back to Gemini so it can attempt to correct the generated code.

---

## System Architecture

```text
                         +----------------------+
                         |        User          |
                         |                      |
                         | Upload CSV           |
                         | Ask Question         |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     Streamlit UI     |
                         |       app.py         |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     Agent Logic      |
                         |      agent.py        |
                         +----------+-----------+
                                    |
                     +--------------+--------------+
                     |                             |
                     v                             v
          +----------------------+       +----------------------+
          |   Dataset Analysis   |       |     Gemini API       |
          |     analyzer.py      |       |  Code Generation     |
          +----------+-----------+       +----------+-----------+
                     |                              |
                     |                              v
                     |                    Generated Python Code
                     |                              |
                     +---------------+--------------+
                                     |
                                     v
                           +----------------------+
                           | Python Code Executor |
                           |        exec()        |
                           +----------+-----------+
                                      |
                          +-----------+-----------+
                          |                       |
                          v                       v
                       Success                  Error
                          |                       |
                          |                       v
                          |              Gemini Code Correction
                          |                       |
                          |                       v
                          |                    Retry
                          |                       |
                          +-----------+-----------+
                                      |
                                      v
                              Analysis Result
                                      |
                                      v
                              Gemini Explanation
                                      |
                                      v
                              Streamlit Response
```

---

## Main Components

### 1. Streamlit Interface

`app.py` provides the user interface.

Responsibilities:

- CSV file upload
- Dataset preview
- Dataset statistics
- Natural-language question input
- Analysis button
- Agent answer display
- Analysis result display
- Visualization display
- Generated-code inspection
- User-friendly error messages

The interface is intentionally lightweight so that the project remains focused on the data-analysis agent rather than frontend development.

### 2. Agent Logic

`agent.py` contains the main agent workflow.

The central function is:

```python
analyze_question(df, question)
```

It receives the Pandas DataFrame and the user's natural-language question.

It then:

1. Collects information about the dataset.
2. Sends the question and dataset information to Gemini.
3. Receives generated Pandas code.
4. Executes the generated code.
5. Detects execution errors.
6. Sends errors back to Gemini when correction is required.
7. Retries the corrected code.
8. Sends the successful result to Gemini for explanation.
9. Returns the answer, result, generated code, and visualization.

### 3. Dataset Analysis Engine

`analyzer.py` handles dataset loading and generated-code execution.

The main responsibilities are:

```text
load_data()
get_dataset_info()
execute_analysis()
```

`load_data()` loads the CSV into a Pandas DataFrame.

`get_dataset_info()` provides information such as:

- Number of rows
- Column names
- Data types
- Missing values

`execute_analysis()` executes the generated analysis code and returns a structured response containing:

- Success status
- Analysis result
- Matplotlib figure, when generated
- Error message, when execution fails

### 4. Gemini API

Google Gemini is used for the reasoning and code-generation portions of the application.

The model receives the dataset structure and user question rather than the complete dataset in the prompt.

The generated code operates directly on the DataFrame already loaded by the application.

Gemini is used for three main tasks:

```text
Question
   |
   v
Code generation

Execution error
   |
   v
Code correction

Successful result
   |
   v
Natural-language explanation
```

---

## Error Recovery

One of the main features of the project is automatic recovery from generated-code errors.

LLMs can occasionally generate incorrect code because of:

- Incorrect column names
- Incorrect assumptions about data types
- Invalid Pandas operations
- Incorrect aggregation logic
- Other Python execution errors

Instead of terminating when generated code fails, the application captures the error.

Example:

```python
total_sales_per_region = df.groupby("Region")["Sale"].sum()
```

If the dataset contains `Sales` rather than `Sale`, execution produces an error.

The agent sends the following information back to Gemini:

```text
User question
+
Dataset information
+
Previous generated code
+
Execution error
```

Gemini then generates corrected code:

```python
total_sales_per_region = df.groupby("Region")["Sales"].sum()
```

The corrected code is executed again.

The application currently limits the recovery process to a maximum of three attempts to avoid unnecessary API usage.

---

## Visualization

The agent can generate a Matplotlib visualization when the question involves a comparison, ranking, trend, distribution, or explicitly requests a chart.

For example:

```text
User:
Show total sales by region.
```

Gemini can generate both the analysis result and a chart.

The generated code stores the Matplotlib figure in:

```python
fig
```

The Streamlit application then displays the figure.

For questions where a visualization is not useful, the agent can return:

```python
fig = None
```

This keeps the interface focused on the information requested by the user.

---

## Example Interaction

### Input

```text
Which region has the highest sales?
```

### Generated analysis

The agent may generate code similar to:

```python
region_sales = df.groupby("Region")["Sales"].sum()
result = region_sales.idxmax()
fig = None
```

### Execution

The code is executed against the uploaded DataFrame.

### Result

```text
North
```

### Final response

```text
The North region has the highest sales.
```

For a question requesting a comparison, the application can additionally display the calculated values and a chart.

---

## Project Structure

```text
data-analyst-agent/
|
├── .env
├── agent.py
├── analyzer.py
├── app.py
├── requirements.txt
|
└── data/
    └── sales.csv
```

### File Description

| File | Purpose |
|------|---------|
| `app.py` | Streamlit user interface |
| `agent.py` | Gemini-powered agent workflow |
| `analyzer.py` | Dataset loading, inspection, and code execution |
| `.env` | Stores the Gemini API key |
| `requirements.txt` | Python dependencies |
| `data/sales.csv` | Sample dataset for testing |

---

## Technologies Used

### Python

Main programming language used to build the application and connect all components.

### Pandas

Used for loading CSV files, dataset inspection, data manipulation, aggregation, and statistical analysis.

### Google Gemini API

Used for natural-language understanding, Pandas code generation, code correction, and result explanation.

### Streamlit

Used to build the interactive web interface without requiring a separate frontend framework.

### Matplotlib

Used for generating visualizations from analysis results.

### python-dotenv

Used to load the Gemini API key from the `.env` file.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd data-analyst-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file to GitHub.

Add it to `.gitignore`:

```text
.env
venv/
__pycache__/
```

### 5. Run the application

```bash
streamlit run app.py
```

---

## Requirements

The project currently uses:

```text
pandas
python-dotenv
google-genai
streamlit
matplotlib
```

A `requirements.txt` file should contain these dependencies.

---

## API Usage and Quota

The application relies on the Gemini API, so API usage is subject to the limits of the configured Gemini account and model.

A single user question may require multiple Gemini requests:

```text
1. Generate analysis code
2. Correct code if execution fails
3. Explain the successful result
```

Additional recovery attempts can increase API usage.

The application handles API errors such as rate limits and displays a user-friendly message instead of exposing a full Streamlit traceback.

---

## Security Considerations

This project is an educational MVP and executes LLM-generated Python code using Python's `exec()` function.

This is a significant security limitation.

The generated code is allowed to execute inside the same Python environment as the application. Therefore, this implementation should not be treated as safe for arbitrary untrusted users or production deployment.

A production implementation should isolate generated code in a restricted sandbox or container with:

- Limited filesystem access
- Restricted network access
- Resource limits
- Process isolation
- Execution timeouts
- Restricted Python capabilities
- Strong validation of generated code

---

## Limitations

### 1. CSV-only input

The current application accepts CSV files. It does not currently provide native support for Excel files, JSON files, SQL databases, APIs, PDF documents, or image datasets.

### 2. LLM-generated code can be incorrect

Gemini may generate incorrect or incomplete analysis code. The recovery loop reduces this problem but cannot guarantee that every question will be answered correctly.

### 3. Limited context understanding

The current MVP does not maintain persistent conversation history. Each question is primarily processed as an independent analysis request.

### 4. API dependency

The application depends on the availability and quota of the Gemini API. Rate limits or API failures can prevent analysis from completing.

### 5. Generated code execution

Using `exec()` creates a security risk and is not suitable for a production environment without sandboxing.

### 6. Complex analytical questions

The MVP is designed primarily for common tabular-data analysis tasks. Complex statistical analysis, advanced machine learning, multi-table analysis, or domain-specific reasoning may require additional logic.

### 7. Visualization limitations

The visualization system relies on generated Python code. Poorly generated plotting code can result in an unsuitable or failed visualization.

---

## Future Enhancements

### Support for More Data Sources

Add support for:

- Excel files
- JSON
- SQL databases
- APIs
- Cloud storage
- Multiple uploaded datasets

### Conversational Analysis

Add persistent conversation history so users can ask follow-up questions such as:

```text
User:
Which region has the highest sales?

User:
Why is it higher than the others?

User:
Show me the monthly trend for that region.
```

The agent could use previous questions and results as context.

### Safer Code Execution

Replace direct `exec()` execution with a sandboxed execution environment. This would allow generated code to run with controlled access to resources.

### Advanced Data Cleaning

Automatically detect and handle:

- Missing values
- Duplicate rows
- Incorrect data types
- Outliers
- Invalid dates
- Inconsistent categorical values

### Automated Exploratory Data Analysis

The agent could automatically generate an EDA report containing:

- Dataset summary
- Missing-value analysis
- Descriptive statistics
- Correlations
- Distributions
- Important categorical patterns
- Recommended visualizations

### More Advanced Visualizations

Support automatic generation of:

- Histograms
- Box plots
- Scatter plots
- Heatmaps
- Time-series charts
- Correlation matrices

### Statistical Analysis

Add support for common statistical operations such as:

- Hypothesis testing
- Correlation analysis
- Regression
- Confidence intervals
- ANOVA

### Machine Learning Integration

The agent could eventually support questions such as:

```text
Predict next month's sales.

Which features are most important?

Build a model to predict customer churn.
```

This would extend the project from data analysis into an AI-assisted data science platform.

### Production Deployment

A production version could include:

- User authentication
- Persistent project storage
- Database integration
- Sandboxed execution
- Usage monitoring
- API rate-limit management
- Cloud deployment
- Role-based access

---

## Design Decisions

### Why Streamlit?

Streamlit provides a simple way to build a data-focused application using Python without requiring a separate frontend and backend implementation.

### Why Gemini?

Gemini provides the natural-language reasoning and code-generation capabilities required for the agent workflow.

### Why Pandas?

Pandas is widely used for tabular data analysis and provides a flexible interface for dynamically generated analysis operations.

### Why generate code instead of directly asking Gemini for the answer?

The agent generates executable analysis code so that numerical results are calculated from the actual dataset rather than relying only on the language model to perform the computation.

This separates reasoning from computation:

```text
Gemini
  |
  | Determines how to analyze
  v
Python + Pandas
  |
  | Performs the actual calculation
  v
Result
```

---

## What Makes It an Agent?

The project goes beyond a simple question-answering chatbot.

The agent can:

1. Receive a natural-language goal.
2. Determine an analysis approach.
3. Generate executable code.
4. Execute the code.
5. Observe execution errors.
6. Modify its approach based on the error.
7. Retry the analysis.
8. Interpret the successful result.

This creates the following loop:

```text
Goal
 |
 v
Reason
 |
 v
Act
 |
 v
Observe
 |
 +---- Error ----> Correct ----+
 |                             |
 +--------- Success <----------+
 |
 v
Explain Result
```

This feedback loop is the central agentic component of the project.

---

## Current Scope

The current version intentionally focuses on a small and understandable MVP rather than attempting to build a complete autonomous data-science platform.

The project demonstrates the core concept:

```text
Natural Language
       |
       v
AI-generated Analysis
       |
       v
Executable Python
       |
       v
Error Recovery
       |
       v
Result + Visualization
       |
       v
Natural-language Insight
```

The architecture is designed so that additional capabilities can be added later without replacing the core agent workflow.

---

## Conclusion

The AI Data Analysis Agent demonstrates how a large language model can be combined with traditional Python data-analysis tools to create an interactive, natural-language interface for tabular data.

Instead of requiring users to write Pandas code manually, the system translates their questions into executable analysis, performs the computation on the uploaded dataset, handles common execution failures, and presents the result in a readable form.

The current implementation is intentionally lightweight and educational, while its architecture provides a foundation for future extensions such as conversational analysis, automated EDA, additional data sources, statistical analysis, machine learning, and secure sandboxed execution.
