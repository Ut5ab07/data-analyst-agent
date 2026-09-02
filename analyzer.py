import pandas as pd

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

def get_dataset_info(df):
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict()
    }

def execute_analysis(df, code):
    local_variables = {
        "df": df,
        "pd": pd
    }

    exec(code, {}, local_variables)

    return local_variables.get("result")


if __name__ == "__main__":

    df = load_data("data/sales.csv")

    print("DATASET")
    print(df)

    info = get_dataset_info(df)

    print("\nDataset Information:")
    print(info)

    code = """
result = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
"""
    result = execute_analysis(df, code)

    print("\nAnalysis Result:")
    print(result)