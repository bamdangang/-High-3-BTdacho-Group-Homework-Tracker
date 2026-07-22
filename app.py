# streamlit_app.py
import os
import streamlit as st
import pandas as pd
from database_core import (
    get_raw_sqlite_connection,
    SQLiteStudentRepository,
    SQLiteSubmissionRepository,
    SubmissionDTO,
    initialize_database_schema
)

# 데이터베이스 기본 스키마 자동 확인 및 생성
if not os.path.exists("student_academy_tracker.db"):
    initialize_database_schema()

# 메모리 릭 방지를 위한 최적화 세션 기반 싱글톤 DB 세션 연결 [span_42](start_span)[span_42](end_span)[span_43](start_span)[span_43](end_span)[span_44](start_span)[span_44](end_span)
@st.cache_resource(scope="session")
def get_cached_database_connection():
    return get_raw_sqlite_connection()

conn = get_cached_database_connection()
student_repo = SQLiteStudentRepository(conn)
submission_repo = SQLiteSubmissionRepository(conn)

# UI 헤더 세션 스타일 정의
st.set_page_config(page_title="고밀도 수학 인증 대시보드", layout="wide")
st.markdown("""
    <style>
   .reportview-container { background: #0F172A; color: #F1F5F9; }
   .stButton>button { width: 100%; background-color: #3B82F6; color: white; border-radius: 8px; }
    h1, h2, h3 { color: #38BDF8!important; }
    </style>
""", unsafe_allow_html=True)

st.title("학습 관리 고도화 분석 플랫폼")
st.subheader("실시간 주간 정량 학업 성취도 추적 엔진")

# 데이터 동기화용 주차 정의 및 사이드바 설정 
st.sidebar.title("통합 컨트롤 센터")
sele[span_34](start_span)[span_34](end_span)cted_week = st.sidebar.number_input("조사 대상 주차 (Week)", min_value=1, max_value=52, value=1, step=1)

# 테넌트 분리를 위한 조장 정보 세션 정의
group_mapping = {
    "승리 조": "승리",
    "결 조": "결",
    "준식 조": "준식",
    "서정 조": "서정",
    "민수 조": "민수",
    "선우 조": "선우"
}

selected_group = st.sidebar.selectbox("담당 조 선택 (Group Tenant)", list(group_mapping.keys()))
designated_leader = group_mapping[selected_group]

# 보안 가상 검증 (조장 인증 세션 관리 보정) [span_45](start_span)[span_45](end_span)[span_46](start_span)[span_46](end_span)
if "authenticated_leader" not in st.session_state:
    st.session_state["authenticated_leader"] = None

st.sidebar.markdown("---")
if st.session_state["authenticated_leader"]!= designated_leader:
    st.sidebar.warning(f"접속 권한: {selected_group} 조장의 인가가 필요합니다.")
    input_password = st.sidebar.text_input("조장 고유 패스코드 (테스트용: leader123)", type="password")
    if st.sidebar.button("접속 권한 획득"):
        if input_password == "leader123":
            st.session_state["authenticated_leader"] = designated_leader
            st.success("보안 토큰 인가 성공.")
            st.rerun()
        else:
            st.error("패스코드가 불일치합니다.")
else:
    st.sidebar.success(f"보안 승인됨: {designated_leader} 조장 가동 중")
    if st.sidebar.button("접속 해제 (Logout)"):
        st.session_state["authenticated_leader"] = None
        st.rerun()

