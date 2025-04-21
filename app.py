# app.py
import streamlit as st
from mentor import SQLMentorAgent
import time
import pandas as pd

# Configure page
st.set_page_config(
    page_title="SQL Mentor",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling (with high contrast buttons and text)
st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
            color: #fff0f0;  /* Black text color for the app */
        }
        .sidebar {
            background-color: #f0e4e4  /* Darker sidebar background */
        }
        .sidebar .sidebar-content {
            background-color: #2c3e50;  /* Darker sidebar background */
        }
        /* Make sidebar text white for better contrast */
        .sidebar p, .sidebar div, .sidebar span, .sidebar label, .sidebar h1, .sidebar h2, .sidebar h3 {
            color: #ffffff !important;  /* White text in sidebar */
        }
        h1, h2, h3 {
            color: #000000;  /* Black text for headings */
        }
        /* High contrast button styling */
        .stButton>button {
            background-color: #f8f9fa;  /* Bright blue buttons */
            color: #000000; /* White text on buttons */
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            font-weight: bold;
            font-size: 16px;  /* Larger text */
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);  /* Text shadow for better visibility */
        }
        .stButton>button:hover {
            background-color: ##f8f9fa;  /* Darker blue on hover */
            transition: 0.3s ease;
        }
        /* Special styling for sidebar buttons with even higher contrast */
        .sidebar .stButton>button {
            background-color: #e74c3c;  /* Red for sidebar buttons - high contrast */
            color: #ffffff;  /* White text */
            border: 2px solid #ffffff;  /* White border */
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        .sidebar .stButton>button:hover {
            background-color: #c0392b;  /* Darker red on hover */
        }
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 8px;
            color: #ffffff;  /* Black text for inputs */
        }
        .success-message {
            color: #2e7d32;
            font-weight: bold;
        }
        .error-message {
            color: #c62828;
            font-weight: bold;
        }
        /* Ensure all main content text is black by default */
        p, div, span, label {
            color: #000000;
        }
        /* Override Streamlit's default text colors */
        .st-bb, .st-at, .st-af, .st-ag {
            color: #f0e4e4 !important;
        }
        /* Make generate practice problem button stand out */
        button[data-testid="baseButton-secondary"] {
            background-color: #3498db !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        /* Make progress bar more visible */
        .stProgress > div > div {
            background-color: #e74c3c !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mentor' not in st.session_state:
    try:
        st.session_state.mentor = SQLMentorAgent()
        st.session_state.mentor_ready = True
    except Exception as e:
        st.error(f"Failed to initialize SQL Mentor: {str(e)}")
        st.session_state.mentor_ready = False

# Sidebar - User Profile
with st.sidebar:
    st.title("🧑‍🏫 SQL Mentor")
    st.markdown("Learn SQL with AI assistance!")
    
    if st.session_state.mentor_ready:
        st.success("Connected to SQL Mentor")
        st.markdown("---")
        
        # Learning progress
        st.subheader("Your Progress")
        progress = st.slider("SQL Mastery", 0, 100, 25)
        st.progress(progress)
        
        # Quick actions
        st.markdown("---")
        st.subheader("Quick Actions")
        if st.button("🔄 Reset Session"):
            st.session_state.clear()
            st.rerun()
    else:
        st.error("Connection failed")

# Main content
st.title("SQL Learning Center")
st.markdown("Welcome to your interactive SQL learning assistant!")

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs([
    "📚 Learn Concepts", 
    "💻 Practice Problems", 
    "🔍 Query Evaluator", 
    "📊 Run Queries"
])

# Tab 1: Concept Learning
with tab1:
    st.header("Learn SQL Concepts")
    concept = st.text_input("What SQL concept would you like to learn about?", 
                          placeholder="e.g., JOIN, GROUP BY, subqueries")
    
    if concept:
        with st.spinner(f"Preparing explanation about {concept}..."):
            explanation = st.session_state.mentor.explain_concept(concept)
            st.markdown("### Explanation")
            st.markdown(explanation)
            
            # Save to history
            if 'learning_history' not in st.session_state:
                st.session_state.learning_history = []
            st.session_state.learning_history.append({
                'type': 'concept',
                'topic': concept,
                'content': explanation
            })

# Tab 2: Practice Problems
with tab2:
    st.header("Practice SQL Problems")
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input("What topic do you want to practice?", 
                             placeholder="e.g., WHERE clause, JOINs")
        difficulty = st.selectbox("Select difficulty", 
                                ["Beginner", "Intermediate", "Advanced"])
    
    if st.button("Generate Practice Problem"):
        if topic:
            with st.spinner("Creating a custom practice problem for you..."):
                problem = st.session_state.mentor.generate_practice_problem(topic, difficulty.lower())
                
                st.session_state.current_problem = problem
                st.markdown("### Problem Statement")
                st.markdown(problem.split("Problem:")[1].split("Hints:")[0])
                
                with st.expander("💡 Hints"):
                    hints = problem.split("Hints:")[1].split("Solution:")[0]
                    st.markdown(hints)
                
                with st.expander("📝 Try your solution"):
                    user_solution = st.text_area("Write your SQL solution here", height=100)
                    if st.button("Submit Solution"):
                        with st.spinner("Evaluating your solution..."):
                            evaluation = st.session_state.mentor.evaluate_student_query(
                                problem.split("Problem:")[1].split("Hints:")[0],
                                user_solution
                            )
                            st.markdown("### Feedback")
                            st.markdown(evaluation)
        else:
            st.warning("Please enter a topic to practice")

# Tab 3: Query Evaluator
with tab3:
    st.header("Get Feedback on Your SQL")
    question = st.text_area("What are you trying to accomplish with your query?",
                          placeholder="Describe what you want the query to do")
    user_query = st.text_area("Enter your SQL query here", 
                            height=150,
                            placeholder="SELECT * FROM students WHERE grade > 90")
    
    if st.button("Evaluate My Query"):
        if user_query:
            with st.spinner("Analyzing your query..."):
                evaluation = st.session_state.mentor.evaluate_student_query(question, user_query)
                st.markdown("### Evaluation Results")
                st.markdown(evaluation)
        else:
            st.warning("Please enter a query to evaluate")

# Tab 4: Query Runner
with tab4:
    st.header("Run SQL Queries")
    query = st.text_area("Enter SQL query to execute", 
                       height=150,
                       placeholder="SELECT * FROM students")
    
    if st.button("Execute Query"):
        if query:
            with st.spinner("Running your query..."):
                result = st.session_state.mentor.execute_sql(query)
                if result["success"]:
                    st.success("Query executed successfully!")
                    st.markdown("### Results")
                    st.dataframe(pd.read_json(result["data"]), use_container_width=True)
                else:
                    st.error("Query failed")
                    st.markdown("### Error Message")
                    st.code(result["error"], language="sql")
        else:
            st.warning("Please enter a query to execute")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #000000;">
        <p>SQL Mentor Agent - Learn SQL with AI Assistance</p>
    </div>
""", unsafe_allow_html=True)