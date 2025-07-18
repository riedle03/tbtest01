import streamlit as st
import pandas as pd # pandas 라이브러리 추가 (Streamlit의 기본 시각화에 자주 사용됨)

# --- 1. Streamlit 세션 상태 초기화 ---
# 페이지 이동 및 설문 데이터를 관리하기 위한 세션 상태 변수 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'main'  # 현재 페이지
if 'survey_answers' not in st.session_state:
    st.session_state.survey_answers = {}  # 사용자의 설문 응답 저장
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0  # 총 번아웃 점수
if 'ee_score' not in st.session_state:
    st.session_state.ee_score = 0  # 감정 소진 점수
if 'dp_score' not in st.session_state:
    st.session_state.dp_score = 0  # 비인격화 점수
if 'rpa_score' not in st.session_state:
    st.session_state.rpa_score = 0  # 자아성취감 저하 점수
if 'burnout_stage_info' not in st.session_state:
    st.session_state.burnout_stage_info = {} # 번아웃 단계 정보 (동물, 설명 등)
if 'privacy_agreed' not in st.session_state:
    st.session_state.privacy_agreed = False # 개인정보 동의 여부

# --- 2. 설문 문항 정의 ---
# MBI-ES (Maslach Burnout Inventory - Educators Survey) 기반으로 간소화된 설문 문항
# 각 문항은 7점 리커트 척도 (0점: 전혀 그렇지 않다 ~ 6점: 매일 그렇다)
# 'category': 'EE' (Emotional Exhaustion), 'DP' (Depersonalization), 'RPA' (Reduced Personal Accomplishment)
survey_questions = [
    {"id": "q1", "text": "나는 업무 때문에 **정신적으로 지쳐** 있습니다. 🧠", "category": "EE"},
    {"id": "q2", "text": "나는 일과시간이 끝날 때쯤 **녹초**가 됩니다. 🔋", "category": "EE"},
    {"id": "q3", "text": "나는 아침에 일어나 일할 생각을 하면 **피곤함**을 느낍니다. 🥱", "category": "EE"},
    {"id": "q4", "text": "하루 종일 학생들과 함께 일하는 것은 나에게 정말 **힘든 일**입니다. 😩", "category": "EE"},
    {"id": "q5", "text": "나는 나의 일로 인해 매우 **지쳐** 있습니다. 😵‍💫", "category": "EE"},
    {"id": "q6", "text": "나는 나의 일로 인해 **좌절감**을 느낍니다. 😔", "category": "EE"},
    {"id": "q7", "text": "나는 내가 나의 일을 너무 **열심히** 하고 있다고 느낍니다. 🔥", "category": "EE"},
    {"id": "q8", "text": "학생들과 직접 대하는 일은 나에게 매우 큰 **스트레스**를 만듭니다. 💢", "category": "EE"},
    {"id": "q9", "text": "나는 내가 **한계에 다다르고** 있다고 느낍니다. 🚧", "category": "EE"},
    {"id": "q10", "text": "나는 일부 학생을 대할 때, **인격이 없는 사물처럼** 대하고 있다고 느낍니다. 🤖", "category": "DP"},
    {"id": "q11", "text": "나는 일을 시작한 후 학생들에게 **감정이 메말라졌습니다**. 🍂", "category": "DP"},
    {"id": "q12", "text": "나는 내가 **속수무책**인 것처럼 느껴질 때가 있습니다. 🤷", "category": "DP"},
    {"id": "q13", "text": "나는 일부 학생들에게 무슨 일이 일어나는지 **별로 신경 쓰지 않습니다**. 😐", "category": "DP"},
    {"id": "q14", "text": "나는 학생들이 일부 그들의 문제 책임을 나에게 **돌리고 있다고** 느낍니다. blaming", "category": "DP"},
    {"id": "q15", "text": "나는 학생들의 감정을 **잘 이해**합니다. 👍", "category": "RPA"}, # 역채점 필요
    {"id": "q16", "text": "나는 학생들의 문제를 **효과적으로 다룹니다**. ✅", "category": "RPA"}, # 역채점 필요
    {"id": "q17", "text": "나는 나의 일을 통해 다른 사람들에게 **긍정적인 영향을 주고** 있다고 느낍니다. ✨", "category": "RPA"}, # 역채점 필요
    {"id": "q18", "text": "나는 매우 **활기차다**고 느낍니다. ⚡", "category": "RPA"}, # 역채점 필요
    {"id": "q19", "text": "나는 학생들에게 **편안한 분위기를 쉽게 조성**해 줄 수 있습니다. 😌", "category": "RPA"}, # 역채점 필요
    {"id": "q20", "text": "나는 학생들과 일이 끝나고 친밀해지면 **기운이 북돋습니다**. 🚀", "category": "RPA"}, # 역채점 필요
    {"id": "q21", "text": "나는 이 일을 통해 많은 **가치 있는 일들을 성취**했습니다. 🏆", "category": "RPA"}, # 역채점 필요
    {"id": "q22", "text": "나는 일을 하면서 감정적인 문제들을 **침착하게 처리**합니다. 🧘", "category": "RPA"} # 역채점 필요
]

