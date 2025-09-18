import streamlit as st
from streamlit_chat import message
import base64
import io
import rag_funcs


# 1. 벡터 DB 객체 생성 (생성되어 있는 벡터 db 로딩)
vector_db = rag_funcs.load_vector_db()

# 2. RAG 체인 구성
rag_chain = rag_funcs.get_rag_chain_with_json_output(vector_db)


# Helper Function to Encode Image
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

#----------------- 사용자 UI & 로직 ------------------#
# --- Page Setup and Custom CSS ---
st.set_page_config(layout="wide")

# This is where all the custom CSS lives
st.markdown("""
<style>
    .st-emotion-cache-1cypcdp {
        flex-direction: row-reverse;
        justify-content: flex-end;
    }
    .st-emotion-cache-163e52v {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .st-emotion-cache-5k619m {
        display: none;
    }
    .example-question {
        background-color: #e0e0e0;
        border-radius: 12px;
        padding: 8px 12px;
        margin: 5px;
        cursor: pointer;
        font-size: 14px;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Encode your local logo file
logo_base64 = get_img_as_base64("images/logo.png")
if logo_base64 is None:
    st.error("Error: 'images/logo.png' not found. Please check the file path.")
    st.stop()

# --- Header Section with Logo and Button ---
st.markdown(f"""
    <div style="display: flex; align-items: center; height: 100%;">
        <img src="data:image/png;base64,{logo_base64}" style="height: 50px; margin-right: 15px;">
        <h1 style="font-size: 36px; margin: 0;">FeelKo</h1>

     <div style="display: flex; justify-content: flex-end; align-items: right; height: 100%;">
        <button style="
            background-color: #f0f2f6;
            border: 1px solid #c9c9c9;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        ">주인공과 찰칵</button>
        </div>
    </div>
""", unsafe_allow_html=True)


# 화면에 보여주기 위해 챗봇의 답변을 저장할 공간 할당
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

# 화면에 보여주기 위해 사용자의 질문을 저장할 공간 할당
if 'past' not in st.session_state:
    st.session_state['past'] = []

# 사용자의 입력이 들어오면 user_input에 저장하고 Send 버튼을 클릭하면
# submitted의 값이 True로 변환.
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('여행하고 싶은 드라마 명장면 여행지를 입력해 주세요.!', '', key='input')
    submitted = st.form_submit_button('Send')

# submitted의 값이 True면 챗봇이 답변을 하기 시작
if submitted and user_input:
    
    # 생성한 프롬프트를 기반으로 챗봇 답변을 생성
    chatbot_response = rag_funcs.run_rag_query(rag_chain, user_input)

    # 화면에 보여주기 위해 사용자의 질문과 챗봇의 답변을 각각 저장
    st.session_state['past'].append(user_input)
    st.session_state['generated'].append(chatbot_response)

# 챗봇의 답변이 있으면 사용자의 질문과 챗봇의 답변을 가장 최근의 순서로 화면에 출력
if st.session_state['generated']:
    for i in reversed(range(len(st.session_state['generated']))):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state['generated'][i], key=str(i))