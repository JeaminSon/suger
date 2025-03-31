import streamlit as st
import requests
import os
import time
# 페이지 설정
st.set_page_config(page_title="당뇨 관리 AI 비서", page_icon="💊", layout="wide")
# Hugging Face API 설정
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# API 키를 직접 입력 (테스트용, 실제로는 st.secrets 사용 권장)
API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")

if not API_KEY and hasattr(st, 'secrets') and "HUGGINGFACE_API_KEY" in st.secrets:
    API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
headers = {"Authorization": f"Bearer {API_KEY}"}
def query_with_retry(prompt, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 200:
                try:
                    result = response.json()
                    # 응답 구조 확인
                    print("응답 구조:", result)
                    
                    # 응답에서 생성된 텍스트 추출
                    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                        generated_text = result[0]["generated_text"]
                        # 생성된 텍스트 표시 또는 처리
                        print("생성된 텍스트:", generated_text)
                        return generated_text  # 성공적인 응답 반환
                    else:
                        print("예상치 못한 응답 형식:", result)
                        return f"예상치 못한 응답 형식: {result}"
                except Exception as e:
                    print("응답 처리 중 오류:", str(e))
                    return f"응답 처리 중 오류: {str(e)}"
            elif response.status_code == 503:
                print(f"서비스 일시 중단 (503). {delay}초 후 재시도 ({attempt+1}/{max_retries})...")
                time.sleep(delay)
                delay *= 2  # 지수 백오프
            elif response.status_code == 500:
                print(response.text)
                if attempt == max_retries - 1:  # 마지막 시도인 경우
                    return f"서버 내부 오류 (500): {response.text[:100]}..."
                time.sleep(delay)  # 재시도 전 대기
            else:
                return f"오류 발생: HTTP {response.status_code}"
        except Exception as e:
            print(f"오류 발생: {str(e)}. 재시도 중...")
            if attempt == max_retries - 1:  # 마지막 시도인 경우
                return f"API 호출 중 오류: {str(e)}"
            time.sleep(delay)
    
    return "최대 재시도 횟수를 초과했습니다. 나중에 다시 시도해주세요."
    
    return "최대 재시도 횟수를 초과했습니다. 나중에 다시 시도해주세요."
def query_huggingface(prompt):
    """Hugging Face API 호출 함수"""
    try:
        response = requests.post(
           API_URL,
           headers=headers,
           json={"inputs": prompt},  # 가장 기본적인 형태로 단순화
           timeout=60
        )
        return response
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None

# try 블록 밖에 있어야 합니다
st.title("당뇨 관리 AI 비서")

# 사용자 정보 저장 세션 초기화
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "age": 50,
        "diabetes_type": "제2형 당뇨",
        "diagnosis_year": 2020,
        "medications": "",
        "recent_glucose": 120,
        "target_glucose": "80-140",
        "height": 170,
        "weight": 70,
        "special_notes": ""
    }

# 탭 생성: 메인 채팅, 사용자 정보 설정
tab1, tab2 = st.tabs(["💬 채팅", "👤 내 정보 설정"])

# 사용자 정보 설정 탭
with tab2:
    st.header("내 건강 정보")
    st.info("아래 정보를 입력하면 더 정확하고 개인화된 답변을 받을 수 있습니다. 모든 정보는 브라우저 세션에만 저장되며 서버에 저장되지 않습니다.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보")
        st.session_state.user_info["name"] = st.text_input("이름", st.session_state.user_info["name"])
        st.session_state.user_info["age"] = st.number_input("나이", 1, 120, st.session_state.user_info["age"])
        st.session_state.user_info["gender"] = st.radio("성별", ["남성", "여성"], horizontal=True)
        st.session_state.user_info["height"] = st.number_input("키 (cm)", 100, 250, st.session_state.user_info["height"])
        st.session_state.user_info["weight"] = st.number_input("체중 (kg)", 30, 200, st.session_state.user_info["weight"])
        
    with col2:
        st.subheader("당뇨 관련 정보")
        st.session_state.user_info["diabetes_type"] = st.selectbox(
            "당뇨 유형", 
            ["제1형 당뇨", "제2형 당뇨", "임신성 당뇨", "기타"], 
            index=["제1형 당뇨", "제2형 당뇨", "임신성 당뇨", "기타"].index(st.session_state.user_info["diabetes_type"])
        )
        st.session_state.user_info["diagnosis_year"] = st.number_input(
            "진단 연도", 1950, 2025, st.session_state.user_info["diagnosis_year"]
        )
        st.session_state.user_info["recent_glucose"] = st.number_input(
            "최근 혈당 수치 (mg/dL)", 40, 500, st.session_state.user_info["recent_glucose"]
        )
        st.session_state.user_info["target_glucose"] = st.text_input(
            "목표 혈당 범위 (예: 80-140)", st.session_state.user_info["target_glucose"]
        )
    
    st.subheader("복용 중인 약물")
    st.session_state.user_info["medications"] = st.text_area(
        "약물 이름과 용량을 한 줄에 하나씩 입력하세요", 
        st.session_state.user_info["medications"],
        placeholder="예시:\n메트포민 500mg\n글리메피리드 2mg"
    )
    
    st.subheader("특이사항")
    st.session_state.user_info["special_notes"] = st.text_area(
        "알레르기, 합병증, 기타 건강 상태 등", 
        st.session_state.user_info["special_notes"],
        placeholder="예시:\n고혈압 있음\n저혈당 발생 이력\n신장 기능 저하"
    )
    
    if st.button("저장", type="primary"):
        st.success("정보가 저장되었습니다!")