# 리커트 척도 옵션 (0점부터 6점까지)
likert_options = [
    "전혀 그렇지 않다 (0점)",
    "거의 그렇지 않다 (1점)",
    "가끔 그렇다 (2점)",
    "자주 그렇다 (3점)",
    "상당히 그렇다 (4점)",
    "매우 그렇다 (5점)",
    "매일 그렇다 (6점)"
]

# --- 3. 번아웃 단계 정보 정의 (동물 비유) ---
# 총점 기준 (최대 점수 22문항 * 6점 = 132점)
burnout_stages = {
    "stage1": {
        "name": "활기찬 다람쥐",
        "emoji": "🐿️", # 이모지 추가
        "description": "에너지가 넘치고, 업무에 대한 열정이 높으며, 스트레스 관리를 잘 하고 있는 상태입니다. 현재의 긍정적인 상태를 유지하며 더욱 발전할 수 있습니다.",
        "recommendations": [
            "꾸준한 자기 관리와 긍정적인 습관을 유지하세요.",
            "새로운 도전과 학습 기회를 찾아보세요.",
            "주변 동료 및 가족과의 긍정적인 관계를 유지하고 강화하세요."
        ],
        "score_range": (0, 26)
    },
    "stage2": {
        "name": "지친 고양이",
        "emoji": "🐈", # 이모지 추가
        "description": "가끔 피로감을 느끼고, 업무에 대한 작은 짜증이 생기지만, 아직 스스로 회복 가능한 수준입니다. 작은 휴식과 리프레시가 필요합니다.",
        "recommendations": [
            "짧은 휴식 시간(점심시간, 쉬는 시간)을 적극 활용하세요.",
            "좋아하는 취미 활동이나 가벼운 운동으로 기분 전환을 시도하세요.",
            "충분한 수면 시간을 확보하고 수면의 질을 높여보세요."
        ],
        "score_range": (27, 52)
    },
    "stage3": {
        "name": "힘든 코끼리",
        "emoji": "🐘", # 이모지 추가
        "description": "만성적인 피로와 함께 업무에 대한 의욕이 저하되고, 감정 조절에 어려움을 겪기 시작하는 상태입니다. 적극적인 자기 돌봄과 주변의 도움이 필요한 시점입니다.",
        "recommendations": [
            "규칙적인 휴식과 재충전 시간을 계획하고 실천하세요.",
            "스트레스 해소에 도움이 되는 자신만의 방법을 탐색하고 적용하세요.",
            "신뢰할 수 있는 동료, 친구, 가족과 솔직하게 대화하며 감정을 나누세요.",
            "필요하다면 전문가와의 상담을 적극적으로 고려해 보세요."
        ],
        "score_range": (53, 78)
    },
    "stage4": {
        "name": "지쳐 쓰러진 사자",
        "emoji": "🦁", # 이모지 추가
        "description": "극심한 감정 소진, 비인격화, 자아성취감 저하가 뚜렷하게 나타나며, 일상생활에도 영향을 미치는 상태입니다. 혼자 해결하기 어려우며, 전문가의 도움이 절실히 필요한 시점입니다.",
        "recommendations": [
            "즉각적인 휴식과 업무 부담 경감이 필요합니다. 학교 또는 교육청에 도움을 요청하는 것을 고려하세요.",
            "심리 상담 전문가와의 심층 상담을 통해 근본적인 원인을 파악하고 해결 방안을 모색하세요.",
            "신체적인 증상이 동반된다면 의료기관을 방문하여 진료를 받으세요."
        ],
        "score_range": (79, 104)
    },
    "stage5": {
        "name": "동면하는 곰",
        "emoji": "🐻", # 이모지 추가
        "description": "모든 에너지가 고갈되어 무기력하고, 사회적 관계를 회피하며, 심각한 신체적/정신적 증상을 보이는 상태입니다. 즉각적인 휴식과 전문적인 치료가 필요한 위급한 상태입니다.",
        "recommendations": [
            "최우선적으로 전문 의료기관(정신건강의학과)을 방문하여 진단 및 치료를 받으세요.",
            "충분한 휴식과 회복 시간을 확보하고, 업무에서 잠시 벗어나 자신을 돌보는 데 집중하세요.",
            "가족 및 주변의 적극적인 지지와 도움이 필요합니다. 도움을 요청하는 것을 주저하지 마세요."
        ],
        "score_range": (105, 132)
    }
}

