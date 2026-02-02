import json
import streamlit as st
import polars as pl
import matplotlib.pyplot as plt
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from profiling.stats import descriptive_statistics
from profiling.missing_values import missing_value_analysis
from profiling.markdown_writer import generate_markdown_report


# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="RAG-based CSV Analyzer",
    layout="wide"
)

st.title("RAG-based CSV Analyzer")
st.write("Upload a CSV file to generate profiling reports.")


# -------------------- Helper Functions --------------------
def plot_missing_values(missing_values):
    cols = list(missing_values.keys())
    values = [v["count"] for v in missing_values.values()]

    fig, ax = plt.subplots()
    ax.bar(cols, values)
    ax.set_title("Missing Values per Column")
    ax.set_ylabel("Missing Count")
    plt.xticks(rotation=45, ha="right")
    return fig


def plot_numeric_distribution(df):
    numeric_cols = [
        col for col, dtype in zip(df.columns, df.dtypes)
        if dtype in (pl.Int64, pl.Float64)
    ]

    if not numeric_cols:
        return None

    fig, ax = plt.subplots()
    df.select(numeric_cols).to_pandas().hist(ax=ax)
    plt.suptitle("Numeric Column Distributions")
    return fig


def generate_pdf_report(md_text, chart_paths):
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(
        temp_pdf.name,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    for line in md_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 20))

    for path in chart_paths:
        story.append(Image(path, width=5 * inch, height=3 * inch))
        story.append(Spacer(1, 20))

    doc.build(story)
    return temp_pdf.name


# -------------------- File Uploader --------------------
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pl.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        st.stop()

    # -------------------- Dataset Info --------------------
    dataset_info = {
        "rows": df.height,
        "columns": df.width,
        "schema": {
            col: str(dtype)
            for col, dtype in zip(df.columns, df.dtypes)
        }
    }

    st.subheader("Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Rows", dataset_info["rows"])
    col2.metric("Columns", dataset_info["columns"])

    st.subheader("Schema")
    st.json(dataset_info["schema"])

    # -------------------- Profiling --------------------
    with st.spinner("Running data profiling..."):
        stats = descriptive_statistics(df)
        missing_values = missing_value_analysis(df)

    st.subheader("Descriptive Statistics")
    st.json(stats)

    st.subheader("Missing Value Analysis")
    st.json(missing_values)

    # -------------------- Markdown Report --------------------
    md_report = generate_markdown_report(
        dataset_info,
        stats,
        missing_values
    )

    st.subheader("Auto-generated Markdown Report")
    st.markdown(md_report)

    # -------------------- Visualizations --------------------
    st.subheader("Data Visualizations")
    chart_paths = []

    fig1 = plot_missing_values(missing_values)
    st.pyplot(fig1)

    tmp1 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig1.savefig(tmp1.name)
    chart_paths.append(tmp1.name)

    fig2 = plot_numeric_distribution(df)
    if fig2:
        st.pyplot(fig2)
        tmp2 = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig2.savefig(tmp2.name)
        chart_paths.append(tmp2.name)

    # -------------------- Downloads --------------------
    report_json = {
        "dataset_info": dataset_info,
        "descriptive_statistics": stats,
        "missing_value_analysis": missing_values
    }

    st.download_button(
        label="⬇️ Download JSON Report",
        data=json.dumps(report_json, indent=4),
        file_name="profiling_report.json",
        mime="application/json"
    )

    st.download_button(
        label="⬇️ Download Markdown Report",
        data=md_report,
        file_name="profiling_report.md",
        mime="text/markdown"
    )

    pdf_path = generate_pdf_report(md_report, chart_paths)
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ Download PDF Report",
            data=f,
            file_name="profiling_report.pdf",
            mime="application/pdf"
        )