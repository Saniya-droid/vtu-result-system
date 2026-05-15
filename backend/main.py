from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import pdfplumber
import re
import uvicorn

app = FastAPI()

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATABASE CONNECTION

DATABASE_URL = "postgresql://neondb_owner:npg_4Ht0WiOuEKIy@ep-muddy-hill-a1uquy4c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# HOME ROUTE

@app.get("/")
def home():
    return {"message": "Backend Working"}

# CREATE TABLE

@app.get("/create-table")
def create_table():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            usn TEXT PRIMARY KEY,
            name TEXT,
            subjects JSONB
        )
    """)

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Table created successfully"}

# CLEAR DATABASE

@app.delete("/clear-results")
def clear_results():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM results")

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "All results deleted successfully"}

# UPLOAD PDF

@app.post("/upload-result")
async def upload_result(file: UploadFile = File(...)):

    temp_file = f"temp_{file.filename}"

    with open(temp_file, "wb") as f:
        f.write(await file.read())

    text = ""

    with pdfplumber.open(temp_file) as pdf:

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    # EXTRACT USN

    usn_match = re.search(r'1[A-Z]{2}\d{2}[A-Z]{2}\d{3}', text)

    usn = usn_match.group(0) if usn_match else "UNKNOWN"

    # EXTRACT NAME

    name_match = re.search(r'Name\s*:\s*([A-Z\s]+)', text)

    name = name_match.group(1).strip() if name_match else "UNKNOWN"

    # SUBJECTS

    subjects = []

    lines = text.split("\n")

    for line in lines:

        marks_match = re.search(r'([A-Z\s]+)\s+(\d{1,3})$', line)

        if marks_match:

            subject_name = marks_match.group(1).strip()

            marks = marks_match.group(2).strip()

            subjects.append({
                "subject": subject_name,
                "marks": marks
            })

    # STORE IN DATABASE

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO results (usn, name, subjects)
        VALUES (%s, %s, %s)
        ON CONFLICT (usn)
        DO UPDATE SET
        name = EXCLUDED.name,
        subjects = EXCLUDED.subjects
        """,
        (usn, name, psycopg2.extras.Json(subjects))
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Result uploaded successfully",
        "usn": usn,
        "name": name
    }

# GET RESULT

@app.get("/get-result/{usn}")
def get_result(usn: str):

    conn = get_db_connection()
    cur = conn.cursor()

    usn = usn.strip().upper()

    cur.execute(
        "SELECT usn, name, subjects FROM results WHERE UPPER(TRIM(usn)) = %s",
        (usn,)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:

        return {
            "usn": result[0],
            "name": result[1],
            "subjects": result[2]
        }

    return {"detail": "Student not found"}

# ALL STUDENTS

@app.get("/students")
def get_students():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT usn, name FROM results")

    students = cur.fetchall()

    cur.close()
    conn.close()

    data = []

    for student in students:

        data.append({
            "usn": student[0],
            "name": student[1]
        })

    return data

# RUN SERVER

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)