# --- 4. 페이지 이동 함수 ---
def go_to_page(page_name):
    st.session_state.page = page_name

# --- 5. 메인 페이지 함수 ---
def main_page():
    st.title("👨‍🏫 교사 번아웃 자가 진단 웹사이트")
    st.markdown("""
    안녕하세요, 선생님! 이 웹사이트는 선생님의 번아웃 상태를 익명으로 자가 진단하고, 그 결과를 친근한 '동물 비유'를 통해 시각적으로 안내하며, 
    개인 맞춤형 스트레스 관리 리소스를 연계하는 것을 목표로 합니다.
    
    선생님의 소중한 정신 건강을 지키고, 더 나아가 행복한 교육 환경을 만드는 데 기여하고자 합니다.
    """)

    st.subheader("💡 웹사이트 목표")
    st.markdown("""
    * 선생님들이 자신의 번아웃 상태를 쉽고 익명으로 진단할 수 있는 환경 제공
    * 진단 결과를 직관적이고 비판단적인 동물 비유로 시각화하여 심리적 부담 경감 및 공감대 형성
    * 진단 결과에 따른 맞춤형 스트레스 관리 팁 및 전문 상담 리소스 제공
    """)

    st.subheader("🔒 개인정보 처리 방침 및 동의")
    st.info("""
    본 설문은 선생님의 번아웃 상태를 진단하기 위한 것으로, **'건강에 관한 정보'**에 해당될 수 있는 **민감정보**를 포함합니다.
    선생님의 개인 식별 정보는 일체 수집되지 않으며, 설문 결과는 익명으로 처리됩니다.
    수집된 익명 데이터는 오직 서비스 개선 및 교사 번아웃 현황에 대한 통계적 분석(개인을 식별할 수 없는 형태)에만 활용됩니다.
    
    **동의 거부 시 불이익:** 본 설문은 자율적인 참여를 원칙으로 하며, 동의를 거부하셔도 어떠한 불이익도 없습니다.
    """)

    # 개인정보 동의 체크박스
    st.session_state.privacy_agreed = st.checkbox("위 개인정보 처리 방침에 동의합니다. (필수)", value=st.session_state.privacy_agreed)

    if st.session_state.privacy_agreed:
        st.button("설문 시작하기", on_click=go_to_page, args=('survey',))
    else:
        st.warning("설문을 시작하려면 개인정보 처리 방침에 동의해야 합니다.")

