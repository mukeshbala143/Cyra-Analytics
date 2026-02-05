import os
import json

from flask import Flask, render_template, request, send_file
import polars as pl
import matplotlib
matplotlib.use("Agg")   # 🔥 VERY IMPORTANT (prevents server crash)
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from profiling.stats import descriptive_statistics
from profiling.missing_values import missing_value_analysis
from profiling.markdown_writer import generate_markdown_report


app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

UPLOAD_DIR = "data"
OUTPUT_DIR = "output"
PLOT_DIR = os.path.join("frontend", "static", "plots")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)


# -------------------- Helper Functions --------------------
def plot_missing_values(missing_values):
    cols = list(missing_values.keys())
    values = [
        v.get("count", 0) if isinstance(v, dict) else v
        for v in missing_values.values()
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(cols, values)
    ax.set_title("Missing Values per Column")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    path = os.path.join(PLOT_DIR, "missing_values.png")
    fig.savefig(path)
    plt.close(fig)

    return "/static/plots/missing_values.png"


def plot_numeric_distributions(df):
    paths = []
    numeric_cols = [
        col for col, dtype in zip(df.columns, df.dtypes)
        if dtype in (pl.Int64, pl.Int32, pl.Float64, pl.Float32)
    ]

    for col in numeric_cols:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df[col].drop_nulls().to_list(), bins=20)
        ax.set_title(f"Distribution of {col}")
        fig.tight_layout()

        filename = f"{col}_dist.png"
        full_path = os.path.join(PLOT_DIR, filename)
        fig.savefig(full_path)
        plt.close(fig)

        paths.append(f"/static/plots/{filename}")

    return paths


def generate_pdf_report(md_text, chart_paths):
    pdf_path = os.path.join(OUTPUT_DIR, "profiling_report.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
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
            safe = (
                line.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
            )
            story.append(Paragraph(safe, styles["Normal"]))
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 20))

    for img in chart_paths:
        img_path = os.path.join("frontend", img.lstrip("/"))
        story.append(Image(img_path, width=5 * inch, height=3 * inch))
        story.append(Spacer(1, 20))

    doc.build(story)
    return pdf_path


# -------------------- Routes --------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return render_template("error.html", message="No file uploaded")

    csv_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(csv_path)

    df = pl.read_csv(csv_path)

    dataset_info = {
        "rows": df.height,
        "columns": df.width,
        "schema": {c: str(t) for c, t in zip(df.columns, df.dtypes)}
    }

    stats = descriptive_statistics(df)
    missing = missing_value_analysis(df)
    markdown = generate_markdown_report(dataset_info, stats, missing)

    charts = []
    charts.append(plot_missing_values(missing))
    charts.extend(plot_numeric_distributions(df))

    json_path = os.path.join(OUTPUT_DIR, "profiling_report.json")
    with open(json_path, "w") as f:
        json.dump({
            "dataset_info": dataset_info,
            "descriptive_statistics": stats,
            "missing_value_analysis": missing
        }, f, indent=4)

    md_path = os.path.join(OUTPUT_DIR, "profiling_report.md")
    with open(md_path, "w") as f:
        f.write(markdown)

    pdf_path = generate_pdf_report(markdown, charts)

    return render_template(
        "result.html",
        dataset_info=dataset_info,
        markdown=markdown,
        charts=charts,
        json_path=json_path,
        md_path=md_path,
        pdf_path=pdf_path
    )


@app.route("/download")
def download():
    path = request.args.get("path")
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    # 🔥 PORT 5002 + NO DEBUG + NO RELOADER
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=False,
        use_reloader=False
    )
