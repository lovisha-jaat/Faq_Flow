import os
import re

import pandas as pd


ALLOWED_EXTENSIONS = {
    "csv",
    "xlsx",
    "xls",
    "txt"
}


def allowed_file(filename):
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def clean_value(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def dataframe_to_chunks(dataframe, source_name):
    """
    Convert every CSV/Excel row into searchable text.

    Example row:

    Product = Laptop
    Price = 50000
    Warranty = 2 years

    becomes one knowledge chunk.
    """

    if dataframe.empty:
        raise ValueError("The uploaded file is empty.")

    dataframe.columns = [
        str(column).strip()
        for column in dataframe.columns
    ]

    chunks = []

    for row_index, row in dataframe.iterrows():
        row_parts = []

        for column in dataframe.columns:
            value = clean_value(row.get(column))

            if value:
                row_parts.append(
                    f"{column}: {value}"
                )

        if not row_parts:
            continue

        row_text = "\n".join(row_parts)

        chunks.append({
            "content": row_text,
            "source_name": source_name,
            "source_type": "file",
            "metadata": (
                f"Row {row_index + 2}"
            )
        })

    if not chunks:
        raise ValueError(
            "No usable information was found in the file."
        )

    return chunks


def read_csv(file_path):
    try:
        return pd.read_csv(
            file_path,
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        return pd.read_csv(
            file_path,
            encoding="latin-1"
        )


def read_excel(file_path):
    return pd.read_excel(file_path)


def split_text_into_chunks(
    text,
    source_name,
    chunk_size=1200
):
    """
    Split TXT or website text into smaller knowledge chunks.
    """

    text = re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()

    if not text:
        return []

    chunks = []

    start = 0
    chunk_number = 1

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            sentence_end = text.rfind(
                ".",
                start,
                end
            )

            if sentence_end > start + 300:
                end = sentence_end + 1

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "content": chunk_text,
                "source_name": source_name,
                "source_type": "text",
                "metadata": (
                    f"Chunk {chunk_number}"
                )
            })

            chunk_number += 1

        start = end

    return chunks


def read_txt(file_path):
    try:
        with open(
            file_path,
            "r",
            encoding="utf-8-sig"
        ) as file:
            text = file.read()

    except UnicodeDecodeError:
        with open(
            file_path,
            "r",
            encoding="latin-1"
        ) as file:
            text = file.read()

    return text


def process_uploaded_file(file_path):
    extension = (
        os.path.splitext(file_path)[1]
        .lower()
        .replace(".", "")
    )

    source_name = os.path.basename(file_path)

    if extension == "csv":
        dataframe = read_csv(file_path)

        return dataframe_to_chunks(
            dataframe,
            source_name
        )

    if extension in {"xlsx", "xls"}:
        dataframe = read_excel(file_path)

        return dataframe_to_chunks(
            dataframe,
            source_name
        )

    if extension == "txt":
        text = read_txt(file_path)

        chunks = split_text_into_chunks(
            text,
            source_name
        )

        if not chunks:
            raise ValueError(
                "The TXT file does not contain usable text."
            )

        return chunks

    raise ValueError(
        "Only CSV, Excel and TXT files are supported."
    )