# 비즈니스 가동 계층 진입
if st.session_state["authenticated_leader"] == designated_leader:
    # 탭 아키텍처 구성을 통한 이력 분석 뷰와 실시간 갱신 뷰 분리
    tab_submission, tab_visual_analytics = st.tabs(["실시간 과제 인증 현황판", "그룹 성취 데이터 정량 분석"])
    
    with tab_submission:
        st.markdown(f"### {selected_group} 소속 조원 실시간 성취 검증 데이터")
        
        # 주간 요일 맵 및 입력 스키마 매핑 정의
        selected_day = st.selectbox(
            "과제 대상 요일 및 과목 확인",
            ["화요일 (수2)", "수요일 (수2-도전)", "목요일 (수2-오답)", "토요일 (수1)", "일요일 (수1-도전)", "월요일 (수1-오답)"]
        )
        
        # 텍스트 형태에서 순수 요일 추출
        day_clean = selected_day.split(" ")
        
        # 해당 그룹에 해당하는 조원 데이터 로딩 [span_47](start_span)[span_47](end_span)
        students = student_repo.get_all_students_by_group(selected_group)
        
        # 조원 루프 생성 및 인라인 편집 그리드 구성 [span_49](start_span)[span_49](end_span)
        for student in students:
            st.markdown(f"#### **{student.student_name} 학생** {'👑 (조장)' if student.is_leader else ''}")
            
            # 기존에 제출된 데이터 조회
            existing_sub = submission_repo.get_submission(selected_week, day_clean, student.student_name)
            
            # 기본 데이터 바인딩 버퍼
            init_completed = existing_sub.is_completed if existing_sub else False
            init_question = existing_sub.question_text if existing_sub else ""
            init_aha = existing_sub.aha_point_text if existing_sub else ""
            init_screenshot = existing_sub.screenshot_path if existing_sub else ""
            
            col_status, col_inputs = st.columns()
            
            with col_status:
                completed_input = st.checkbox(
                    "미션 이행 완료", 
                    value=init_completed, 
                    key=f"check_{student.student_name}_{day_clean}_{selected_week}"
                )
                
                # 원격 리소스를 위한 모사 업로더 추가 
                uploaded_file = st.file_uploader(
                    "인증 스크린샷 적재", 
                    type=["png", "jpg", "jpeg"],
                    key=f"file_{student.student_name}_{day_clean}_{selected_week}"
                )
                
                screenshot_path_to_save = init_screenshot
                if uploaded_file is not None:
                    # 파일 저장 가상 주소 설정 
                    os.makedirs("uploaded_screenshots", exist_ok=True)
                    target_path = os.path.join("uploaded_screenshots", f"{selected_week}_{day_clean}_{student.student_name}.png")
                    with open(target_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    screenshot_path_to_save = target_path
                    st.info("스크린샷이 임시 인프라에 적재되었습니다.")
            
            with col_inputs:
                question_val = init_question
                aha_val = init_aha
                
                # 비즈니스 시나리오 기반의 조건부 입력 양식 드로잉 
                if "도전" in selected_day:
         [span_35](start_span)[span_35](end_span)           st.warning("도전 요일 규칙: 혼자서 해결하기 힘든 지점이나 가설 질문이 의무적으로 기록되어야 합니다.")
                    question_val = st.text_area(
                        "인증 제출 시 질문 기술 (필수)",
                        value=init_question,
                        placeholder="이 문제를 풀 때 가정한 핵심 개념과 막힌 포인트는 무엇인가요?",
                        key=f"quest_{student.student_name}_{day_clean}_{selected_week}"
                    )
                elif "오답" in selected_day:
                    st.info("오답 요일 규칙: 해설 분석을 통한 스스로의 각성 포인트(아하포인트) 작성이 누락되면 인증 승인이 거절됩니다.")
                    aha_val = st.text_area(
                        "오답 정리 아하포인트 기술 (필수)",
                        value=init_aha,
                        placeholder="실수 방지를 위해 수집한 아하포인트를 입력하세요.",
                        key=f"aha_{student.student_name}_{day_clean}_{selected_week}"
                    )
                else:
                    st.success("타임어택 요일: 신속 정확하게 기본 문제를 푼 뒤 이행 체크를 완료하세요.")
            
            # 저장 액션 처리 [span_50](start_span)[span_50](end_span)
            if st.button(f"{student.student_name} 학생 데이터 원격 저장", key=f"save_btn_{student.student_name}_{day_clean}"):
                
                # 비즈니스 규칙 유효성 검사 예외 트리거
                if "도전" in selected_day and not question_val.strip():
                    st.error(f"{student.student_name} 학생의 도전 제출용 질문 작성이 생략되었습니다. 저장할 수 없습니다.")
                elif "오답" in selected_day and not aha_val.strip():
                    st.error(f"{student.student_name} 학생의 오답 노트용 아하포인트 작성이 누락되었습니다. 저장할 수 없습니다.")
                else:
                    new_submission = SubmissionDTO(
                        id=None,
                        week_number=selected_week,
                        day_of_week=day_clean,
                        student_name=student.student_name,
                        is_completed=completed_input,
                        screenshot_path=screenshot_path_to_save,
                        question_text=question_val,
                        aha_point_text=aha_val,
                        verified_at=None
                    )
                    submission_repo.save_submission(new_submission)
                    st.success(f"{student.student_name} 학생의 {day_clean} 일자 인증 레코드가 무결하게 트랜잭션 기록되었습니다.")
            st.markdown("---")
            
    with tab_visual_analytics:
        st.markdown(f"### {selected_group} 주간 정량 성취율 현황 (Week {selected_week})")
        
        # 분석 리포트 가공을 위한 통계 리포트 데이터 로딩 
       [span_48](start_span)[span_48](end_span) raw_stats = submission_repo.get_group_weekly_stats(selected_week, selected_group)
        if raw_stats:
            stats_df = pd.DataFrame(raw_stats)
            stats_df.columns =
            
            # 성취율 백분율 산출 파이프라인
            stats_df["주간 달성률 (%)"] = (stats_df / 6 * 100).round(1)
            
            st.dataframe(stats_df, use_container_width=True)
            
            # 스트림릿 자체 차트 위젯을 연동한 정량적 비교 그래프 출력
            st.bar_chart(data=stats_df, x="학생 이름", y="주간 달성률 (%)")
        else:
            st.info("데이터베이스 트랜잭션 수집 진행 중입니다. 분석 데이터가 부족합니다.")
else:
    st.info("왼쪽 사이드바의 제어 센터를 통하여 담당하시는 조장 권한 패스코드를 기입해 주십시오.")

