import streamlit as st
import base64
import io

# Helper Function to Encode Image
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

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


st.markdown("---")
st.write("- 드라마와 명장면 여행지를 입력하세요.")

# --- Chat Interface (Display history first) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])




# --- User Input Section ---
col1, col2 = st.columns([1, 0.05])
with col1:
    # Text input for the user's question
    if user_input := st.chat_input("질문을 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # Placeholder for your LLM call
                bot_response = f"귀하의 질문: '{user_input}'에 대한 LLM 답변입니다."
                st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
with col2:
    # Microphone button for voice input
    voice_input = st.button("🎤", key="voice_input")



st.markdown("---")
# --- Example Questions Section (첫 화면에서만 표시) ---
# 메시지가 없을 때만 질문 예시를 보여줌
if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns(3)
    
    # The example buttons will now trigger a new chat input
    with col1:
        if st.button("캐더헌에 나오는 명소를 알려줘", key="example1"):
            st.session_state.messages.append({"role": "user", "content": "캐더헌에 나오는 명소를 알려줘"})
            st.rerun()
    
    with col2:
        if st.button("내가 있는 위치 주변의 명소를 알려줘", key="example2"):
            st.session_state.messages.append({"role": "user", "content": "내가 있는 위치 주변의 명소를 알려줘"})
            st.rerun()
    
    with col3:
        if st.button("현재 위치에서 캐더헌에 나오는 명소가 있는지 알려줘", key="example3"):
            st.session_state.messages.append({"role": "user", "content": "현재 위치에서 캐더헌에 나오는 명소가 있는지 알려줘"})
            st.rerun()



#########################################
# import streamlit as st
# import io

# # Set up the page configuration
# st.set_page_config(page_title="캐릭터챗봇", page_icon="🤖")

# # --- UI Components ---
# # Custom CSS for a clean look
# st.markdown("""
# <style>
#     .st-emotion-cache-1cypcdp {
#         flex-direction: row-reverse;
#         justify-content: flex-end;
#     }
#     .st-emotion-cache-163e52v {
#         background-color: #f0f2f6;
#         padding: 1rem;
#         border-radius: 0.5rem;
#     }
#     .st-emotion-cache-5k619m {
#         display: none;
#     }
#     .example-question {
#         background-color: #e0e0e0;
#         border-radius: 12px;
#         padding: 8px 12px;
#         margin: 5px;
#         # display: inline-block;
#         cursor: pointer;
#         font-size: 14px;
#     }
# </style>
# """, unsafe_allow_html=True)



# import streamlit as st
# import base64

# # --- Helper Function to Encode Image ---
# # This function reads an image file and converts it into a Base64 string.
# def get_img_as_base64(file_path):
#     with open(file_path, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# # Encode your local logo.png file
# logo_base64 = get_img_as_base64("images/logo.png")

# # --- Page Setup ---
# st.markdown(f"""
#     <div style="display: flex; align-items: center; height: 80%; width:100%">
#         <img src="data:images/png;base64,{logo_base64}" style="height: 40px; margin-right: 0px;">
#         <h1 style="font-size: 36px; margin: 0;">FeelKo</h1>
#         <div style="display: flex; justify-content: flex-end; align-items: right; height: 80%; width:50%">
#             <button style="
#                 background-color: #f0f2f6;
#                 border: 1px solid #c9c9c9;
#                 border-radius: 10px;
#                 padding: 15px 20px;
#                 font-size: 16px;
#                 cursor: pointer;
#             ">주인공과 찰칵</button>
#         </div>
#     </div>
# """, unsafe_allow_html=True)

# st.markdown("---")
# # You can add the rest of your app content here
# st.write("드라마와 명장면 여행지를 입력하세요.")

# # --- Chat Interface ---
# # Initialize chat history in session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # --- User Input Section ---
# # Placeholder for the user's input
# user_input_placeholder = st.empty()

# with user_input_placeholder.container():
#     col1, col2 = st.columns([1, 0.05])
#     with col1:
#         # Text input for the user's question
#         user_input = st.chat_input("질문을 입력하세요...", key="text_input")
#     with col2:
#         # Microphone button for voice input
#         voice_input = st.button("🎤", key="voice_input")


# # --- Example Questions ---
# st.markdown("---")
# st.subheader("질문 예시")
# col1, col2, col3 = st.columns(3)

# with col1:
#     if st.button("캐더헌에 나오는 명소를 알려줘", key="example1"):
#         user_input = "캐더헌에 나오는 명소를 알려줘"
# with col2:
#     if st.button("내가 있는 위치 주변의 명소를 알려줘", key="example2"):
#         user_input = "내가 있는 위치 주변의 명소를 알려줘"
# with col3:
#     if st.button("현재 위치에서 캐더헌에 나오는 명소가 있는지 알려줘", key="example3"):
#         user_input = "현재 위치에서 캐더헌에 나오는 명소가 있는지 알려줘"

# # --- Logic to handle input ---
# if user_input:
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(user_input)

#     # Simulate a bot response (you'll replace this with your actual logic)
#     with st.chat_message("assistant"):
#         with st.spinner("생각 중..."):
#             # This is where you would call your LLM or chatbot model
#             bot_response = f"귀하의 질문: '{user_input}'에 대한 답변입니다."
#             st.markdown(bot_response)
        
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": bot_response})

