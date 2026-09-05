import html

import streamlit as st
import pandas as pd

from analyzer import get_dataset_info
from agent import analyze_question


# Page configuration
st.set_page_config(
    page_title="Data Analysis Agent",
    layout="wide"
)


# Title
st.title("Data Analysis Agent")

st.write(
    "Upload a CSV file and ask questions about your data "
    "using natural language."
)

st.markdown(
    """
    <style>
    .status-line {
        margin: 0.75rem 0 1.25rem;
        padding-left: 0.75rem;
        border-left: 2px solid #31c48d;
        color: #8be8bd;
        font-size: 0.9rem;
    }

    .status-line.error {
        border-left-color: #ff6b6b;
        color: #ff9b9b;
    }

    .status-line.neutral {
        border-left-color: #8a94a6;
        color: #aeb7c6;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# File upload
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


if uploaded_file is not None:

    # Load dataset
    df = pd.read_csv(uploaded_file)

    st.markdown(
        "<div class='status-line'>Dataset loaded</div>",
        unsafe_allow_html=True
    )

    # Dataset information
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", len(df))

    with col2:
        st.metric("Columns", len(df.columns))

    with col3:
        st.metric(
            "Missing Values",
            int(df.isnull().sum().sum())
        )

    # Dataset preview
    st.subheader("Data Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    # Question input
    st.subheader("Ask a Question")

    question = st.text_input(
        "What would you like to know about the dataset?",
        placeholder="Example: Which region has the highest sales?"
    )

    # Analyze button
    if st.button("Analyze"):

        if question.strip() == "":
            st.markdown(
                "<div class='status-line neutral'>"
                "Please enter a question."
                "</div>",
                unsafe_allow_html=True
            )

        else:

            with st.spinner("Analyzing your data..."):

                response = analyze_question(
                    df,
                    question
                )

        
           # Display result
            if response["success"]:

                if response.get("api_error"):
                    st.markdown(
                        "<div class='status-line error'>"
                        f"{html.escape(response['api_error'])}"
                        "</div>",
                        unsafe_allow_html=True
                    )

                st.subheader("Agent Answer")

                st.write(response["answer"])

                # Show analysis result directly
                st.subheader("Analysis Result")

                st.write(response["result"])

                # Generated code stays inside dropdown
                with st.expander("View Generated Code"):
                    st.code(
                        response["code"],
                        language="python"
                    )

            else:

                st.markdown(
                    "<div class='status-line error'>"
                    f"{html.escape(response['answer'])}"
                    "</div>",
                    unsafe_allow_html=True
                )

                with st.expander("Error Details"):
                    st.write(response["error"])

else:

    st.markdown(
        "<div class='status-line neutral'>"
        "Upload a CSV file to get started."
        "</div>",
        unsafe_allow_html=True
    )