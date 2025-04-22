import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Database Operations ---
def init_db():
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        manager_id INTEGER
    )''')
    # Evaluations table
    c.execute('''CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        manager_id INTEGER,
        quality REAL,
        punctuality REAL,
        teamwork REAL,
        targets REAL,
        comments TEXT,
        review_date TEXT,
        status TEXT
    )''')
    # Goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        description TEXT,
        set_date TEXT,
        status TEXT
    )''')
    # Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        manager_id INTEGER,
        message TEXT,
        date TEXT
    )''')
    # Self-evaluations table
    c.execute('''CREATE TABLE IF NOT EXISTS self_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        comments TEXT,
        submission_date TEXT,
        status TEXT
    )''')
    # Documents table
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        filename TEXT,
        upload_date TEXT
    )''')
    # Meetings table
    c.execute('''CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        manager_id INTEGER,
        meeting_date TEXT,
        purpose TEXT
    )''')
    # Training recommendations
    c.execute('''CREATE TABLE IF NOT EXISTS training (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        manager_id INTEGER,
        program TEXT,
        date TEXT
    )''')
    # Sample data (optional, can be removed after initial testing)
    c.execute("INSERT OR IGNORE INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
              ('emp1', 'pass123', 'employee', 2))
    c.execute("INSERT OR IGNORE INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
              ('mgr1', 'pass123', 'manager', None))
    conn.commit()
    conn.close()

