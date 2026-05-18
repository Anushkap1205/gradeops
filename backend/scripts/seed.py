"""Seed minimal users and an exam for local testing. Run from backend/: python scripts/seed.py"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.exam import Exam
from app.models.user import User, UserRole


def main() -> None:
    db = SessionLocal()
    try:
        professor = User(name="Dr. Smith", role=UserRole.professor)
        student = User(name="Alex Student", role=UserRole.student)
        ta = User(name="Jordan TA", role=UserRole.ta)
        db.add_all([professor, student, ta])
        db.flush()

        exam = Exam(
            title="Midterm 1",
            course="CS101",
            created_by=professor.id,
        )
        db.add(exam)
        db.commit()

        print("Seed complete:")
        print(f"  professor_id={professor.id}")
        print(f"  student_id={student.id}")
        print(f"  ta_id={ta.id}")
        print(f"  exam_id={exam.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
