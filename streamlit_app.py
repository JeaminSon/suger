import streamlit as st
import requests

# 페이지 설정
st.set_page_config(page_title="당뇨 관리 AI 비서", page_icon="💊", layout="wide")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# 앱 타이틀
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

    # 사용자 입력 처리
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 약물 목록 처리
        medications_list = []
        if st.session_state.user_info["medications"]:
            medications_list = [med for med in st.session_state.user_info["medications"].split("\n") if med.strip()]
        
        # 특이사항 처리
        special_notes = st.session_state.user_info["special_notes"] if st.session_state.user_info["special_notes"] else "특이사항 없음"
        
        # MCP 프롬프트 구성
        mcp_prompt = f"""
        <system>
        당신은 당뇨 환자를 위한 개인 건강 관리 비서입니다. 친절하고 이해하기 쉬운 말로 의학적으로 정확한 조언을 제공하세요.
        환자가 위험한 상황에 처했다고 판단되면 즉시 의사와 상담하라고 권고하세요.
        고혈당 및 저혈당 증상, 약물 정보, 식이요법, 운동 등에 관한 전문적인 지식을 바탕으로 응답하세요.
        </system>
        
        <user_profile>
        이름: {st.session_state.user_info["name"] if st.session_state.user_info["name"] else "사용자"}
        나이: {st.session_state.user_info["age"]}세
        성별: {st.session_state.user_info.get("gender", "미지정")}
        키: {st.session_state.user_info["height"]}cm
        체중: {st.session_state.user_info["weight"]}kg
        당뇨 유형: {st.session_state.user_info["diabetes_type"]}
        진단 시기: {st.session_state.user_info["diagnosis_year"]}년
        최근 혈당 수치: {st.session_state.user_info["recent_glucose"]} mg/dL
        목표 혈당 범위: {st.session_state.user_info["target_glucose"]} mg/dL
        현재 약물: {', '.join(medications_list) if medications_list else "없음"}
        특이사항: {special_notes}
        </user_profile>
        
        <chat_history>
        {chr(10).join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])}
        </chat_history>
        
        <query>
        {prompt}
        </query>
        """
        
        # AI 응답 생성
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    message_placeholder.markdown("🤔 생각 중...")
    
    try:
        # Hugging Face API 호출
        output = query({
            "inputs": mcp_prompt,
            "parameters": {"max_new_tokens": 512, "temperature": 0.7}
        })
        
        # 응답 처리
        if isinstance(output, dict) and 'error' in output:
            full_response = f"모델 로딩 중 오류: {output['error']}"
        else:
            # 일반적인 응답 형식 처리
            full_response = output[0]['generated_text']
            # 입력 프롬프트 부분 제거
            full_response = full_response.replace(mcp_prompt, "").strip()
            
        message_placeholder.markdown(full_response)
    except Exception as e:
        full_response = "죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        message_placeholder.markdown(full_response)
        st.error(f"오류 발생: {str(e)}")
        
        # 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": full_response})
