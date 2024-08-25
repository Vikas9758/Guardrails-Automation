import streamlit as st
from contents import ask_model, apply_guardrails, sanitize_text
import time
import asyncio
# Streamlit App configuration
st.set_page_config(page_title="Chatbot with Guardrails 🛡️", page_icon="💬", layout="centered")
import os


# Function to save conversation history to a file
def save_conversation_to_file(conversation_history):
    # Ensure the 'chat' folder exists
    if not os.path.exists("chat"):
        os.makedirs("chat")

    # Generate a filename based on the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"chat/conversation_{timestamp}.txt"

    # Write the conversation history to the file
    with open(filename, "w") as file:
        for convo in conversation_history:
            file.write(f"You: {convo['question']}\n")
            file.write(f"Bot (No Guardrails): {convo['raw_answer']}\n")
            file.write(f"Bot (With Guardrails): {convo['guarded_answer']}\n")
            file.write("\n---\n\n")


# Function to clear conversation history
def clear_conversation():
    if st.session_state.conversation_history:
        save_conversation_to_file(st.session_state.conversation_history)
    st.session_state.conversation_history = []
    st.success("Conversation history saved and cleared.")

def apply_guardrail(names,detail,inp,out,m_nam,apk):
    rails,ccnt = asyncio.run(apply_guardrails(names,detail,inp,out,m_nam,apk))
    return rails,ccnt

# Custom CSS for chat UI
st.markdown("""
    <style>
    /* General body style */
    body {
        background-color: #f5f5f5;
    }

    /* Chat message styles */
    .user-message {
        background-color: #d1e7dd;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
        color: #0f5132;
        width: fit-content;
        max-width: 70%;
        font-family: sans-serif;
    }

    .bot-message {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
        color: #343a40;
        width: fit-content;
        max-width: 70%;
        font-family: sans-serif;
    }

    /* Align user messages to the right */
    .user-message-container {
        display: flex;
        justify-content: flex-end;
    }

    /* Align bot messages to the left */
    .bot-message-container {
        display: flex;
        justify-content: flex-start;
    }

    /* Custom button styling */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 12px;
        padding: 10px 15px;
    }

    .stButton>button:hover {
        background-color: #0056b3;
    }

    /* Text area styling */
    textarea {
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #ced4da;
        width: 100%;
    }

    /* Hide the submit button only */
    .stForm button[type="submit"] {
        display: none;
    }
    </style>
    <script>
    // JavaScript to handle Enter key press for form submission
    document.addEventListener('DOMContentLoaded', function() {
        var form = document.querySelector('form');
        if (form) {
            form.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    form.querySelector('button[type="submit"]').click();
                }
            });
        }
    });
    </script>
""", unsafe_allow_html=True)

# Initialize session state for guardrails and conversation
if "rails" not in st.session_state:
    st.session_state.rails = None
    st.session_state.guardrails_applied = False
    st.session_state.question = ""
    st.session_state.conversation_history = []
    st.session_state.info=""
    st.session_state.api_key=""


