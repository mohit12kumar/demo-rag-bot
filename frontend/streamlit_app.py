import os
import streamlit as st
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ==========================================
# PAGE CONFIG & CUSTOM CSS
# ==========================================

st.set_page_config(
    page_title="AI Study Library",
    page_icon="📚",
    layout="wide"
)

# Inject custom CSS for premium styling (Now managed natively via .streamlit/config.toml)
# Note: Fonts and background styling are defined in .streamlit/config.toml


# ==========================================
# BACKEND CONNECTION CHECK
# ==========================================
try:
    health_check = requests.get(f"{API_URL}/health", timeout=3)
    backend_connected = (health_check.status_code == 200)
except Exception:
    backend_connected = False

if not backend_connected:
    st.error("🚨 **Error: Backend API server is offline or unreachable.**")
    st.info(f"Make sure your FastAPI server is running at **{API_URL}** before using the Streamlit dashboard.")
    st.markdown("""
    **To start the project:**
    Double-click the **`run.bat`** file in the project folder to automatically spin up both the FastAPI backend and Streamlit frontend.
    """)
    st.stop()

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "documents" not in st.session_state:
    st.session_state.documents = []

if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None

if "quiz_user_answers" not in st.session_state:
    st.session_state.quiz_user_answers = {}

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None

if "revision_plan" not in st.session_state:
    st.session_state.revision_plan = None

if "revision_completed" not in st.session_state:
    st.session_state.revision_completed = {}


# ==========================================
# API HELPER FUNCTIONS
# ==========================================

def get_auth_headers():
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers


def fetch_documents():
    if not st.session_state.user:
        st.session_state.documents = []
        return
    try:
        response = requests.get(
            f"{API_URL}/upload/",
            headers=get_auth_headers()
        )
        if response.status_code == 200:
            st.session_state.documents = response.json()
        else:
            st.session_state.documents = []
    except Exception:
        st.session_state.documents = []


# ==========================================
# SIDEBAR AUTHENTICATION
# ==========================================

st.sidebar.title("📚 AI Study Library")
st.sidebar.markdown("### 🔐 User Session")

if st.session_state.user:
    st.sidebar.success(f"Hello, {st.session_state.user['name']}!")
    
    # Load user documents
    if not st.session_state.documents:
        fetch_documents()
        
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.documents = []
        st.session_state.quiz_questions = None
        st.session_state.flashcards = None
        st.session_state.revision_plan = None
        st.session_state.revision_completed = {}
        st.rerun()
