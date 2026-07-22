# database_core.py
import os
import sqlite3
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# 로깅 설정 표준화
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnterpriseDB")

DB_FILE_PATH = "student_academy_tracker.db"

def get_raw_sqlite_connection() -> sqlite3.Connection:
    """
    고성능 대기 행렬 및 동시 스레드 동시 조회를 위한 WAL 및 busy_timeout 적용 SQLite 커넥션 팩토리.
    """
    conn = sqlite3.connect(
        DB_FILE_PATH,
        timeout=10.0,
        check_same_thread=False
    )
    # WAL 모드 전면 적용을 통한 읽기-쓰기 격리 성능 극대화 
    conn.execute("PRAGMA journal_mode=WAL;")
    conn[span_10](start_span)[span_10](end_span)[span_12](start_span)[span_12](end_span)[span_14](start_span)[span_14](end_span).execute("PRAGMA busy_timeout=5000;")
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
    day_of_week: str  # 화, 수, 목, 토, 일, 월
    student_name: str
    is_completed: bool
    screenshot_path: Optional[str]
    question_text: Optional[str]
    aha_point_text: Optional[str]
    verified_at: Optional[str]

class IStudentRepository(ABC):
    @abstractmethod
    def get_all_students_by_group(self, group_name: str) -> List:
        pass

class ISubmissionRepository(ABC):
    @abstractmethod
    def get_submission(self, week: int, day: str, student_name: str) -> Optional:
        pass

    @abstractmethod
    def save_submission(self, submission: SubmissionDTO) -> None:
        pass

    @abstractmethod
    def get_group_weekly_stats(self, week: int, group_name: str) -> List]:
        pass

class SQLiteStudentRepository(IStudentRepository):
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def get_all_students_by_group(self, group_name: str) -> List:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, group_name, student_name, is_leader FROM students WHERE group_name =? ORDER BY is_leader DESC, student_name ASC",
            (group_name,)
        )
        rows = cursor.fetchall()
        return, group_name=r, student_name=r, is_leader=bool(r)) for r in rows]

class SQLiteSubmissionRepository(ISubmissionRepository):
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
            id=row, week_number=row, day_of_week=row, student_name=row,
            is_completed=bool(row), screenshot_path=row, question_text=row,
            aha_point_text=row, verified_at=row
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
             submission.is_completed, submission.screenshot_path, submission.question_text,
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
        return [{"student_name": r, "completed": r, "total": r} for r in rows]

def initialize_database_schema():
    """
    초기 시드 데이터 및 프로덕션 스키마 정적 구축.
    """
    conn = get_raw_sqlite_connection()
    cursor = conn.cursor()
    
    # 테이블 생성
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
    
    # 초기 그룹 인원 마이그레이션 데이터 정의
    seeding_students = [
        # 승리 조
        ("승리 조", "승리", 1), ("승리 조", "정원", 0), ("승리 조", "예서", 0), ("승리 조", "이현", 0),
        # 결 조
        ("결 조", "결", 1), ("결 조", "태준", 0), ("결 조", "성시우", 0), ("결 조", "박시후", 0), ("결 조", "준환", 0),
        # 준식 조
        ("준식 조", "준식", 1), ("준식 조", "재범", 0), ("준식 조", "은솔", 0), ("준식 조", "강민", 0), ("준식 조", "김시우", 0),
        # 서정 조
        ("서정 조", "서정", 1), ("서정 조", "태영", 0), ("서정 조", "승준", 0), ("서정 조", "가빈", 0),
        # 민수 조
        ("민수 조", "민수", 1), ("민수 조", "규원", 0), ("민수 조", "성욱", 0), ("민수 조", "전지후", 0), ("민수 조", "이준", 0),
        # 선우 조
        ("선우 조", "선우", 1), ("선우 조", "정연", 0), ("선우 조", "준오", 0), ("선우 조", "하준", 0)
    ]
    
    for group, name, leader in seeding_students:
        cursor.execute(
            "INSERT OR IGNORE INTO students (group_name, student_name, is_leader) VALUES (?,?,?)",
            (group, name, leader)
        )
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database_schema()
