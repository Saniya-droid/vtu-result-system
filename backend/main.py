from fastapi import FastAPI, UploadFile
import pdfplumber
import re
import psycopg2

app = FastAPI()

# =========================
# DATABASE CONNECTION
# =========================

conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_4Ht0WiOuEKIy@ep-muddy-hill-a1uquy4c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# =========================
# CREATE TABLES
# =========================

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    usn VARCHAR PRIMARY KEY,
    name VARCHAR
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    usn VARCHAR,
    subject_code VARCHAR,
    subject_name VARCHAR,
    internal_marks INT,
    external_marks INT,
    total_marks INT,
    result VARCHAR
);
""")

conn.commit()
cur.close()

# =========================
# HOME ROUTE
# =========================

@app.get("/")
def home():
    return {"message": "Backend Working"}

# =========================
# CLEAR DATABASE ROUTE
# =========================

@app.delete("/clear-results")
def clear_results():

    cur = conn.cursor()

    cur.execute("DELETE FROM results")
    cur.execute("DELETE FROM students")

    conn.commit()

    cur.close()

    return {
        "message": "Database Cleared Successfully"
    }

# =========================
# PDF UPLOAD ROUTE
# =========================

@app.post("/upload-result")
async def upload_result(file: UploadFile):

    cur = conn.cursor()

    text = ""

    with pdfplumber.open(file.file) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    # =========================
    # EXTRACT STUDENT DETAILS
    # =========================

    usn_match = re.search(
        r'University Seat Number\s*:\s*(\S+)',
        text
    )

    name_match = re.search(
        r'Student Name\s*:\s*(.+)',
        text
    )

    if not usn_match or not name_match:

        cur.close()

        return {
            "error": "Could not extract student details"
        }

    usn = usn_match.group(1).strip()

    name = name_match.group(1).strip()

    # =========================
    # EXTRACT SUBJECTS
    # =========================

    subjects = []

    lines = text.split("\n")

    for line in lines:

        parts = line.strip().split()

        if (
            len(parts) >= 6 and
            parts[0].startswith(
                ("BCS", "BCSL", "BSCK", "BYOK", "BME")
            )
        ):

            try:

                subject_code = parts[0]

                result = parts[-2]

                total_marks = int(parts[-3])

                external_marks = int(parts[-4])

                internal_marks = int(parts[-5])

                subject_name = " ".join(parts[1:-5])

                subjects.append({
                    "subject_code": subject_code,
                    "subject_name": subject_name,
                    "internal_marks": internal_marks,
                    "external_marks": external_marks,
                    "total_marks": total_marks,
                    "result": result
                })

            except:
                continue

    # =========================
    # REMOVE DUPLICATES
    # =========================

    unique_subjects = {}

    for subject in subjects:
        unique_subjects[
            subject["subject_code"]
        ] = subject

    subjects = list(unique_subjects.values())

    # =========================
    # INSERT STUDENT
    # =========================

    cur.execute(
        """
        INSERT INTO students (usn, name)
        VALUES (%s, %s)
        ON CONFLICT (usn)
        DO NOTHING
        """,
        (usn, name)
    )

    # =========================
    # DELETE OLD RESULTS
    # =========================

    cur.execute(
        """
        DELETE FROM results
        WHERE usn = %s
        """,
        (usn,)
    )

    # =========================
    # INSERT SUBJECTS
    # =========================

    for subject in subjects:

        cur.execute(
            """
            INSERT INTO results
            (
                usn,
                subject_code,
                subject_name,
                internal_marks,
                external_marks,
                total_marks,
                result
            )

            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                usn,
                subject["subject_code"],
                subject["subject_name"],
                subject["internal_marks"],
                subject["external_marks"],
                subject["total_marks"],
                subject["result"]
            )
        )

    conn.commit()

    cur.close()

    return {
        "message": "Result Uploaded Successfully",
        "usn": usn,
        "name": name,
        "subjects": subjects
    }

# =========================
# GET RESULT ROUTE
# =========================

@app.get("/get-result/{usn}")
def get_result(usn: str):

    cur = conn.cursor()

    cur.execute(
        """
        SELECT usn, name
        FROM students
        WHERE usn = %s
        """,
        (usn,)
    )

    student = cur.fetchone()

    if not student:

        cur.close()

        return {
            "error": "Student not found"
        }

    cur.execute(
        """
        SELECT
            subject_code,
            subject_name,
            internal_marks,
            external_marks,
            total_marks,
            result

        FROM results

        WHERE usn = %s

        ORDER BY subject_code
        """,
        (usn,)
    )

    results = cur.fetchall()

    cur.close()

    formatted_results = []

    for row in results:

        formatted_results.append({
            "subject_code": row[0],
            "subject_name": row[1],
            "internal_marks": row[2],
            "external_marks": row[3],
            "total_marks": row[4],
            "result": row[5]
        })

    return {
        "usn": student[0],
        "name": student[1],
        "results": formatted_results
    }