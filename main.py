import json
from ingestion.load_csv import load_csv
from profiling.stats import descriptive_statistics
from profiling.missing_values import missing_value_analysis
from profiling.markdown_writer import generate_markdown_report

DATA_PATH = "data/sample.csv"
OUTPUT_JSON = "output/profiling_report.json"
OUTPUT_MD = "output/profiling_report.md"

def main():
    df = load_csv(DATA_PATH)

    dataset_info = {
        "rows": df.height,
        "columns": df.width,
        "schema": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
    }

    stats = descriptive_statistics(df)
    missing_values = missing_value_analysis(df)

    # Save JSON
    with open(OUTPUT_JSON, "w") as f:
        json.dump(
            {
                "dataset_info": dataset_info,
                "descriptive_statistics": stats,
                "missing_value_analysis": missing_values
            },
            f,
            indent=4
        )

    # Save Markdown
    md_report = generate_markdown_report(dataset_info, stats, missing_values)
    with open(OUTPUT_MD, "w") as f:
        f.write(md_report)

    print("=== PROFILING COMPLETE ===")
    print("JSON report:", OUTPUT_JSON)
    print("Markdown report:", OUTPUT_MD)

if __name__ == "__main__":
    main()