# --- 6. 설문 페이지 함수 ---
def survey_page():
    st.title("📝 교사 번아웃 자가 진단 설문")
    st.markdown("다음 문항을 읽고, 최근 1개월 동안 자신에게 해당되는 정도를 선택해 주세요.")

    # 설문 폼 시작
    with st.form(key='burnout_survey_form'):
        st.markdown("---")
        # 각 문항에 대한 라디오 버튼 생성
        for q in survey_questions:
            # 기본값 설정 (선택되지 않은 상태)
            default_index = likert_options.index(st.session_state.survey_answers.get(q['id'], likert_options[0]))
            st.session_state.survey_answers[q['id']] = st.radio(
                f"**{q['text']}**",
                likert_options,
                index=default_index,
                key=q['id'] # 각 라디오 버튼의 고유 키
            )
            st.markdown("---")
        
        submitted = st.form_submit_button("결과 확인하기")

        if submitted:
            # 점수 계산
            total_score = 0
            ee_score = 0
            dp_score = 0
            rpa_score = 0

            for q in survey_questions:
                # 선택된 옵션에서 점수 추출 (예: "전혀 그렇지 않다 (0점)" -> 0)
                score_str = st.session_state.survey_answers[q['id']].split('(')[1].replace('점)', '')
                score = int(score_str)

                # RPA (자아성취감 저하) 문항은 역채점 (6점 -> 0점, 0점 -> 6점)
                if q['category'] == 'RPA':
                    score = 6 - score # 7점 척도에서 0-6점 기준이므로 6에서 뺌

                total_score += score
                if q['category'] == 'EE':
                    ee_score += score
                elif q['category'] == 'DP':
                    dp_score += score
                elif q['category'] == 'RPA':
                    rpa_score += score
            
            st.session_state.total_score = total_score
            st.session_state.ee_score = ee_score
            st.session_state.dp_score = dp_score
            st.session_state.rpa_score = rpa_score

            # 번아웃 단계 결정
            st.session_state.burnout_stage_info = calculate_burnout_stage(total_score)
            
            go_to_page('result')

# --- 7. 번아웃 단계 계산 함수 ---
def calculate_burnout_stage(score):
    for stage_key, stage_info in burnout_stages.items():
        min_score, max_score = stage_info["score_range"]
        if min_score <= score <= max_score:
            return stage_info
    return burnout_stages["stage5"] # 기본값 또는 최고 단계