# 채팅 탭
with tab1:
    # 사용자 정보 요약 표시 (접을 수 있는 섹션)
    with st.expander("내 정보 요약"):
        if st.session_state.user_info["name"]:
            st.write(f"**이름**: {st.session_state.user_info['name']}")
        st.write(f"**나이**: {st.session_state.user_info['age']}세")
        if "gender" in st.session_state.user_info:
            st.write(f"**성별**: {st.session_state.user_info['gender']}")
        st.write(f"**당뇨 유형**: {st.session_state.user_info['diabetes_type']}")
        st.write(f"**진단 연도**: {st.session_state.user_info['diagnosis_year']}년")
        st.write(f"**최근 혈당**: {st.session_state.user_info['recent_glucose']} mg/dL")
        st.write(f"**목표 혈당 범위**: {st.session_state.user_info['target_glucose']} mg/dL")
        if st.session_state.user_info["medications"]:
            st.write("**복용 중인 약물**:")
            for med in st.session_state.user_info["medications"].split("\n"):
                if med.strip():
                    st.write(f"- {med}")

    # 채팅 이력을 저장할 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 당뇨 관리와 관련해 어떤 도움이 필요하신가요?"}
        ]

    # 이전 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 처리 부분
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 키워드 기반 응답 시스템
    response_text = get_diabetes_response(prompt.lower())
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(response_text)
        
        # 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# 키워드 기반 응답 함수
def get_diabetes_response(query):
    # 식이요법 관련 키워드
    if any(word in query for word in ["먹", "식사", "식이", "음식", "식단", "영양"]):
        return """당뇨 관리를 위한 식이요법 팁입니다:
        
1. 탄수화물 섭취를 조절하고 복합 탄수화물(현미, 통곡물 등)을 선택하세요.
2. 식이섬유가 풍부한 채소를 충분히 섭취하세요.
3. 단백질 섭취를 적절히 유지하세요(살코기, 생선, 콩류, 저지방 유제품).
4. 지방은 불포화지방(올리브유, 아보카도, 견과류)을 선택하세요.
5. 규칙적인 식사 시간을 유지하고 과식을 피하세요.
6. 식사 후 2시간 혈당을 측정하여 특정 음식이 혈당에 미치는 영향을 파악하세요."""

    # 운동 관련 키워드
    elif any(word in query for word in ["운동", "활동", "걷", "근력", "체중"]):
        return """당뇨 환자에게 권장되는 운동 가이드라인:
        
1. 일주일에 최소 150분의 중강도 유산소 운동을 하세요(걷기, 수영, 자전거 등).
2. 주 2-3회 근력 운동을 포함하세요.
3. 운동 전후로 혈당을 측정하여 변화를 모니터링하세요.
4. 운동 중 저혈당 위험에 대비해 간식을 준비하세요.
5. 운동 강도는 점진적으로 늘리고 무리하지 마세요.
6. 발 관리에 특별히 주의하고 적절한 신발을 착용하세요."""

    # 혈당 관리 관련 키워드
    elif any(word in query for word in ["혈당", "당뇨", "수치", "모니터", "측정"]):
        return """효과적인 혈당 관리 방법:
        
1. 정기적으로 혈당을 측정하고 기록하세요(식전, 식후 2시간, 취침 전).
2. 목표 혈당 범위(80-140 mg/dL)를 유지하도록 노력하세요.
3. 3개월마다 당화혈색소(HbA1c) 검사를 받으세요.
4. 혈당 패턴을 분석하여 조절이 필요한 생활습관을 파악하세요.
5. 스트레스가 혈당에 미치는 영향을 인지하고 관리하세요.
6. 혈당이 지속적으로 목표 범위를 벗어나면 의사와 상담하세요."""

    # 일반적인 질문이나 "뭘 해야 하나요" 유형의 질문
    else:
        return """당뇨 관리를 위한 기본 지침:
        
1. 정기적인 혈당 모니터링: 식전, 식후 2시간, 취침 전에 측정하세요.
2. 균형 잡힌 식단: 탄수화물을 조절하고, 식이섬유가 풍부한 음식을 섭취하세요.
3. 규칙적인 운동: 주 5일, 하루 30분 이상의 중강도 운동을 목표로 하세요.
4. 체중 관리: 건강한 체중을 유지하도록 노력하세요.
5. 정기적인 건강 검진: 3-6개월마다 의사를 방문하여 당화혈색소 검사를 받으세요.
6. 발 관리: 매일 발을 점검하고 적절한 신발을 착용하세요.
7. 스트레스 관리: 스트레스는 혈당에 영향을 줄 수 있으므로 관리가 중요합니다.

현재 혈당이 120 mg/dL로 목표 범위(80-140 mg/dL) 내에 있어 잘 관리되고 있습니다. 계속해서 좋은 생활습관을 유지하세요."""