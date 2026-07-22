import sqlite3
import pandas as pd
import streamlit as st

# 1. 페이지 설정
st.set_page_config(page_title="고3BT다조 과제 관리", layout="wide")
st.title("📚 고3BT다조 주간 과제 인증 관리")


# 2. SQLite DB 연결 및 테이블 생성 함수
def init_db():
    conn = sqlite3.connect("homework.db")
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            team TEXT,
            role TEXT,
            name TEXT PRIMARY KEY,
            tue BOOLEAN,
            wed BOOLEAN,
            thu BOOLEAN,
            sat BOOLEAN,
            sun BOOLEAN,
            mon BOOLEAN
        )
    """
    )

    # 초기 데이터가 없으면 입력 (박지후 학생 이름 반영)
    c.execute("SELECT COUNT(*) FROM attendance")
    if c.fetchone()[0] == 0:
        initial_members = [
            ("승리 조", "조장", "승리"),
            ("승리 조", "조원", "정원"),
            ("승리 조", "조원", "예서"),
            ("승리 조", "조원", "이현"),
            ("결 조", "조장", "결"),
            ("결 조", "조원", "태준"),
            ("결 조", "조원", "성시우"),
            ("결 조", "조원", "박지후"),
            ("결 조", "조원", "준환"),
            ("준식 조", "조장", "준식"),
            ("준식 조", "조원", "재범"),
            ("준식 조", "조원", "은솔"),
            ("준식 조", "조원", "강민"),
            ("준식 조", "조원", "김시우"),
            ("서정 조", "조장", "서정"),
            ("서정 조", "조원", "태영"),
            ("서정 조", "조원", "승준"),
            ("서정 조", "조원", "가빈"),
            ("민수 조", "조장", "민수"),
            ("민수 조", "조원", "규원"),
            ("민수 조", "조원", "성욱"),
            ("민수 조", "조원", "전지후"),
            ("민수 조", "조원", "이준"),
            ("선우 조", "조장", "선우"),
            ("선우 조", "조원", "정연"),
            ("선우 조", "조원", "준오"),
            ("선우 조", "조원", "하준"),
        ]
        for team, role, name in initial_members:
            c.execute(
                "INSERT INTO attendance VALUES (?, ?, ?, False, False, False, False, False, False)",
                (team, role, name),
            )
        conn.commit()
    conn.close()


# DB 불러오기 함수
def load_data():
    conn = sqlite3.connect("homework.db")
    df = pd.read_sql("SELECT * FROM attendance", conn)
    conn.close()

    # 컬럼명 한글로 변경
    df.columns = [
        "조",
        "역할",
        "이름",
        "화(수2 기본)",
        "수(수2 도전+질문)",
        "목(수2 오답)",
        "토(수1 기본)",
        "일(수1 나머지+질문)",
        "월(수1 오답)",
    ]
    # 체크박스용 불리언 변환
    for col in df.columns[3:]:
        df[col] = df[col].astype(bool)
    return df


# 데이터 수정 반영 함수
def update_data(name, column, value):
    col_map = {
        "화(수2 기본)": "tue",
        "수(수2 도전+질문)": "wed",
        "목(수2 오답)": "thu",
        "토(수1 기본)": "sat",
        "일(수1 나머지+질문)": "sun",
        "월(수1 오답)": "mon",
    }
    db_col = col_map[column]
    conn = sqlite3.connect("homework.db")
    c = conn.cursor()
    c.execute(
        f"UPDATE attendance SET {db_col} = ? WHERE name = ?", (value, name)
    )
    conn.commit()
    conn.close()


# DB 초기화 실행
init_db()
df = load_data()

# 사이드바 - 조 선택
selected_team = st.sidebar.selectbox(
    "조를 선택하세요", ["전체보기"] + list(df["조"].unique())
)

if selected_team != "전체보기":
    filtered_df = df[df["조"] == selected_team].copy()
else:
    filtered_df = df.copy()

st.subheader(f"📌 {selected_team} 체크 현황")

# 체크박스 편집 화면
edited_df = st.data_editor(
    filtered_df,
    column_config={
        "화(수2 기본)": st.column_config.CheckboxColumn("화: 수2 기본"),
        "수(수2 도전+질문)": st.column_config.CheckboxColumn("수: 수2 제출+질문"),
        "목(수2 오답)": st.column_config.CheckboxColumn("목: 수2 오답"),
        "토(수1 기본)": st.column_config.CheckboxColumn("토: 수1 기본"),
        "일(수1 나머지+질문)": st.column_config.CheckboxColumn("일: 수1 제출+질문"),
        "월(수1 오답)": st.column_config.CheckboxColumn("월: 수1 오답"),
    },
    disabled=["조", "역할", "이름"],
    hide_index=True,
    key="homework_editor",
)

# 변경사항 자동 감지 및 DB 저장
for idx, row in edited_df.iterrows():
    orig_row = df[df["이름"] == row["이름"]].iloc[0]
    for col in df.columns[3:]:
        if row[col] != orig_row[col]:
            update_data(row["이름"], col, bool(row[col]))
            st.toast(
                f"💾 {row['이름']} 학생의 {col} 상태가 저장되었습니다!",
                icon="✅",
            )
            st.rerun()

# 리셋 버튼 (새로운 주차가 시작될 때 체크박스 전체 초기화용)
st.divider()
if st.button("🔄 주간 체크박스 전체 초기화 (새로운 주 시작)"):
    conn = sqlite3.connect("homework.db")
    c = conn.cursor()
    c.execute(
        "UPDATE attendance SET tue=False, wed=False, thu=False, sat=False, sun=False, mon=False"
    )
    conn.commit()
    conn.close()
    st.success("모든 체크 현황이 초기화되었습니다.")
    st.rerun()

