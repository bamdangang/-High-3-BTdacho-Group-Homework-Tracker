import pandas as pd
import streamlit as st

# 1. 이미지 기반 학생 데이터 구조화
data = {
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
        "이현",  # 승리 조
        "결",
        "태준",
        "성시우",
        "박지후",
        "준환",  # 결 조
        "준식",
        "재범",
        "은솔",
        "강민",
        "김시우",  # 준식 조
        "서정",
        "태영",
        "승준",
        "가빈",  # 서정 조
        "민수",
        "규원",
        "성욱",
        "전지후",
        "이준",  # 민수 조
        "선우",
        "정연",
        "준오",
        "하준",  # 선우 조
    ],
    "화(수2 기본)": [False] * 27,
    "수(수2 도전+질문)": [False] * 27,
    "목(수2 오답)": [False] * 27,
    "토(수1 기본)": [False] * 27,
    "일(수1 나머지+질문)": [False] * 27,
    "월(수1 오답)": [False] * 27,
}

df = pd.DataFrame(data)

# Streamlit 웹 UI 구성
st.set_page_config(page_title="주간 숙제 인증 관리", layout="wide")
st.title("📚 주간 수1/수2 숙제 인증 관리 시스템")

# 조별 필터 선택
selected_team = st.sidebar.selectbox(
    "조를 선택하세요", ["전체보기"] + list(df["조"].unique())
)

if selected_team != "전체보기":
    filtered_df = df[df["조"] == selected_team]
else:
    filtered_df = df

st.subheader(f"📌 {selected_team} 인증 현황")

# 인터랙티브 체크박스 데이터 에디터 출력
edited_df = st.data_editor(
    filtered_df,
    column_config={
        "화(수2 기본)": st.column_config.CheckboxColumn("화: 수2 타임어택/기본"),
        "수(수2 도전+질문)": st.column_config.CheckboxColumn("수: 수2 제출+질문 필수"),
        "목(수2 오답)": st.column_config.CheckboxColumn("목: 수2 오답(아하포인트)"),
        "토(수1 기본)": st.column_config.CheckboxColumn("토: 수1 타임어택/기본"),
        "일(수1 나머지+질문)": st.column_config.CheckboxColumn("일: 수1 제출+질문 필수"),
        "월(수1 오답)": st.column_config.CheckboxColumn("월: 수1 오답(아하포인트)"),
    },
    disabled=["조", "역할", "이름"],
    hide_index=True,
)

# 저장 및 다운로드 기능
st.divider()
csv = edited_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 현재 체크 현황 CSV 다운로드",
    data=csv,
    file_name="homework_check.csv",
    mime="text/csv",
)