# --- 8. 결과 페이지 함수 ---
def result_page():
    st.title("📊 나의 번아웃 진단 결과")

    stage_info = st.session_state.burnout_stage_info
    total_score = st.session_state.total_score
    
    # 인포그래픽 형식 시작
    st.markdown("---")
    st.subheader("✨ 당신의 번아웃 프로필 ✨")

    # 카드 게임 형식으로 동물 카드 표시
    st.markdown(f"""
    <div style="
        border: 2px solid #4CAF50; /* 테두리 색상 */
        border-radius: 15px; /* 둥근 모서리 */
        padding: 20px;
        margin: 20px 0;
        background-color: #e8f5e9; /* 배경색 */
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2); /* 그림자 효과 */
        text-align: center;
    ">
        <h2 style="color: #2e7d32; margin-bottom: 10px;">{stage_info['name']} {stage_info['emoji']}</h2>
        <p style="font-size: 80px; margin: 0;">{stage_info['emoji']}</p>
        <p style="font-size: 1.1em; color: #388e3c;">
            _{stage_info['description']}_
        </p>
        <p style="font-size: 1.2em; font-weight: bold; color: #1b5e20;">
            총 번아웃 점수: {total_score}점 (최대 132점)
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 전체 번아웃 진행도
    st.subheader("📊 전체 번아웃 진행도")
    max_total_score = 132
    progress_percentage = (total_score / max_total_score) * 100
    st.progress(int(progress_percentage))
    st.caption(f"현재 번아웃 진행도: {progress_percentage:.1f}%")
    st.markdown("---")

    st.subheader("📈 세부 번아웃 지표 분석")

    # 세부 번아웃 지표 설명
    st.markdown("""
    번아웃은 크게 세 가지 핵심 지표로 구성됩니다. 각 지표는 선생님의 번아웃 상태를 이해하는 데 중요한 통찰을 제공합니다.
    * **감정 소진 (Emotional Exhaustion):** 업무로 인해 감정적, 신체적으로 에너지가 고갈되고 지쳐있는 정도를 나타냅니다. 이 점수가 높을수록 심한 피로감을 느끼며, 업무에 대한 의욕이 저하될 수 있습니다.
    * **비인격화 (Depersonalization):** 학생이나 동료 등 타인에 대해 냉소적이고 무관심한 태도를 보이는 정도를 나타냅니다. 이 점수가 높을수록 타인과의 관계에서 거리를 두려 하고, 감정적으로 메말라질 수 있습니다.
    * **자아성취감 저하 (Reduced Personal Accomplishment):** 자신의 업무 성과나 능력에 대해 부정적으로 느끼고, 성취감이 낮은 정도를 나타냅니다. 이 점수가 높을수록 자신의 노력이 의미 없다고 느끼거나, 무기력해질 수 있습니다.
    """)

    # 세부 번아웃 지표 데이터프레임 생성
    burnout_data = {
        '지표': ['감정 소진', '비인격화', '자아성취감 저하'],
        '점수': [st.session_state.ee_score, st.session_state.dp_score, st.session_state.rpa_score]
    }
    df_burnout = pd.DataFrame(burnout_data)

    # 지표별 최대 점수 (차트 스케일링을 위해)
    # MBI-ES 문항 수에 따른 최대 점수 (각 문항 6점 기준)
    max_ee_score = 9 * 6  # 감정 소진 9문항
    max_dp_score = 5 * 6  # 비인격화 5문항
    max_rpa_score = 8 * 6 # 자아성취감 저하 8문항 (역채점 후)

    # DataFrame에 최대 점수 추가 (차트 시각화에 활용)
    df_burnout['최대 점수'] = [max_ee_score, max_dp_score, max_rpa_score]

    # 세로 막대 차트 (st.bar_chart는 기본적으로 세로 막대)
    # Streamlit의 기본 bar_chart는 여러 시리즈를 한 차트에 선으로 연결하는 기능을 직접 제공하지 않습니다.
    # 각 지표를 개별 막대로 표시하고, 설명으로 보완합니다.
    st.bar_chart(df_burnout.set_index('지표'))
    st.caption("각 지표의 막대 길이는 해당 지표의 점수를 나타냅니다. (오른쪽 스케일 참고)")

    st.markdown("---")

    st.subheader("🌟 나를 위한 맞춤형 권장사항")
    for rec in stage_info['recommendations']:
        st.markdown(f"- {rec}")
    
    st.markdown("---")

    st.subheader("🔗 전문가 연계 정보")
    st.markdown("""
    보다 정확한 진단과 심층적인 상담이 필요하다면, 아래 전문 기관의 도움을 받아보세요.
    * **교원치유지원센터:** 각 시도 교육청에서 운영하며 교원들의 심리적 어려움을 지원합니다. (해당 지역 교육청 웹사이트 참고)
    * **국가트라우마센터:** 재난 및 외상 후 스트레스 관리를 위한 전문 상담을 제공합니다. [국가트라우마센터](https://www.nct.go.kr/)
    * **정신건강복지센터:** 지역사회 기반의 정신건강 증진 및 상담 서비스를 제공합니다. (거주 지역 정신건강복지센터 검색)
    """)

    st.warning("⚠️ **면책 조항:** 본 웹사이트의 진단 결과는 자가 진단을 위한 참고 자료이며, 전문적인 의학적 또는 심리적 진단을 대체할 수 없습니다. 정확한 진단과 상담을 위해서는 반드시 전문가와 상의하시기 바랍니다.")

    st.button("다시 설문하기", on_click=go_to_page, args=('main',))

# --- 9. 메인 앱 실행 로직 ---
if st.session_state.page == 'main':
    main_page()
elif st.session_state.page == 'survey':
    survey_page()
elif st.session_state.page == 'result':
    result_page()
