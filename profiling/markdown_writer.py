def generate_markdown_report(dataset_info, stats, missing_values) -> str:
    """
    Generates a human-readable Markdown profiling report.
    """
    md = []

    md.append("# Dataset Profiling Report")
    md.append("")

    # Dataset Info
    md.append("## Dataset Overview")
    md.append("")
    md.append(f"- **Rows:** {dataset_info['rows']}")
    md.append(f"- **Columns:** {dataset_info['columns']}")
    md.append("")

    md.append("### Schema")
    md.append("")
    for col, dtype in dataset_info["schema"].items():
        md.append(f"- `{col}` : {dtype}")
    md.append("")

    # Descriptive Statistics
    md.append("## Descriptive Statistics")
    md.append("")
    if not stats:
        md.append("_No numeric columns found._")
        md.append("")
    else:
        for col, values in stats.items():
            md.append(f"### `{col}`")
            md.append("")  # blank line after column heading

            for k, v in values.items():
                md.append(
                    f"- **{k.capitalize()}**: {round(v, 4) if v is not None else 'N/A'}"
                )

            md.append("")

    # Missing Values
    md.append("## Missing Value Analysis")
    md.append("")
    for col, info in missing_values.items():
        md.append(
            f"- `{col}`: {info['missing_count']} missing "
            f"({info['missing_percentage']:.2f}%)"
        )
        md.append("")  # blank line after each entry

    return "\n".join(md)