import streamlit as st
import openai
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (API 키 보안을 위해 권장)
load_dotenv()

# 환경 변수에서 OpenAI API 키 가져오기
# Streamlit Community Cloud에 배포할 경우, st.secrets 사용을 권장합니다.
# openai_api_key = st.secrets["OPENAI_API_KEY"]
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key)
else:
    st.error("OpenAI API 키를 찾을 수 없습니다. '.env' 파일 또는 'st.secrets'를 확인하세요.")
    client = None

# Streamlit 앱 설정
st.set_page_config(
    page_title="교사용 공문서 자동 생성기",
    layout="centered"
)

st.title("📄 교사용 공문서 자동 생성기")
st.markdown("---")

# 사용자 입력: 공문 주제
doc_topic = st.text_input(
    "**생성할 공문의 주제를 입력하세요. (예: 1학년 현장체험학습 관련 안내)**",
    placeholder="예시: 2025학년도 2학기 학교폭력 예방 교육 실시"
)

# 사용자 입력: 추가 정보 (선택 사항)
additional_info = st.text_area(
    "**본문에 포함하고 싶은 추가 정보 (선택 사항)**",
    placeholder="예시: 일시, 장소, 대상 등 세부 정보",
    height=100
)

# 공문 생성 함수
def generate_official_document(topic, info=""):
    if not client:
        return "API 클라이언트가 초기화되지 않았습니다. API 키를 확인하세요."

    # 공문서 생성을 위한 프롬프트 구성
    # 교사용 공문서 스타일과 내용을 지정하여 모델의 응답 품질을 높입니다.
    system_prompt = (
        "당신은 학교 교사 및 행정 직원을 위한 공문서를 작성하는 전문 비서입니다. "
        "다음 내용을 바탕으로 **교내용 또는 학부모/학생 대상 안내용 공문서 본문**을 "
        "정중하고 명확하며 공식적인 어투로 작성해 주세요. "
        "공문서의 기본 구조(관련근거, 세부 내용 등)를 갖추되, 불필요한 서식은 제외하고 본문 내용만 작성합니다."
    )
    
    user_content = f"주제: {topic}\n\n[추가 정보]\n{info if info else '없음'}\n\n상황에 맞는 공문서 본문을 작성해 주세요."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 더 나은 품질을 위해 'gpt-4o' 또는 'gpt-4-turbo' 권장
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7 # 창의성 조절
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API 호출 중 오류 발생: {e}"

# 버튼 클릭 시 공문 생성
if st.button("🚀 공문서 본문 생성하기", type="primary", use_container_width=True):
    if doc_topic:
        with st.spinner('AI가 공문서 본문을 작성 중입니다... 잠시만 기다려 주세요.'):
            generated_text = generate_official_document(doc_topic, additional_info)
            
            st.markdown("---")
            st.subheader("✅ 생성된 공문서 본문")
            
            # 생성된 텍스트를 텍스트 영역에 표시 (복사 용이)
            st.code(generated_text, language="text")
            
            st.download_button(
                label="📄 텍스트 파일로 다운로드",
                data=generated_text.encode('utf-8'),
                file_name=f"{doc_topic.replace(' ', '_')}_공문서_본문.txt",
                mime="text/plain"
            )

    else:
        st.warning("먼저 공문의 주제를 입력해 주세요.")
