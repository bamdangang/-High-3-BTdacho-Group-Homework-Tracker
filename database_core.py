import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AcademyDB")

DB_FILE_PATH = "student_academy_tracker.db"

def get_raw_sqlite_connection() -> sqlite3.Connection:
    """
    여러 사용자가 동시에 접근해도 락(Lock) 충돌이 나지 않도록 WAL 모드를 설정하는 SQLite 연결 함수입니다.
    """
    conn = sqlite3.connect(
        DB_FILE_PATH,
        timeout=10.0,
        check_same_thread=False
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

@dataclass
class StudentDTO:
    id: int
    group_name: str
    student_name: str
    is_leader: bool

@dataclass
class SubmissionDTO:
    id: Optional[int]
    week_number: int
    day_of_week: str
    student_name: str
    is_completed: bool
    screenshot_path: Optional[str]
    question_text: Optional[str]
    aha_point_text: Optional[str]
    verified_at: Optional[str]

class SQLiteStudentRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def get_all_students_by_group(self, group_name: str) -> List:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, group_name, student_name, is_leader FROM students WHERE group_name =? ORDER BY is_leader DESC, student_name ASC",
            (group_name,)
        )
        rows = cursor.fetchall()
        return, group_name=r[1], student_name=r[2], is_leader=bool(r[3]))
            for r in rows
        ]

class SQLiteSubmissionRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def get_submission(self, week: int, day: str, student_name: str) -> Optional:
        cursor = self._conn.cursor()
        cursor.execute(
            """SELECT id, week_number, day_of_week, student_name, is_completed, 
                      screenshot_path, question_text, aha_point_text, verified_at 
               FROM submissions 
               WHERE week_number =? AND day_of_week =? AND student_name =?""",
            (week, day, student_name)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SubmissionDTO(
            id=row, week_number=row[1], day_of_week=row[2], student_name=row[3],
            is_completed=bool(row[4]), screenshot_path=row[5], question_text=row[6],
            aha_point_text=row[7], verified_at=row[8]
        )

    def save_submission(self, submission: SubmissionDTO) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """INSERT INTO submissions (week_number, day_of_week, student_name, is_completed, 
                                        screenshot_path, question_text, aha_point_text, verified_at)
               VALUES (?,?,?,?,?,?,?, datetime('now', 'localtime'))
               ON CONFLICT(week_number, day_of_week, student_name) DO UPDATE SET
                  is_completed = excluded.is_completed,
                  screenshot_path = excluded.screenshot_path,
                  question_text = excluded.question_text,
                  aha_point_text = excluded.aha_point_text,
                  verified_at = datetime('now', 'localtime')""",
            (submission.week_number, submission.day_of_week, submission.student_name,
             int(submission.is_completed), submission.screenshot_path, submission.question_text,
             submission.aha_point_text)
        )
        self._conn.commit()

    def get_group_weekly_stats(self, week: int, group_name: str) -> List]:
        cursor = self._conn.cursor()
        cursor.execute(
            """SELECT s.student_name, 
                      SUM(CASE WHEN sub.is_completed = 1 THEN 1 ELSE 0 END) as completed_count,
                      COUNT(sub.id) as registered_count
               FROM students s
               LEFT JOIN submissions sub ON s.student_name = sub.student_name AND sub.week_number =?
               WHERE s.group_name =?
               GROUP BY s.student_name""",
            (week, group_name)
        )
        rows = cursor.fetchall()
        # 주간 과제 종류는 총 6가지(화, 수, 목, 토, 일, 월)이므로 총합을 6으로 설정하여 전송합니다.
        return [{"student_name": r, "completed": r[1], "total": 6} for r in rows]

def initialize_database_schema():
    conn = get_raw_sqlite_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            student_name TEXT UNIQUE NOT NULL,
            is_leader INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_number INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            student_name TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            screenshot_path TEXT,
            question_text TEXT,
            aha_point_text TEXT,
            verified_at TEXT,
            UNIQUE(week_number, day_of_week, student_name),
            FOREIGN KEY(student_name) REFERENCES students(student_name) ON DELETE CASCADE
        )
    """)
    # 조원 및 조장 구성 기초 데이터 씨딩 (박지후 학생 이름 보정 완료)
    seeding_students = [
        ("승리 조", "승리", 1), ("승리 조", "정원", 0), ("승리 조", "예서", 0), ("승리 조", "이현", 0),
        ("결 조", "결", 1), ("결 조", "태준", 0), ("결 조", "성시우", 0), ("결 조", "박지후", 0), ("결 조", "준환", 0),
        ("준식 조", "준식", 1), ("준식 조", "재범", 0), ("준식 조", "은솔", 0), ("준식 조", "강민", 0), ("준식 조", "김시우", 0),
        ("서정 조", "서정", 1), ("서정 조", "태영", 0), ("서정 조", "승준", 0), ("서정 조", "가빈", 0),
        ("민수 조", "민수", 1), ("민수 조", "규원", 0), ("민수 조", "성욱", 0), ("민수 조", "전지후", 0), ("민수 조", "이준", 0),
        ("선우 조", "선우", 1), ("선우 조", "정연", 0), ("선우 조", "준오", 0), ("선우 조", "하준", 0)
    ]
    for group, name, leader in seeding_students:
        cursor.execute(
            "INSERT OR IGNORE INTO students (group_name, student_name, is_leader) VALUES (?,?,?)",
            (group, name, leader)
        )
    conn.commit()
    conn.close()