else:
    auth_tab1, auth_tab2 = st.sidebar.tabs(["Login", "Register"])
    
    # Login Tab
    with auth_tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.warning("Please enter credentials.")
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.token = data["access_token"]
                        st.session_state.user = data["user"]
                        fetch_documents()
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login failed."))
                except Exception as e:
                    st.error(f"Network error: {e}")
                    
    # Register Tab
    with auth_tab2:
        reg_name = st.text_input("Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            if not reg_name or not reg_email or not reg_pass:
                st.warning("All fields are required.")
            else:
                try:
                    res = requests.post(f"{API_URL}/auth/register", json={"name": reg_name, "email": reg_email, "password": reg_pass})
                    if res.status_code == 200:
                        st.success("Successfully registered! You can login now.")
                    else:
                        st.error(res.json().get("detail", "Registration failed."))
                except Exception as e:
                    st.error(f"Network error: {e}")

# --- Uploaded Files Library ---
if st.session_state.user:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 My Document Library")
    
    if st.session_state.documents:
        for doc in st.session_state.documents:
            doc_id = doc["id"]
            doc_name = doc["document_name"]
            doc_type = doc["document_type"]
            
            cols = st.sidebar.columns([4, 1])
            with cols[0]:
                icon = "📄" if doc_type != "youtube" else "🎥"
                st.markdown(f"**{icon} {doc_name}**")
            with cols[1]:
                if st.button("🗑️", key=f"del_{doc_id}", help="Delete this file"):
                    try:
                        res = requests.delete(
                            f"{API_URL}/upload/{doc_id}",
                            headers=get_auth_headers()
                        )
                        if res.status_code == 200:
                            st.sidebar.success("Deleted!")
                            fetch_documents()
                            st.rerun()
                        else:
                            st.sidebar.error("Error deleting.")
                    except Exception as e:
                        st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.info("Your study library is empty. Upload files to get started!")


# ==========================================
# MAIN APPLICATION INTERFACE (GATED)
# ==========================================

st.title("📚 AI Study Library Dashboard")

if not st.session_state.user:
    st.warning("🔒 **Authentication Required**")
    st.info("Please log in or register from the sidebar to access your RAG study library, upload materials, ask questions, or generate study aids.")
    st.markdown("""
    ### Features of AI Study Library:
    - 📄 **Direct Library Management**: Upload notes and download/index YouTube transcripts.
    - 💬 **Ask Questions**: Query across your entire library with source citations (doc name + page number).
    - 📝 **Summaries & Revision Plans**: Automatically compile study topics into detailed plans and digests.
    - ❓ **Interactive Quizzes & Flashcards**: AI-powered study generators to practice what you've learned.
    """)
    st.stop()

# Main study tabs
tab_chat, tab_compare, tab_summary, tab_quiz, tab_flashcard, tab_revision = st.tabs([
    "💬 Ask Questions",
    "📊 Compare Concepts",
    "📝 Topic Summaries",
    "❓ MCQ Quizzes",
    "🧠 Flashcards",
    "📅 Revision Plans"
])


# ==========================================
# TAB 1: ASK QUESTIONS (RAG CHAT)
# ==========================================
with tab_chat:
    st.header("💬 Ask Questions & RAG Chat")
    
    # Query Scope Selector
    scope = st.radio(
        "Select search scope:",
        options=["🌐 Search All Documents", "📄 Search Specific Document Only"],
        horizontal=True
    )
    
    filter_doc_id = None
    if scope == "📄 Search Specific Document Only":
        if st.session_state.documents:
            doc_options = {d["document_name"]: d["id"] for d in st.session_state.documents}
            selected_doc_name = st.selectbox("Choose specific document:", options=list(doc_options.keys()))
            filter_doc_id = doc_options[selected_doc_name]
        else:
            st.info("No documents found in your library to select.")
            
    # Input area
    question = st.text_area(
        "Enter your question:",
        placeholder="What did I learn about virtual environments in python? Or: What have I learned so far in this course?",
        key="chat_question"
    )
    
    if st.button("Send Query", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Analyzing sources and synthesizing response..."):
                payload = {
                    "question": question,
                    "user_id": st.session_state.user["id"]
                }
                
                # Apply filter if specific document is selected
                if scope == "📄 Search Specific Document Only" and filter_doc_id:
                    payload["document_id"] = filter_doc_id
                    
                try:
                    res = requests.post(
                        f"{API_URL}/query/",
                        json=payload,
                        headers=get_auth_headers()
                    )
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.markdown("### 🤖 Response")
                        st.markdown(data.get("answer"))
                        
                        citations = data.get("citations", [])
                        if citations:
                            st.markdown("#### 🔗 Sources Cited")
                            badges_list = []
                            for cit in citations:
                                doc_name = cit.get("document", "Source")
                                page_num = cit.get("page", 1)
                                badges_list.append(f"📄 `{doc_name} (Page/Slide {page_num})`")
                            st.markdown(" ".join(badges_list))
                    else:
                        st.error("Failed to retrieve an answer from the backend.")
                except Exception as e:
                    st.error(f"Network error: {e}")

    # Section to Upload Files / YouTube
    st.markdown("---")
    st.subheader("📥 Add Materials to your Study Library")
    
    up_tab, yt_tab = st.tabs(["📄 Upload Notes/Slides (PDF, PPT, TXT)", "🎥 Import YouTube Transcript"])
    
    with up_tab:
        uploaded_files = st.file_uploader(
            "Choose PDF, PPTX or TXT files:",
            type=["pdf", "pptx", "txt"],
            accept_multiple_files=True
        )
        if uploaded_files:
            if st.button("Process & Upload All Files"):
                success_count = 0
                for file in uploaded_files:
                    files = {"file": (file.name, file.getvalue())}
                    try:
                        with st.spinner(f"Ingesting '{file.name}'..."):
                            res = requests.post(
                                f"{API_URL}/upload/",
                                files=files,
                                headers=get_auth_headers()
                            )
                            if res.status_code == 200:
                                success_count += 1
                            else:
                                st.error(f"Failed uploading '{file.name}': {res.text}")
                    except Exception as e:
                        st.error(f"Error uploading '{file.name}': {e}")
                
                if success_count > 0:
                    st.success(f"Successfully processed {success_count} file(s)!")
                    fetch_documents()
                    st.rerun()
                    
    with yt_tab:
        yt_input = st.text_input("Enter YouTube Video URL or Video ID:")
        if st.button("Import YouTube Transcript"):
            if not yt_input.strip():
                st.warning("Please enter a URL or Video ID.")
            else:
                with st.spinner("Downloading transcript from YouTube and indexing..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/upload/youtube",
                            json={
                                "url_or_id": yt_input.strip()
                            },
                            headers=get_auth_headers()
                        )
                        if res.status_code == 200:
                            st.success("YouTube transcript imported and indexed successfully!")
                            fetch_documents()
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Failed to fetch transcript."))
                    except Exception as e:
                        st.error(f"Network error: {e}")


# ==========================================
# TAB 2: COMPARE CONCEPTS
# ==========================================
with tab_compare:
    st.header("📊 Compare Concepts Side-by-Side")
    st.markdown("Enter two concepts or terms to compare them based on all files indexed in your library.")
    
    col1, col2 = st.columns(2)
    with col1:
        concept1 = st.text_input("Concept A:", key="c1")
    with col2:
        concept2 = st.text_input("Concept B:", key="c2")
        
    if st.button("Compare Concepts", type="primary", use_container_width=True):
        if not concept1.strip() or not concept2.strip():
            st.warning("Please fill in both concept inputs.")
        else:
            with st.spinner(f"Comparing '{concept1}' and '{concept2}'..."):
                try:
                    res = requests.post(
                        f"{API_URL}/query/compare",
                        json={
                            "concept1": concept1,
                            "concept2": concept2,
                            "user_id": st.session_state.user["id"]
                        },
                        headers=get_auth_headers()
                    )
                    if res.status_code == 200:
                        st.markdown("### 📊 AI Concept Comparison")
                        st.markdown(res.json().get("comparison"))
                    else:
                        st.error("Comparison request failed.")
                except Exception as e:
                    st.error(f"Network error: {e}")


# ==========================================
# TAB 3: TOPIC SUMMARIES
# ==========================================
with tab_summary:
    st.header("📝 Topic Summaries")
    st.markdown("Generate a detailed summary on any topic using all documents in your library.")
    
    sum_topic = st.text_input("Topic to Summarize:", placeholder="e.g. Git Branching, FastAPI Dependency Injection")
    if st.button("Generate Summary", type="primary", use_container_width=True):
        if not sum_topic.strip():
            st.warning("Please specify a topic.")
        else:
            with st.spinner("Synthesizing summary from indexed files..."):
                try:
                    res = requests.post(
                        f"{API_URL}/summary/",
                        json={
                            "topic": sum_topic
                        },
                        headers=get_auth_headers()
                    )
                    if res.status_code == 200:
                        st.markdown("### 📝 Generated Summary")
                        st.markdown(res.json().get("summary"))
                    else:
                        st.error("Failed to generate summary.")
                except Exception as e:
                    st.error(f"Network error: {e}")


# ==========================================
# TAB 4: MCQ QUIZZES
# ==========================================
with tab_quiz:
    st.header("❓ Quiz Generator")
    st.markdown("Test your understanding! Generate a multiple-choice quiz based on your library files.")
    
    quiz_topic = st.text_input("Quiz Topic:", placeholder="e.g. Python lists, FastAPI routers")
    
    col_g, col_c = st.columns([1, 4])
    with col_g:
        if st.button("Generate Quiz", key="btn_gen_quiz"):
            if not quiz_topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating quiz questions..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/quiz/",
                            json={
                                "topic": quiz_topic,
                                "num_questions": 5
                            },
                            headers=get_auth_headers()
                        )
                        if res.status_code == 200:
                            st.session_state.quiz_questions = res.json().get("quiz", [])
                            st.session_state.quiz_user_answers = {}
                            st.session_state.quiz_submitted = False
                        else:
                            st.error("Failed to generate quiz.")
                    except Exception as e:
                        st.error(f"Network error: {e}")
                        
    with col_c:
        if st.session_state.quiz_questions and st.button("Clear Quiz", key="btn_clear_quiz"):
            st.session_state.quiz_questions = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_user_answers = {}
            st.rerun()
            
    if st.session_state.quiz_questions:
        st.markdown(f"### ✏️ Active Quiz: **{quiz_topic}**")
        with st.form("main_quiz_form"):
            for idx, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{idx+1}:** {q['question']}")
                options = q.get("options", [])
                prev_val = st.session_state.quiz_user_answers.get(idx, None)
                
                ans = st.radio(
                    "Select the correct option:",
                    options=options,
                    index=options.index(prev_val) if prev_val in options else 0,
                    key=f"quiz_radio_{idx}"
                )
                st.session_state.quiz_user_answers[idx] = ans
                st.markdown("---")
                
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                st.session_state.quiz_submitted = True
                
        if st.session_state.quiz_submitted:
            st.markdown("### 📊 Quiz Results")
            correct = 0
            for idx, q in enumerate(st.session_state.quiz_questions):
                user_ans = st.session_state.quiz_user_answers.get(idx)
                correct_ans = q.get("answer")
                st.markdown(f"**Question {idx+1}:** {q['question']}")
                if user_ans == correct_ans:
                    correct += 1
                    st.success(f"Your answer: **{user_ans}** (Correct! ✔️)")
                else:
                    st.error(f"Your answer: **{user_ans}** (Incorrect ❌)")
                    st.info(f"Correct answer: **{correct_ans}**")
                st.markdown("---")
                
            score = (correct / len(st.session_state.quiz_questions)) * 100
            if score >= 70:
                st.balloons()
                st.success(f"🎉 **Excellent!** Score: **{correct}/{len(st.session_state.quiz_questions)}** ({score:.1f}%)")
            else:
                st.warning(f"📚 **Keep studying!** Score: **{correct}/{len(st.session_state.quiz_questions)}** ({score:.1f}%)")


# ==========================================
# TAB 5: FLASHCARDS
# ==========================================
with tab_flashcard:
    st.header("🧠 Study Flashcards")
    st.markdown("Review study terms! Generate and flip interactive flashcards from your library files.")
    
    fc_topic = st.text_input("Flashcard Topic:", placeholder="e.g. Git commands, API methods")
    
    col_fg, col_fc = st.columns([1, 4])
    with col_fg:
        if st.button("Generate Flashcards", key="btn_gen_fc"):
            if not fc_topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating flashcards..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/flashcards/",
                            json={
                                "topic": fc_topic
                            },
                            headers=get_auth_headers()
                        )
                        if res.status_code == 200:
                            st.session_state.flashcards = res.json().get("flashcards", [])
                        else:
                            st.error("Failed to generate flashcards.")
                    except Exception as e:
                        st.error(f"Network error: {e}")
                        
    with col_fc:
        if st.session_state.flashcards and st.button("Clear Flashcards", key="btn_clear_fc"):
            st.session_state.flashcards = None
            st.rerun()
            
    if st.session_state.flashcards:
        st.markdown(f"### 🧠 Active Deck: **{fc_topic}**")
        for idx, card in enumerate(st.session_state.flashcards):
            with st.container(border=True):
                st.markdown(f"#### 📌 Card {idx+1}")
                st.markdown(f"**Question:** {card.get('question')}")
                with st.expander("👁️ Show Answer"):
                    st.info(card.get("answer"))