def register_user(username, password, role, manager_id=None):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
                  (username, password, role, manager_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def authenticate_user(username, password):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute("SELECT id, role, manager_id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def save_evaluation(employee_id, manager_id, quality, punctuality, teamwork, targets, comments):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO evaluations (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, review_date, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, datetime.now().strftime('%Y-%m-%d'), 'Draft'))
    conn.commit()
    conn.close()

def get_evaluations(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM evaluations WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM evaluations WHERE manager_id = ?"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def save_goal(employee_id, description):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO goals (employee_id, description, set_date, status)
                 VALUES (?, ?, ?, ?)''',
              (employee_id, description, datetime.now().strftime('%Y-%m-%d'), 'Active'))
    conn.commit()
    conn.close()

def get_goals(employee_id):
    conn = sqlite3.connect('performance.db')
    df = pd.read_sql_query("SELECT * FROM goals WHERE employee_id = ?", conn, params=(employee_id,))
    conn.close()
    return df

def save_feedback(employee_id, manager_id, message):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO feedback (employee_id, manager_id, message, date)
                 VALUES (?, ?, ?, ?)''',
              (employee_id, manager_id, message, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_feedback(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM feedback WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM feedback WHERE manager_id = ?"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def save_self_evaluation(employee_id, comments):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO self_evaluations (employee_id, comments, submission_date, status)
                 VALUES (?, ?, ?, ?)''',
              (employee_id, comments, datetime.now().strftime('%Y-%m-%d'), 'Pending'))
    conn.commit()
    conn.close()

def get_self_evaluations(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM self_evaluations WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM self_evaluations WHERE employee_id IN (SELECT id FROM users WHERE manager_id = ?)"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def save_document(employee_id, filename):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO documents (employee_id, filename, upload_date)
                 VALUES (?, ?, ?)''',
              (employee_id, filename, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_documents(employee_id):
    conn = sqlite3.connect('performance.db')
    df = pd.read_sql_query("SELECT * FROM documents WHERE employee_id = ?", conn, params=(employee_id,))
    conn.close()
    return df

def schedule_meeting(employee_id, manager_id, meeting_date, purpose):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO meetings (employee_id, manager_id, meeting_date, purpose)
                 VALUES (?, ?, ?, ?)''',
              (employee_id, manager_id, meeting_date, purpose))
    conn.commit()
    conn.close()

def get_meetings(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM meetings WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM meetings WHERE manager_id = ?"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def save_training(employee_id, manager_id, program):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO training (employee_id, manager_id, program, date)
                 VALUES (?, ?, ?, ?)''',
              (employee_id, manager_id, program, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_training(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM training WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM training WHERE manager_id = ?"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def get_team_employees(manager_id):
    conn = sqlite3.connect('performance.db')
    df = pd.read_sql_query("SELECT id, username FROM users WHERE manager_id = ?", conn, params=(manager_id,))
    conn.close()
    return df

def get_managers():
    conn = sqlite3.connect('performance.db')
    df = pd.read_sql_query("SELECT id, username FROM users WHERE role = 'manager'", conn)
    conn.close()
    return df

def update_evaluation_status(evaluation_id, status):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute("UPDATE evaluations SET status = ? WHERE id = ?", (status, evaluation_id))
    conn.commit()
    conn.close()

def update_self_evaluation_status(evaluation_id, status):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute("UPDATE self_evaluations SET status = ? WHERE id = ?", (status, evaluation_id))
    conn.commit()
    conn.close()

# --- Custom CSS ---
css = """
body {
    background-color: #f0f2f6;
    font-family: 'Arial', sans-serif;
}
h1, h2, h3 {
    color: #1f2a44;
}
.stButton>button {
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #0056b3;
}
.stTextInput>input, .stTextArea>textarea {
    border: 1px solid #ced4da;
    border-radius: 5px;
    padding: 10px;
}
.stTabs [role="tab"] {
    background-color: #ffffff;
    border-radius: 5px 5px 0 0;
    padding: 10px 20px;
    margin-right: 5px;
    color: #1f2a44;
}
.stTabs [role="tab"][aria-selected="true"] {
    background-color: #007bff;
    color: white;
}
.stDataFrame {
    border: 1px solid #ced4da;
    border-radius: 5px;
    padding: 10px;
}
.stFileUploader {
    border: 1px dashed #ced4da;
    border-radius: 5px;
    padding: 10px;
}
"""

# --- Streamlit Application ---
# Initialize database
init_db()

# Set page configuration
st.set_page_config(page_title="Employee Performance Evaluation System", layout="wide")

# Apply custom CSS
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Session state for user
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.manager_id = None

# Login and Registration page
def auth_page():
    st.title("🔐 Performance Insight Solutions")
    st.markdown("### Login or Register to Access the Employee Performance System")

    # Tabs for Login and Register
    login_tab, register_tab = st.tabs(["Login", "Register"])

    # Login Tab
    with login_tab:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            if submitted:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user_id, st.session_state.role, st.session_state.manager_id = user
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    # Register Tab
    with register_tab:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            role = st.selectbox("Role", ["employee", "manager"], key="register_role")
            manager_id = None
            if role == "employee":
                managers = get_managers()
                if not managers.empty:
                    manager_username = st.selectbox("Select Manager", managers['username'], key="register_manager")
                    manager_id = managers[managers['username'] == manager_username]['id'].iloc[0]
                else:
                    st.warning("No managers available. Please register a manager first.")
            submitted = st.form_submit_button("Register")
            if submitted:
                if role == "employee" and manager_id is None:
                    st.error("Please select a manager or ensure a manager is registered.")
                elif register_user(new_username, new_password, role, manager_id):
                    st.success(f"Registered successfully! Please login with {new_username}.")
                else:
                    st.error("Username already exists. Choose a different username.")

# Employee Dashboard
def employee_dashboard():
    st.title("👤 Employee Dashboard")
    tabs = st.tabs(["Evaluations", "Feedback", "Goals", "Self-Evaluation", "Documents", "Meetings", "Training"])

    # Tab 1: View Evaluations
    with tabs[0]:
        st.subheader("📊 My Performance Evaluations")
        evaluations = get_evaluations(st.session_state.user_id, st.session_state.role, st.session_state.user_id)
        if not evaluations.empty:
            st.dataframe(evaluations[['review_date', 'quality', 'punctuality', 'teamwork', 'targets', 'comments', 'status']])
            # Graphical report
            df_melt = evaluations.melt(id_vars=['review_date'], value_vars=['quality', 'punctuality', 'teamwork', 'targets'],
                                       var_name='Metric', value_name='Score')
            fig = px.line(df_melt, x='review_date', y='Score', color='Metric', title="Performance Trends")
            st.plotly_chart(fig)
        else:
            st.info("No evaluations available.")

    # Tab 2: View Feedback
    with tabs[1]:
        st.subheader("💬 Feedback from Manager")
        feedback = get_feedback(st.session_state.user_id, st.session_state.role, st.session_state.user_id)
        if not feedback.empty:
            for _, row in feedback.iterrows():
                st.write(f"**{row['date']}**: {row['message']}")
        else:
            st.info("No feedback available.")

    # Tab 3: Set and View Goals
    with tabs[2]:
        st.subheader("🎯 My Goals")
        with st.form("goal_form"):
            goal_description = st.text_area("Set a New Goal")
            if st.form_submit_button("Submit Goal"):
                save_goal(st.session_state.user_id, goal_description)
                st.success("Goal saved!")
        goals = get_goals(st.session_state.user_id)
        if not goals.empty:
            st.dataframe(goals[['description', 'set_date', 'status']])
        else:
            st.info("No goals set.")

    # Tab 4: Self-Evaluation
    with tabs[3]:
        st.subheader("✍️ Self-Evaluation")
        with st.form("self_evaluation_form"):
            comments = st.text_area("Your Self-Evaluation Comments")
            if st.form_submit_button("Submit Self-Evaluation"):
                save_self_evaluation(st.session_state.user_id, comments)
                st.success("Self-evaluation submitted!")
        self_evals = get_self_evaluations(st.session_state.user_id, st.session_state.role, st.session_state.user_id)
        if not self_evals.empty:
            st.dataframe(self_evals[['submission_date', 'comments', 'status']])
        else:
            st.info("No self-evaluations submitted.")

    # Tab 5: Upload Documents
    with tabs[4]:
        st.subheader("📂 Upload Achievements")
        uploaded_file = st.file_uploader("Upload a document", type=['pdf', 'docx', 'txt'])
        if uploaded_file:
            filename = uploaded_file.name
            save_document(st.session_state.user_id, filename)
            st.success(f"Uploaded {filename}")
        documents = get_documents(st.session_state.user_id)
        if not documents.empty:
            st.dataframe(documents[['filename', 'upload_date']])
        else:
            st.info("No documents uploaded.")

    # Tab 6: Request Meetings
    with tabs[5]:
        st.subheader("📅 Request a Meeting")
        with st.form("meeting_form"):
            meeting_date = st.date_input("Meeting Date")
            purpose = st.text_input("Purpose of Meeting")
            if st.form_submit_button("Request Meeting"):
                schedule_meeting(st.session_state.user_id, st.session_state.manager_id, str(meeting_date), purpose)
                st.success("Meeting requested!")
        meetings = get_meetings(st.session_state.user_id, st.session_state.role, st.session_state.user_id)
        if not meetings.empty:
            st.dataframe(meetings[['meeting_date', 'purpose']])
        else:
            st.info("No meetings scheduled.")

    # Tab 7: View Training
    with tabs[6]:
        st.subheader("🎓 Recommended Training")
        training = get_training(st.session_state.user_id, st.session_state.role, st.session_state.user_id)
        if not training.empty:
            st.dataframe(training[['program', 'date']])
        else:
            st.info("No training recommended.")

# Manager Dashboard
def manager_dashboard():
    st.title("🛠️ Manager Dashboard")
    tabs = st.tabs(["Evaluate Employees", "Set Goals", "Provide Feedback", "Review Self-Evaluations", "Schedule Meetings", "Recommend Training", "Analytics"])

    # Tab 1: Evaluate Employees
    with tabs[0]:
        st.subheader("📈 Evaluate Team Members")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee", team['username'])
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            with st.form(f"eval_form_{employee_id}"):
                quality = st.slider("Work Quality", 0.0, 5.0, 2.5)
                punctuality = st.slider("Punctuality", 0.0, 5.0, 2.5)
                teamwork = st.slider("Teamwork", 0.0, 5.0, 2.5)
                targets = st.slider("Meeting Targets", 0.0, 5.0, 2.5)
                comments = st.text_area("Comments")
                if st.form_submit_button("Submit Evaluation"):
                    save_evaluation(employee_id, st.session_state.user_id, quality, punctuality, teamwork, targets, comments)
                    st.success("Evaluation saved as draft!")
            evaluations = get_evaluations(employee_id, st.session_state.role, st.session_state.user_id)
            if not evaluations.empty:
                st.subheader("Past Evaluations")
                for _, row in evaluations.iterrows():
                    st.write(f"**{row['review_date']}** (Status: {row['status']})")
                    st.write(f"Quality: {row['quality']}, Punctuality: {row['punctuality']}, Teamwork: {row['teamwork']}, Targets: {row['targets']}")
                    st.write(f"Comments: {row['comments']}")
                    if row['status'] == 'Draft':
                        if st.button(f"Finalize Evaluation {row['id']}", key=f"finalize_{row['id']}"):
                            update_evaluation_status(row['id'], 'Final')
                            st.success("Evaluation finalized!")
        else:
            st.info("No team members assigned.")

    # Tab 2: Set Goals
    with tabs[1]:
        st.subheader("🎯 Set Goals for Team")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee for Goal", team['username'], key='goal_employee')
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            with st.form(f"goal_form_{employee_id}"):
                goal_description = st.text_area("Goal Description")
                if st.form_submit_button("Set Goal"):
                    save_goal(employee_id, goal_description)
                    st.success("Goal set!")
        else:
            st.info("No team members assigned.")

    # Tab 3: Provide Feedback
    with tabs[2]:
        st.subheader("💬 Provide Feedback")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee for Feedback", team['username'], key='feedback_employee')
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            with st.form(f"feedback_form_{employee_id}"):
                message = st.text_area("Feedback Message")
                if st.form_submit_button("Send Feedback"):
                    save_feedback(employee_id, st.session_state.user_id, message)
                    st.success("Feedback sent!")
        else:
            st.info("No team members assigned.")

    # Tab 4: Review Self-Evaluations
    with tabs[3]:
        st.subheader("✍️ Review Self-Evaluations")
        self_evals = get_self_evaluations(None, st.session_state.role, st.session_state.user_id)
        if not self_evals.empty:
            for _, row in self_evals.iterrows():
                st.write(f"**Employee ID: {row['employee_id']}, Date: {row['submission_date']}** (Status: {row['status']})")
                st.write(f"Comments: {row['comments']}")
                if row['status'] == 'Pending':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Approve {row['id']}", key=f"approve_{row['id']}"):
                            update_self_evaluation_status(row['id'], 'Approved')
                            st.success("Self-evaluation approved!")
                    with col2:
                        if st.button(f"Reject {row['id']}", key=f"reject_{row['id']}"):
                            update_self_evaluation_status(row['id'], 'Rejected')
                            st.success("Self-evaluation rejected!")
        else:
            st.info("No self-evaluations to review.")

    # Tab 5: Schedule Meetings
    with tabs[4]:
        st.subheader("📅 Schedule Meetings")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee for Meeting", team['username'], key='meeting_employee')
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            with st.form(f"meeting_form_{employee_id}"):
                meeting_date = st.date_input("Meeting Date")
                purpose = st.text_input("Purpose of Meeting")
                if st.form_submit_button("Schedule Meeting"):
                    schedule_meeting(employee_id, st.session_state.user_id, str(meeting_date), purpose)
                    st.success("Meeting scheduled!")
        meetings = get_meetings(None, st.session_state.role, st.session_state.user_id)
        if not meetings.empty:
            st.dataframe(meetings[['employee_id', 'meeting_date', 'purpose']])
        else:
            st.info("No meetings scheduled.")

    # Tab 6: Recommend Training
    with tabs[5]:
        st.subheader("🎓 Recommend Training")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee for Training", team['username'], key='training_employee')
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            with st.form(f"training_form_{employee_id}"):
                program = st.text_input("Training Program")
                if st.form_submit_button("Recommend Training"):
                    save_training(employee_id, st.session_state.user_id, program)
                    st.success("Training recommended!")
        training = get_training(None, st.session_state.role, st.session_state.user_id)
        if not training.empty:
            st.dataframe(training[['employee_id', 'program', 'date']])
        else:
            st.info("No training recommended.")

    # Tab 7: Analytics
    with tabs[6]:
        st.subheader("📊 Team Performance Analytics")
        evaluations = get_evaluations(None, st.session_state.role, st.session_state.user_id)
        if not evaluations.empty:
            # Average scores per employee
            avg_scores = evaluations.groupby('employee_id')[['quality', 'punctuality', 'teamwork', 'targets']].mean().reset_index()
            fig = px.bar(avg_scores, x='employee_id', y=['quality', 'punctuality', 'teamwork', 'targets'],
                         barmode='group', title="Average Performance Scores by Employee")
            st.plotly_chart(fig)
            # Trend over time
            fig_trend = px.line(evaluations, x='review_date', y=['quality', 'punctuality', 'teamwork', 'targets'],
                                color='employee_id', title="Performance Trends Over Time")
            st.plotly_chart(fig_trend)
        else:
            st.info("No evaluations available for analytics.")

# Main app logic
if st.session_state.user_id is None:
    auth_page()
else:
    if st.session_state.role == 'employee':
        employee_dashboard()
    else:
        manager_dashboard()
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.role = None
        st.session_state.manager_id = None
        st.rerun()
