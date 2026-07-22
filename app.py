import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 페이지 기본 설정
st.set_page_config(page_title="고3BT다조 과제 관리", layout="wide")
st.title("📚 고3BT다조 주간 과제 인증 관리")

# 구글 시트 연결 생성
conn = st.connection("gsheets", type=GSheetsConnection)


# 1. 초기 데이터 구조 정의 (구글 시트가 비어있을 때 사용)
def get_initial_data():
    return pd.DataFrame(
        {
            "조": [
                "승리 조",
                "승리 조",
                "승리 조",
                "승리 조",
                "결 조",
                "결 조",
                "결 조",
                "결 조",
                "결 조",
                "준식 조",
                "준식 조",
                "준식 조",
                "준식 조",
                "준식 조",
                "서정 조",
                "서정 조",
                "서정 조",
                "서정 조",
                "민수 조",
                "민수 조",
                "민수 조",
                "민수 조",
                "민수 조",
                "선우 조",
                "선우 조",
                "선우 조",
                "선우 조",
            ],
            "역할": [
                "조장",
                "조원",
                "조원",
                "조원",
                "조장",
                "조원",
                "조원",
                "조원",
                "조원",
                "조장",
                "조원",
                "조원",
                "조원",
                "조원",
                "조장",
                "조원",
                "조원",
                "조원",
                "조장",
                "조원",
                "조원",
                "조원",
                "조원",
                "조장",
                "조원",
                "조원",
                "조원",
            ],
            "이름": [
                "승리",
                "정원",
                "예서",
                "이현",
                "결",
                "태준",
                "성시우",
                "박지후",
                "준환",  # 박지후 반영
                "준식",
                "재범",
                "은솔",
                "강민",
                "김시우",
                "서정",
                "태영",
                "승준",
                "가빈",
                "민수",
                "규원",
                "성욱",
                "전지후",
                "이준",
                "선우",
                "정연",
                "준오",
                "하준",
            ],
            "화(수2 기본)": [False] * 27,
            "수(수2 도전+질문)": [False] * 27,
            "목(수2 오답)": [False] * 27,
            "토(수1 기본)": [False] * 27,
            "일(수1 나머지+질문)": [False] * 27,
            "월(수1 오답)": [False] * 27,
        }
    )


# 2. 구글 시트에서 데이터 읽어오기
try:
    existing_data = conn.read(worksheet="Sheet1", ttl=5)
    if existing_data.empty or len(existing_data) == 0:
        df = get_initial_data()
        conn.update(worksheet="Sheet1", data=df)
    else:
        df = existing_data
except Exception as e:
    st.info("구글 시트를 초기화하는 중입니다...")
    df = get_initial_data()
    conn.update(worksheet="Sheet1", data=df)

# 불리언(True/False) 타입 보장
check_columns = [
    "화(수2 기본)",
    "수(수2 도전+질문)",
    "목(수2 오답)",
    "토(수1 기본)",
    "일(수1 나머지+질문)",
    "월(수1 오답)",
]
for col in check_columns:
    df[col] = df[col].astype(bool)

# 사이드바 - 조 선택 필터
selected_team = st.sidebar.selectbox(
    "조를 선택하세요", ["전체보기"] + list(df["조"].unique())
)

if selected_team != "전체보기":
    filtered_df = df[df["조"] == selected_team].copy()
else:
    filtered_df = df.copy()

st.subheader(f"📌 {selected_team} 체크 현황")

# 3. 데이터 에디터 (수정 시 실시간 구글 시트 저장)
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
    key="data_editor",
)

# 변경사항 발생 시 구글 시트로 자동 동기화
if not edited_df.equals(filtered_df):
    df.update(edited_df)
    conn.update(worksheet="Sheet1", data=df)
    st.toast("✅ 구글 시트에 실시간으로 저장되었습니다!", icon="💾")
    st.rerun()