# ==========================================
# TAB 6: REVISION PLANS
# ==========================================
with tab_revision:
    st.header("📅 Study Revision Plan")
    st.markdown("Get a day-by-day structured study schedule tailored to your topic and library files.")
    
    rev_topic = st.text_input("Study Plan Topic:", placeholder="e.g. Python web development, Git flow")
    
    col_rg, col_rc = st.columns([1, 4])
    with col_rg:
        if st.button("Generate Revision Plan", key="btn_gen_rev"):
            if not rev_topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Creating schedule plan..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/revision/",
                            json={
                                "topic": rev_topic,
                                "days": 5
                            },
                            headers=get_auth_headers()
                        )
                        if res.status_code == 200:
                            st.session_state.revision_plan = res.json().get("revision_plan", [])
                            st.session_state.revision_completed = {}
                        else:
                            st.error("Failed to generate revision plan.")
                    except Exception as e:
                        st.error(f"Network error: {e}")
                        
    with col_rc:
        if st.session_state.revision_plan and st.button("Clear Revision Plan", key="btn_clear_rev"):
            st.session_state.revision_plan = None
            st.session_state.revision_completed = {}
            st.rerun()
            
    if st.session_state.revision_plan:
        st.markdown(f"### 📅 Revision Schedule: **{rev_topic}**")
        
        total = len(st.session_state.revision_plan)
        done = sum(1 for val in st.session_state.revision_completed.values() if val)
        pct = done / total if total > 0 else 0.0
        
        st.progress(pct)
        st.write(f"Completed **{done}** out of **{total}** study days ({pct*100:.1f}%)")
        
        for idx, day in enumerate(st.session_state.revision_plan):
            d_num = day.get("day", idx + 1)
            task = day.get("task", "")
            
            completed = st.checkbox(
                f"**Day {d_num}**: {task}",
                value=st.session_state.revision_completed.get(idx, False),
                key=f"rev_task_check_{idx}"
            )
            st.session_state.revision_completed[idx] = completed