# Conditional rendering based on guardrails being applied
if not st.session_state.guardrails_applied:
    st.title("Guardrail Automation 🛡️")
    st.header("🚧 Apply Guardrails Before Chatting")
    st.write("Provide project details and set up guardrails before starting the conversation:")

    # Input fields for project setup
    st.session_state.api_key=st.text_input("Enter your Groq Api Key",value=st.session_state.get("api_key",""))
    st.session_state.name = st.text_input("📋 Project Name", value=st.session_state.get("name", ""))
    st.session_state.details = st.text_area("📝 Project Details", value=st.session_state.get("details", ""))
    st.session_state.for_input = st.text_area("🚧 Input Guardrails", value=st.session_state.get("for_input", ""))
    st.session_state.for_output = st.text_area("🔒 Output Guardrails", value=st.session_state.get("for_output", ""))
    format_options=["string","json"]
    st.session_state.output_format = st.selectbox("🔍 Choose an output format", format_options)
    # Submit button to apply guardrails
    if st.button("Submit"):
        st.write("### Submitted Details:")
        st.write(f"**Project Name:** {st.session_state.name}")
        st.write(f"**Project Details:** {st.session_state.details}")
        st.write(f"**Input Guardrails:** {st.session_state.for_input}")
        st.write(f"**Output Guardrails:** {st.session_state.for_output}")

    # LLM selection dropdown
    llm_options = ["gemma-7b-it","gemma2-9b-it", "llama-3.1-8b-instant","llama3-8b-8192","llama3-70b-8192","mixtral-8x7b-32768"]
    st.session_state.selected_llm = st.selectbox("🔍 Choose an LLM", llm_options)

    # Button to apply guardrails and move to chat
    if st.button("🚀 Apply Guardrails"):
        st.session_state.rails,cnt = apply_guardrail(names=st.session_state.name, detail=st.session_state.details, inp=st.session_state.for_input,
                                                       out=st.session_state.for_output, m_nam=st.session_state.selected_llm,apk=st.session_state.api_key)
        st.write("### Input and Output Rails")
        st.write(cnt)
        st.session_state.guardrails_applied = True
        st.success("Guardrails Applied Successfully ✅")
        if st.button("Start Conversation"):
            st.rerun()

else:
    st.title("Chatbot with Guardrails 🛡️")
    # Display conversation history
    st.header("💬 Chat")
    if st.session_state.conversation_history:
        for convo in st.session_state.conversation_history:
            # User message
            st.markdown(f"""
            <div class="user-message-container">
                <div class="user-message"><strong>You:</strong><br>{convo['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)

            with col1:
                # Bot response without guardrails
                st.markdown(f"""
                <div class="bot-message-container">
                    <div class="bot-message"><strong>Bot (No Guardrails):</strong><br>{convo['raw_answer']} </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Bot response with guardrails
                st.markdown(f"""
                <div class="bot-message-container">
                    <div class="bot-message"><strong>Bot (With Guardrails):</strong><br>{convo['guarded_answer']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Input area for user's question
    with st.form(key="chat_form", clear_on_submit=True):
        st.session_state.question = st.text_area("💬 Type your message here:")

        # Process input and get answers
        if st.form_submit_button("Submit"):
            st.session_state.question = sanitize_text(st.session_state.question)
            if st.session_state.question != "":
                # Get raw and guarded answers
                st1 = time.time()
                if st.session_state.details:
                    raw_answer = asyncio.run(ask_model(st.session_state.details+"\n"+st.session_state.question, st.session_state.selected_llm,st.session_state.output_format))
                else:
                    raw_answer = asyncio.run(ask_model(st.session_state.question, st.session_state.selected_llm,st.session_state.output_format,st.session_state.api_key))
                t1 = time.time() - st1
                st2 = time.time()
                guarded_answer = st.session_state.rails.generate(messages=[{"role": 'user', "content": st.session_state.question}])['content']
                t2 = time.time() - st2
                st.session_state.info=st.session_state.rails.explain()
                if guarded_answer == "I'm sorry, I can't respond to that.":
                    guarded_answer="Reason for blocking the user message: "+st.session_state.info.llm_calls[0].completion
                guarded_answer += "\n" + f" time_taken : {t2}"
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "question": st.session_state.question,
                    "raw_answer": raw_answer.content+"\n" + f" time_taken : {t1}",
                    "guarded_answer": guarded_answer
                })
                # Refresh page to show the new conversation
                st.rerun()
    if st.button("Edit Guardrails"):
        st.session_state.rails = None
        st.session_state.guardrails_applied = False
        st.session_state.question = ""
        st.session_state.info=""
        st.session_state.conversation_history = []
        st.rerun()

    if st.button("🗑️ Clear Conversation History"):
        clear_conversation()
        st.rerun()
