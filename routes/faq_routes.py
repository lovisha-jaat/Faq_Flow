import os
import sqlite3
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.utils import secure_filename

from services.ai_service import (
    create_knowledge_table,
    invalidate_company_model,
    train_company_model
)
from services.file_service import (
    allowed_file,
    process_uploaded_file
)
from services.website_service import (
    scrape_website
)
from utils.decorators import login_required


faq_bp = Blueprint(
    "faq",
    __name__,
    url_prefix="/knowledge"
)


def database_path():
    return current_app.config.get(
        "DATABASE",
        os.path.join(
            current_app.root_path,
            "database",
            "faqflow.db"
        )
    )


def save_chunks(
    company_id,
    chunks,
    replace=False
):
    create_knowledge_table()

    connection = sqlite3.connect(
        database_path()
    )

    cursor = connection.cursor()

    try:
        if replace:
            cursor.execute(
                """
                DELETE FROM knowledge_chunks
                WHERE company_id = ?
                """,
                (company_id,)
            )

        for chunk in chunks:
            cursor.execute(
                """
                INSERT INTO knowledge_chunks (
                    company_id,
                    content,
                    source_name,
                    source_type,
                    source_url,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    chunk["content"],
                    chunk.get("source_name"),
                    chunk.get("source_type"),
                    chunk.get("source_url"),
                    chunk.get("metadata")
                )
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


@faq_bp.route("/")
@login_required
def faq_list():
    company_id = session.get(
        "company_id"
    )

    create_knowledge_table()

    connection = sqlite3.connect(
        database_path()
    )

    connection.row_factory = sqlite3.Row

    chunks = connection.execute(
        """
        SELECT *
        FROM knowledge_chunks
        WHERE company_id = ?
        ORDER BY id DESC
        """,
        (company_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "faqs/faq_list.html",
        faqs=chunks
    )


@faq_bp.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload_data():
    if request.method == "GET":
        return render_template(
            "faqs/upload_data.html"
        )

    company_id = session.get(
        "company_id"
    )

    uploaded_file = request.files.get(
        "knowledge_file"
    )

    if (
        not uploaded_file or
        uploaded_file.filename == ""
    ):
        flash(
            "Please choose a CSV, Excel or TXT file.",
            "danger"
        )

        return redirect(
            url_for("faq.upload_data")
        )

    if not allowed_file(
        uploaded_file.filename
    ):
        flash(
            "Only CSV, Excel and TXT files are supported.",
            "danger"
        )

        return redirect(
            url_for("faq.upload_data")
        )

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4().hex}_"
        f"{secure_filename(uploaded_file.filename)}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    uploaded_file.save(file_path)

    try:
        chunks = process_uploaded_file(
            file_path
        )

        replace = (
            request.form.get(
                "upload_mode"
            ) == "replace"
        )

        save_chunks(
            company_id,
            chunks,
            replace=replace
        )

        invalidate_company_model(
            company_id
        )

        train_company_model(
            company_id
        )

        flash(
            (
                f"{len(chunks)} knowledge chunks were "
                "imported successfully."
            ),
            "success"
        )

    except Exception as error:
        current_app.logger.exception(
            "File import failed"
        )

        flash(
            str(error),
            "danger"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return redirect(
        url_for("faq.upload_data")
    )


@faq_bp.route(
    "/website",
    methods=["POST"]
)
@login_required
def import_website():
    company_id = session.get(
        "company_id"
    )

    website_url = request.form.get(
        "website_url",
        ""
    ).strip()

    if not website_url:
        flash(
            "Please enter a website URL.",
            "danger"
        )

        return redirect(
            url_for("faq.upload_data")
        )

    try:
        chunks = scrape_website(
            website_url,
            max_pages=10
        )

        save_chunks(
            company_id,
            chunks,
            replace=False
        )

        invalidate_company_model(
            company_id
        )

        train_company_model(
            company_id
        )

        flash(
            (
                f"{len(chunks)} website knowledge "
                "chunks were imported."
            ),
            "success"
        )

    except Exception as error:
        current_app.logger.exception(
            "Website import failed"
        )

        flash(
            str(error),
            "danger"
        )

    return redirect(
        url_for("faq.upload_data")
    )