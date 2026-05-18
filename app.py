# =========================================================
# AI CHATBOT WITH DATA INTEGRATION
# CHATBOT FIRST DESIGN
# =========================================================
# 
import streamlit as st
from backend import ask_llm, load_csv, get_sqlite_tables, load_sqlite_table, load_sql, load_xls, get_sql_tables, load_sql_table
from utilities import build_prompt_with_context

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Chatbot Assistant",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

if "df" not in st.session_state:
    st.session_state.df = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_load" not in st.session_state:
    st.session_state.first_load = True

# =========================================================
# SIDEBAR - DATA INPUT
# =========================================================

st.sidebar.title("📥 Data Management")
st.sidebar.markdown("---")

# Menu untuk pilih sumber data
data_source = st.sidebar.selectbox(
    "Pilih Sumber Data",
    [
        "-- Tidak Ada --",
        "📂 Upload CSV",
        "📋 Upload Excel (.xls/.xlsx)",
        "🗄️ SQLite",
        "📄 SQL File (.sql)"
    ],
    key="data_source"
)

# =========================================================
# CSV UPLOAD
# =========================================================

if data_source == "📂 Upload CSV":

    st.sidebar.subheader("📂 Upload CSV")

    uploaded_file = st.sidebar.file_uploader(
        "Pilih file CSV",
        type=["csv"]
    )

    if uploaded_file:

        df, success, message = load_csv(uploaded_file)
        
        if success:
            st.session_state.df = df
            st.sidebar.success(message)
            st.sidebar.info(f"📊 Data: {df.shape[0]} baris, {df.shape[1]} kolom")
        else:
            st.sidebar.error(message)

# =========================================================
# EXCEL UPLOAD
# =========================================================

elif data_source == "📋 Upload Excel (.xls/.xlsx)":

    st.sidebar.subheader("📋 Upload Excel")

    uploaded_file = st.sidebar.file_uploader(
        "Pilih file Excel",
        type=["xls", "xlsx"]
    )

    if uploaded_file:

        df, success, message = load_xls(uploaded_file)
        
        if success:
            st.session_state.df = df
            st.sidebar.success(message)
            st.sidebar.info(f"📊 Data: {df.shape[0]} baris, {df.shape[1]} kolom")
        else:
            st.sidebar.error(message)

# =========================================================
# SQLITE UPLOAD
# =========================================================

elif data_source == "🗄️ SQLite":

    st.sidebar.subheader("🗄️ SQLite Database")

    sqlite_file = st.sidebar.file_uploader(
        "Pilih file SQLite",
        type=["db", "sqlite", "sqlite3"]
    )

    if sqlite_file:

        table_list, success, message = get_sqlite_tables(sqlite_file)
        
        if success:
            st.sidebar.success("✅ File SQLite berhasil dibaca!")
            
            selected_table = st.sidebar.selectbox(
                "Pilih Tabel",
                table_list
            )

            if selected_table:

                df, success, message = load_sqlite_table(selected_table)
                
                if success:
                    st.session_state.df = df
                    st.sidebar.success(message)
                    st.sidebar.info(f"📊 Data: {df.shape[0]} baris, {df.shape[1]} kolom")
                else:
                    st.sidebar.error(message)
        else:
            st.sidebar.error(message)

# =========================================================
# SQL FILE UPLOAD
# =========================================================

elif data_source == "📄 SQL File (.sql)":

    st.sidebar.subheader("📄 SQL File")

    sql_file = st.sidebar.file_uploader(
        "Pilih file SQL",
        type=["sql"]
    )

    if sql_file:

        table_list, success, message = get_sql_tables(sql_file)
        
        if success:
            st.sidebar.success("✅ File SQL berhasil dibaca!")
            
            selected_table = st.sidebar.selectbox(
                "Pilih Tabel",
                table_list,
                key="sql_table_select"
            )

            if selected_table:

                df, success, message = load_sql_table(selected_table)
                
                if success:
                    st.session_state.df = df
                    st.sidebar.success(message)
                    st.sidebar.info(f"📊 Data: {df.shape[0]} baris, {df.shape[1]} kolom")
                else:
                    st.sidebar.error(message)
        else:
            st.sidebar.error(message)

# =========================================================
# DATA STATUS
# =========================================================

st.sidebar.markdown("---")

if st.session_state.df is not None:
    st.sidebar.success("✅ Data Aktif")
    with st.sidebar.expander("👀 Preview Data"):
        st.dataframe(st.session_state.df.head(), use_container_width=True)
else:
    st.sidebar.warning("⚠️ Belum Ada Data")

# =========================================================
# MAIN PAGE - CHATBOT
# =========================================================

st.title("🤖 AI Chatbot Assistant")

# =========================================================
# GREETING MESSAGE (First Load)
# =========================================================

if st.session_state.first_load:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """👋 **Halo! Saya adalah AI Chatbot Assistant Anda.**

Saya siap membantu Anda dengan:
- 📊 Membaca dan menganalisis data
- 🔍 Mencari informasi spesifik dalam dataset
- 📈 Memberikan insight dari data Anda
- ❓ Menjawab pertanyaan tentang data

**Cara Menggunakan:**
1. Upload atau koneksikan data Anda dari sidebar
2. Tanyakan apa pun tentang data Anda di chat ini
3. Saya akan membantu Anda mendapatkan jawaban yang tepat

Mulai percakapan sekarang! 😊"""
        }
    ]
    st.session_state.first_load = False

# =========================================================
# DISPLAY CHAT MESSAGES
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================================================
# CHAT INPUT
# =========================================================

user_input = st.chat_input("Tanyakan sesuatu tentang data Anda...")

if user_input:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        full_prompt = build_prompt_with_context(user_input, st.session_state.df)

        with st.spinner("🤔 Berpikir..."):
            response = ask_llm(full_prompt)

        message_placeholder.markdown(response)

    # Add assistant message to history
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.caption("🤖 AI Chatbot Assistant")

with col2:
    if st.session_state.df is not None:
        st.caption(f"📊 Data: {st.session_state.df.shape[0]} baris")
    else:
        st.caption("⚠️ Belum ada data")

with col3:
    st.caption("© 2026 AI Chatbot Team")
