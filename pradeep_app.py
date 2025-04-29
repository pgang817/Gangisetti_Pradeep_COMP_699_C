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
        manager_id INTEGER,
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
        # For employees, manager_id is required
        if role == 'employee' and manager_id is None:
            print("Manager ID is required for employee registration")
            return False

        c.execute('INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)',
                  (username, password, role, manager_id))
        conn.commit()
        print(f"User registered: {username}, role: {role}, manager_id: {manager_id}")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Registration failed: {str(e)}")
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute("SELECT id, role, manager_id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def evaluate_employee(employee_id, manager_id, quality, punctuality, teamwork, targets, comments):
    try:
        print(f"Saving evaluation - Employee ID: {employee_id}, Manager ID: {manager_id}")
        conn = sqlite3.connect('performance.db')
        c = conn.cursor()
        review_date = datetime.now().strftime('%Y-%m-%d')
        
        # Convert IDs to integers
        employee_id = int(employee_id)
        manager_id = int(manager_id)
        
        # Convert scores to floats
        quality = float(quality)
        punctuality = float(punctuality)
        teamwork = float(teamwork)
        targets = float(targets)
        
        c.execute('''
            INSERT INTO evaluations 
            (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, review_date, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, review_date, 'Draft'))
        
        conn.commit()
        print(f"Evaluation saved successfully for employee {employee_id}")
        
        # Verify the saved evaluation
        c.execute('SELECT * FROM evaluations WHERE employee_id = ? ORDER BY review_date DESC LIMIT 1', (employee_id,))
        saved = c.fetchone()
        print(f"Latest evaluation for employee {employee_id}: {saved}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error in evaluate_employee: {e}")
        return False

def save_evaluation(employee_id, manager_id, quality, punctuality, teamwork, targets, comments):
    try:
        print(f"Saving evaluation - Employee ID: {employee_id}, Manager ID: {manager_id}")
        conn = sqlite3.connect('performance.db')
        c = conn.cursor()
        
        # Convert IDs to integers
        employee_id = int(employee_id)
        manager_id = int(manager_id)
        
        # Convert scores to floats
        quality = float(quality)
        punctuality = float(punctuality)
        teamwork = float(teamwork)
        targets = float(targets)
        
        review_date = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('''
            INSERT INTO evaluations 
            (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, review_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_id, manager_id, quality, punctuality, teamwork, targets, comments, review_date, 'Draft'))
        
        conn.commit()
        print(f"Evaluation saved successfully for employee {employee_id}")
        
        # Verify the saved evaluation
        c.execute('SELECT * FROM evaluations WHERE employee_id = ? ORDER BY review_date DESC LIMIT 1', (employee_id,))
        saved = c.fetchone()
        print(f"Latest evaluation for employee {employee_id}: {saved}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error in save_evaluation: {e}")
        return False

def get_evaluations(employee_id, role, user_id):
    conn = sqlite3.connect('performance.db')
    query = "SELECT * FROM evaluations WHERE employee_id = ?" if role == 'employee' else "SELECT * FROM evaluations WHERE manager_id = ?"
    df = pd.read_sql_query(query, conn, params=(employee_id if role == 'employee' else user_id,))
    conn.close()
    return df

def save_goal(employee_id, manager_id, description):
    conn = sqlite3.connect('performance.db')
    c = conn.cursor()
    c.execute('''INSERT INTO goals (employee_id, manager_id, description, set_date, status)
                 VALUES (?, ?, ?, ?, ?)''',
              (employee_id, manager_id, description, datetime.now().strftime('%Y-%m-%d'), 'Active'))
    conn.commit()
    conn.close()

def get_goals(employee_id, role, manager_id):
    conn = sqlite3.connect('performance.db')
    # For employees, show goals assigned by their manager
    # For managers, show goals they've assigned
    query = "SELECT * FROM goals WHERE employee_id = ? AND manager_id = ?" if role == 'employee' else "SELECT * FROM goals WHERE manager_id = ?"
    params = (employee_id, manager_id) if role == 'employee' else (manager_id,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def save_feedback(employee_id, manager_id, message):
    try:
        print(f"Saving feedback - employee_id: {employee_id}, manager_id: {manager_id}, message: {message}")
        conn = sqlite3.connect('performance.db')
        c = conn.cursor()
        c.execute('''INSERT INTO feedback (employee_id, manager_id, message, date)
                     VALUES (?, ?, ?, ?)''',
                  (employee_id, manager_id, message, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        print("Feedback committed to database")
        # Verify the save
        c.execute('SELECT * FROM feedback WHERE employee_id=? AND manager_id=? ORDER BY id DESC LIMIT 1', 
                  (employee_id, manager_id))
        result = c.fetchone()
        print(f"Verification - Last feedback entry: {result}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving feedback: {str(e)}")
        return False

def get_feedback(employee_id, role, manager_id):
    conn = sqlite3.connect('performance.db')
    # For employees, show feedback given by their manager
    # For managers, show feedback they've given to selected employee
    if role == 'employee':
        query = "SELECT * FROM feedback WHERE employee_id = ? AND manager_id = ?"
        params = (employee_id, manager_id)
    else:
        # If employee_id is provided, show feedback for that employee
        if employee_id:
            query = "SELECT * FROM feedback WHERE employee_id = ? AND manager_id = ?"
            params = (employee_id, manager_id)
        else:
            # Show all feedback given by the manager
            query = "SELECT * FROM feedback WHERE manager_id = ?"
            params = (manager_id,)
    df = pd.read_sql_query(query, conn, params=params)
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

def get_team_employees(manager_id):
    print(f"Getting team employees for manager_id: {manager_id}")
    conn = sqlite3.connect('performance.db')
    try:
        # Get all employees assigned to this manager
        query = '''
        SELECT id, username, role 
        FROM users 
        WHERE manager_id = ? AND role = "employee"
        ORDER BY username
        '''
        df = pd.read_sql_query(query, conn, params=(manager_id,))
        print(f"Found {len(df)} team members: {df['username'].tolist() if not df.empty else []}")
        return df
    finally:
        conn.close()

def schedule_meeting(employee_id, manager_id, meeting_date, purpose):
    try:
        print(f"Scheduling meeting - employee_id: {employee_id}, manager_id: {manager_id}, date: {meeting_date}, purpose: {purpose}")
        conn = sqlite3.connect('performance.db')
        c = conn.cursor()
        c.execute('''INSERT INTO meetings (employee_id, manager_id, meeting_date, purpose)
                     VALUES (?, ?, ?, ?)''',
                  (employee_id, manager_id, meeting_date, purpose))
        conn.commit()
        print("Meeting committed to database")
        # Verify the save
        c.execute('SELECT * FROM meetings WHERE employee_id=? AND manager_id=? ORDER BY id DESC LIMIT 1', 
                  (employee_id, manager_id))
        result = c.fetchone()
        print(f"Verification - Last meeting entry: {result}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error scheduling meeting: {str(e)}")
        return False

def get_meetings(employee_id, role, manager_id):
    conn = sqlite3.connect('performance.db')
    # For employees, show meetings where they are the employee
    # For managers, show meetings they've scheduled with selected employee
    if role == 'employee':
        query = "SELECT * FROM meetings WHERE employee_id = ? AND manager_id = ?"
        params = (employee_id, manager_id)
    else:
        # If employee_id is provided, show meetings for that employee
        if employee_id:
            query = "SELECT * FROM meetings WHERE employee_id = ? AND manager_id = ?"
            params = (employee_id, manager_id)
        else:
            # Show all meetings scheduled by the manager
            query = "SELECT * FROM meetings WHERE manager_id = ?"
            params = (manager_id,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def save_training(employee_id, manager_id, program):
    try:
        print(f"Saving training - employee_id: {employee_id}, manager_id: {manager_id}, program: {program}")
        conn = sqlite3.connect('performance.db')
        c = conn.cursor()
        c.execute('''INSERT INTO training (employee_id, manager_id, program, date)
                     VALUES (?, ?, ?, ?)''',
                  (employee_id, manager_id, program, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        print("Training committed to database")
        # Verify the save
        c.execute('SELECT * FROM training WHERE employee_id=? AND manager_id=? ORDER BY id DESC LIMIT 1', 
                  (employee_id, manager_id))
        result = c.fetchone()
        print(f"Verification - Last training entry: {result}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving training: {str(e)}")
        return False

def get_training(employee_id, role, manager_id):
    conn = sqlite3.connect('performance.db')
    # For employees, show training assigned to them by their manager
    # For managers, show training they've assigned to selected employee
    if role == 'employee':
        query = "SELECT * FROM training WHERE employee_id = ? AND manager_id = ?"
        params = (employee_id, manager_id)
    else:
        # If employee_id is provided, show training for that employee
        if employee_id:
            query = "SELECT * FROM training WHERE employee_id = ? AND manager_id = ?"
            params = (employee_id, manager_id)
        else:
            # Show all training assigned by the manager
            query = "SELECT * FROM training WHERE manager_id = ?"
            params = (manager_id,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_team_employees(manager_id):
    conn = sqlite3.connect('performance.db')
    # manager_id here is the actual ID of the manager, not their username
    df = pd.read_sql_query("SELECT id, username FROM users WHERE manager_id = ? AND role = 'employee'", conn, params=(manager_id,))
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
                    st.write(f"Debug - Login successful: user_id={st.session_state.user_id}, role={st.session_state.role}, manager_id={st.session_state.manager_id}")
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
            
            # Show manager selection for employees
            manager_id = None
            manager_username = None
            if role == "employee":
                # Get list of managers
                conn = sqlite3.connect('performance.db')
                managers = pd.read_sql_query('SELECT id, username FROM users WHERE role = "manager"', conn)
                conn.close()
                
                if not managers.empty:
                    st.write("Available Managers:")
                    manager_username = st.selectbox(
                        "Select Manager",
                        managers['username'],
                        key="register_manager"
                    )
                    manager_id = int(managers[managers['username'] == manager_username]['id'].iloc[0])
                    st.write(f"Debug - Selected manager: {manager_username} (ID: {manager_id})")
                else:
                    st.warning("No managers available. Please register a manager first.")
            
            submitted = st.form_submit_button("Register")
            if submitted:
                if new_username and new_password:
                    if role == "employee" and manager_id is None:
                        st.error("Please select a manager for the employee.")
                    else:
                        st.write(f"Debug - Registering {role} with manager_id: {manager_id}")
                        if register_user(new_username, new_password, role, manager_id):
                            if role == "employee":
                                st.success(f"Registration successful! {new_username} has been registered as {role} and assigned to {manager_username}")
                            else:
                                st.success(f"Registration successful! {new_username} has been registered as {role}")
                        else:
                            st.error("Registration failed. Username may already exist.")
                else:
                    st.error("Username already exists. Please choose a different username.")

# Employee Dashboard
def employee_dashboard():
    st.title("👤 Employee Dashboard")
    st.write(f"Debug - Employee ID: {st.session_state.user_id}, Manager ID: {st.session_state.manager_id}")
    tabs = st.tabs(["Evaluations", "Goals", "Feedback", "Self Evaluations", "Documents", "Meetings", "Training"])

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

    # Tab 2: View Goals
    with tabs[1]:
        st.subheader("🎯 My Goals")
        with st.form("goal_form"):
            goal_description = st.text_area("Set a New Goal")
            if st.form_submit_button("Submit Goal"):
                save_goal(st.session_state.user_id, goal_description)
                st.success("Goal saved!")
        goals = get_goals(st.session_state.user_id, st.session_state.role, st.session_state.manager_id)
        if not goals.empty:
            st.dataframe(goals[['description', 'set_date', 'status']])
        else:
            st.info("No goals set.")

    # Tab 3: View Feedback
    with tabs[2]:
        st.subheader("💬 Feedback")
        st.write(f"Debug - Getting feedback for employee {st.session_state.user_id} from manager {st.session_state.manager_id}")
        feedback = get_feedback(st.session_state.user_id, st.session_state.role, st.session_state.manager_id)
        st.write(f"Debug - Found {len(feedback)} feedback entries")
        if not feedback.empty:
            st.dataframe(feedback[['date', 'message']])
        else:
            st.info("No feedback received yet.")

    # Tab 4: Self Evaluations
    with tabs[3]:
        st.subheader("✍️ Self Evaluations")
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

    # Tab 6: Meetings
    with tabs[5]:
        st.subheader("📅 Meetings")
        st.write(f"Debug - Getting meetings for employee {st.session_state.user_id} from manager {st.session_state.manager_id}")
        meetings = get_meetings(st.session_state.user_id, st.session_state.role, st.session_state.manager_id)
        st.write(f"Debug - Found {len(meetings)} meeting entries")
        if not meetings.empty:
            st.dataframe(meetings[['meeting_date', 'purpose']])
        else:
            st.info("No meetings scheduled yet.")

    # Tab 7: View Training
    with tabs[6]:
        st.subheader("🎓 Recommended Training")
        training = get_training(st.session_state.user_id, st.session_state.role, st.session_state.manager_id)
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
            st.write(f"Debug: Selected employee ID: {employee_id}, Manager ID: {st.session_state.user_id}")
            with st.form(f"goal_form_{employee_id}"):
                goal_description = st.text_area("Goal Description")
                if st.form_submit_button("Set Goal"):
                    st.write(f"Debug: Saving goal for employee {employee_id} from manager {st.session_state.user_id}")
                    save_goal(int(employee_id), int(st.session_state.user_id), goal_description)
                    st.success("Goal set!")
        else:
            st.info("No team members assigned.")

    # Tab 3: Provide Feedback
    with tabs[2]:
        st.subheader("💬 Provide Feedback")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            st.write(f"Debug - Team members: {team.to_dict('records')}")
            employee = st.selectbox("Select Employee for Feedback", team['username'], key='feedback_employee')
            employee_id = int(team[team['username'] == employee]['id'].iloc[0])
            st.write(f"Debug - Selected employee: {employee} (ID: {employee_id}), Manager ID: {st.session_state.user_id}")
            with st.form(f"feedback_form_{employee_id}"):
                message = st.text_area("Feedback Message")
                if st.form_submit_button("Send Feedback"):
                    st.write(f"Debug - Saving feedback for employee {employee_id} from manager {st.session_state.user_id}")
                    if save_feedback(employee_id, int(st.session_state.user_id), message):
                        st.success(f"Feedback sent to {employee}!")
                        # Show the saved feedback
                        feedback = get_feedback(employee_id, 'manager', st.session_state.user_id)
                        if not feedback.empty:
                            st.write("Latest feedback:")
                            st.dataframe(feedback[['date', 'message']])
                    else:
                        st.error("Failed to save feedback!")
            # Show existing feedback for this employee
            feedback = get_feedback(employee_id, 'manager', st.session_state.user_id)
            st.write(f"Debug: Found {len(feedback)} feedback entries")
            if not feedback.empty:
                st.write("Existing feedback:")
                st.dataframe(feedback[['date', 'message']])
            else:
                st.info("No feedback given yet.")
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
            st.write(f"Debug - Team members: {team.to_dict('records')}")
            employee = st.selectbox("Select Employee for Meeting", team['username'], key='meeting_employee')
            employee_id = int(team[team['username'] == employee]['id'].iloc[0])
            st.write(f"Debug - Selected employee: {employee} (ID: {employee_id}), Manager ID: {st.session_state.user_id}")
            with st.form(f"meeting_form_{employee_id}"):
                meeting_date = st.date_input("Meeting Date")
                purpose = st.text_input("Purpose of Meeting")
                if st.form_submit_button("Schedule Meeting"):
                    st.write(f"Debug - Scheduling meeting for employee {employee_id} with manager {st.session_state.user_id}")
                    if schedule_meeting(employee_id, int(st.session_state.user_id), str(meeting_date), purpose):
                        st.success(f"Meeting scheduled with {employee}!")
                        # Show the saved meeting
                        meetings = get_meetings(employee_id, 'manager', st.session_state.user_id)
                        if not meetings.empty:
                            st.write("Latest meetings:")
                            st.dataframe(meetings[['meeting_date', 'purpose']])
                    else:
                        st.error("Failed to schedule meeting!")
            # Show existing meetings for this employee
            meetings = get_meetings(employee_id, 'manager', st.session_state.user_id)
            st.write(f"Debug: Found {len(meetings)} meeting entries")
            if not meetings.empty:
                st.write("Existing meetings:")
                st.dataframe(meetings[['meeting_date', 'purpose']])
            else:
                st.info("No meetings scheduled yet.")


    # Tab 6: Recommend Training
    with tabs[5]:
        st.subheader("🎓 Recommend Training")
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            employee = st.selectbox("Select Employee for Training", team['username'], key='training_employee')
            employee_id = team[team['username'] == employee]['id'].iloc[0]
            st.write(f"Debug: Selected employee ID: {employee_id}, Manager ID: {st.session_state.user_id}")
            with st.form(f"training_form_{employee_id}"):
                program = st.text_input("Training Program")
                if st.form_submit_button("Recommend Training"):
                    st.write(f"Debug: Saving training for employee {employee_id} from manager {st.session_state.user_id}")
                    save_training(int(employee_id), int(st.session_state.user_id), program)
                    st.success("Training recommended!")
            # Show existing training for this employee
            training = get_training(employee_id, 'manager', st.session_state.user_id)
            st.write(f"Debug: Found {len(training)} training entries")
            if not training.empty:
                st.write("Existing training:")
                st.dataframe(training[['date', 'program']])
            else:
                st.info("No training recommended yet.")


    # Tab 7: Analytics
    with tabs[6]:
        st.subheader("📈 Team Performance Analytics")
        
        # Get team members
        team = get_team_employees(st.session_state.user_id)
        if not team.empty:
            # Add 'All Employees' option
            all_option = pd.DataFrame({'id': [-1], 'username': ['All Employees']})
            team_with_all = pd.concat([all_option, team])
            
            # Employee selection
            selected_employee = st.selectbox(
                "Select Employee",
                team_with_all['username'],
                key='analytics_employee'
            )
            
            # Get selected employee ID
            if selected_employee != 'All Employees':
                selected_id = str(team[team['username'] == selected_employee]['id'].iloc[0])
            else:
                selected_id = None
            
            # Get evaluations
            evaluations = get_evaluations(selected_id, st.session_state.role, st.session_state.user_id)
            
            if not evaluations.empty:
                # Clean and convert data types
                evaluations['quality'] = pd.to_numeric(evaluations['quality'], errors='coerce')
                evaluations['punctuality'] = pd.to_numeric(evaluations['punctuality'], errors='coerce')
                evaluations['teamwork'] = pd.to_numeric(evaluations['teamwork'], errors='coerce')
                evaluations['targets'] = pd.to_numeric(evaluations['targets'], errors='coerce')
                evaluations['employee_id'] = evaluations['employee_id'].fillna('24')  # Default to nagendra's ID
                
                # Create ID to name mapping
                id_to_name = dict(zip(team['id'].astype(str), team['username']))
                
                # Map employee IDs to names
                evaluations['employee_name'] = evaluations['employee_id'].map(id_to_name).fillna('Nagendra')
                
                # Drop any rows with missing values in scores
                evaluations = evaluations.dropna(subset=['quality', 'punctuality', 'teamwork', 'targets'])
                
                if not evaluations.empty:
                    # Show evaluation details
                    st.write(f"Showing data for: {selected_employee}")
                    st.write(f"Number of evaluations: {len(evaluations)}")
                    
                    # Calculate average scores
                    if selected_employee != 'All Employees':
                        # For single employee, show scores over time
                        evaluations['review_date'] = pd.to_datetime(evaluations['review_date'])
                        
                        # Line chart showing progress
                        fig = px.line(evaluations, 
                                     x='review_date', 
                                     y=['quality', 'punctuality', 'teamwork', 'targets'],
                                     title=f"Performance Trends for {selected_employee}")
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Score",
                            legend_title="Metrics"
                        )
                        st.plotly_chart(fig)
                        
                        # Show individual scores
                        st.write("Individual Evaluation Scores:")
                        display_df = evaluations[['review_date', 'quality', 'punctuality', 'teamwork', 'targets']].copy()
                        display_df['review_date'] = display_df['review_date'].dt.strftime('%Y-%m-%d')
                        st.dataframe(display_df.set_index('review_date').round(2))
                        
                        # Calculate and show averages
                        avg_scores = evaluations[['quality', 'punctuality', 'teamwork', 'targets']].mean().round(2)
                        st.write("Average Scores:")
                        st.write({
                            "Quality": avg_scores['quality'],
                            "Punctuality": avg_scores['punctuality'],
                            "Teamwork": avg_scores['teamwork'],
                            "Targets": avg_scores['targets']
                        })
                    else:
                        # For all employees, show comparison
                        avg_scores = evaluations.groupby('employee_name').agg({
                            'quality': 'mean',
                            'punctuality': 'mean',
                            'teamwork': 'mean',
                            'targets': 'mean'
                        }).reset_index()
                        
                        # Bar chart comparing employees
                        fig = px.bar(avg_scores, 
                                    x='employee_name', 
                                    y=['quality', 'punctuality', 'teamwork', 'targets'],
                                    barmode='group', 
                                    title="Average Performance Scores by Employee")
                        fig.update_layout(
                            xaxis_title="Employee",
                            yaxis_title="Score",
                            legend_title="Metrics"
                        )
                        st.plotly_chart(fig)
                        
                        # Show average scores table
                        st.write("Team Average Scores:")
                        st.dataframe(avg_scores.set_index('employee_name').round(2))
                else:
                    st.info("No valid evaluation data for the selected employee.")
            else:
                st.info("No evaluations available for the selected employee.")
        else:
            st.info("No team members found.")

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
