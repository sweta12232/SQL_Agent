import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import json

class SQLMentorAgent:
    def __init__(self, api_key=None, db_path="sample.db"):
        """Initialize the SQL Mentor Agent"""
        load_dotenv()
        
        # Configuration
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API is not correct")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            generation_config={
                'temperature': 0.2,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        
        # Database setup
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Initialize sample database if empty
        self._initialize_sample_db()
        
        # Learning tracking
        self.chat_history = []
        self.student_progress = {}
    
    def _initialize_sample_db(self):
        """Create sample tables if they don't exist"""
        # Check if tables exist
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        if not self.cursor.fetchall():
            # Create sample tables
            self.cursor.execute("""
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    grade INTEGER,
                    email TEXT
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE courses (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    teacher TEXT,
                    room_number TEXT
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE enrollments (
                    student_id INTEGER,
                    course_id INTEGER,
                    enrollment_date TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (course_id) REFERENCES courses(id)
                )
            """)
            
            # Insert sample data
            students = [
                (1, 'Alice Johnson', 15, 92, 'alice@school.edu'),
                (2, 'Bob Smith', 16, 85, 'bob@school.edu'),
                (3, 'Charlie Brown', 15, 78, 'charlie@school.edu'),
                (4, 'Diana Prince', 17, 95, 'diana@school.edu'),
                (5, 'Ethan Hunt', 16, 88, 'ethan@school.edu')
            ]
            
            courses = [
                (101, 'Mathematics', 'Mr. Anderson', 'Room 101'),
                (102, 'Science', 'Dr. Watson', 'Lab 2'),
                (103, 'History', 'Mrs. Parker', 'Room 205'),
                (104, 'English', 'Ms. Lang', 'Room 104')
            ]
            
            enrollments = [
                (1, 101, '2023-09-01'),
                (1, 102, '2023-09-01'),
                (2, 101, '2023-09-01'),
                (3, 103, '2023-09-02'),
                (4, 102, '2023-09-01'),
                (4, 104, '2023-09-03'),
                (5, 101, '2023-09-01'),
                (5, 103, '2023-09-02')
            ]
            
            self.cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?)", students)
            self.cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, ?)", courses)
            self.cursor.executemany("INSERT INTO enrollments VALUES (?, ?, ?)", enrollments)
            self.conn.commit()
    
    def ask_gemini(self, prompt, structured_output=False):
        """Send a prompt to Gemini and get a response"""
        try:
            if structured_output:
                response = self.model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            print(f"Error communicating with Gemini API: {str(e)}")
            return {"error": str(e)} if structured_output else f"Error: {str(e)}"
    
    def execute_sql(self, query):
        """Execute SQL query and return results"""
        try:
            df = pd.read_sql_query(query, self.conn)
            return {"success": True, "data": df.to_string(index=False)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def explain_concept(self, concept, student_level="beginner"):
        """Generate an explanation for an SQL concept"""
        prompt = f"""
        Explain this SQL concept to a {student_level} student: {concept}
        
        Include:
        1. Simple definition
        2. Why it's important
        3. Basic syntax with example
        4. Common mistakes
        5. A practice exercise
        
        Use friendly, simple language with real-world analogies.
        """
        return self.ask_gemini(prompt)
    
    def evaluate_student_query(self, question, student_query):
        """Evaluate a student's SQL query"""
        execution_result = self.execute_sql(student_query)
        
        prompt = f"""
        Evaluate this SQL query:
        
        Question: {question}
        Student's Query: {student_query}
        
        Execution Result: {"Success" if execution_result["success"] else "Failed: " + execution_result["error"]}
        {execution_result["data"] if execution_result["success"] else ""}
        
        Provide feedback with:
        1. Is it correct? If not, what's wrong?
        2. What's done well?
        3. How to improve?
        4. Simplified error explanation if needed
        
        Format as:
        - Correctness: [Correct/Incorrect]
        - Feedback: [Detailed feedback]
        - Strengths: [List of good points]
        - Improvements: [List of suggestions]
        """
        return self.ask_gemini(prompt)
    
    def generate_practice_problem(self, concepts, difficulty="easy"):
        """Generate a practice problem"""
        prompt = f"""
        Create an SQL practice problem about: {concepts}
        Difficulty: {difficulty}
        
        Our database has:
        - students (id, name, age, grade, email)
        - courses (id, name, teacher, room_number)
        - enrollments (student_id, course_id, enrollment_date)
        
        Provide:
        1. Clear problem statement
        2. 2-3 hints
        3. Sample solution
        4. Expected output description
        
        Format as:
        Problem: [description]
        Hints:
        1. [hint 1]
        2. [hint 2]
        Solution: [SQL query]
        Expected Output: [description]
        """
        return self.ask_gemini(prompt)
    
    def interactive_learning(self):
        """Interactive learning session"""
        print("\nWelcome to SQL Mentor!\n")
        print("Available commands:")
        print("1. explain [concept] - Learn about an SQL concept")
        print("2. practice [topic] - Get a practice problem")
        print("3. evaluate [query] - Check your SQL query")
        print("4. query [sql] - Run an SQL query")
        print("5. help - Show this menu")
        print("6. exit - End the session\n")
        
        while True:
            user_input = input("\nWhat would you like to do? ").strip().lower()
            
            if user_input.startswith("exit"):
                print("Goodbye! Happy learning!")
                break
                
            elif user_input.startswith("help"):
                print("\nAvailable commands:")
                print("1. explain [concept] - Learn about an SQL concept")
                print("2. practice [topic] - Get a practice problem")
                print("3. evaluate [query] - Check your SQL query")
                print("4. query [sql] - Run an SQL query")
                print("5. help - Show this menu")
                print("6. exit - End the session")
                
            elif user_input.startswith("explain"):
                concept = user_input[8:].strip()
                if concept:
                    print(f"\nExplaining {concept}...\n")
                    print(self.explain_concept(concept))
                else:
                    print("Please specify a concept to explain (e.g., 'explain JOINs')")
                    
            elif user_input.startswith("practice"):
                topic = user_input[8:].strip()
                if topic:
                    print(f"\nGenerating practice problem about {topic}...\n")
                    print(self.generate_practice_problem(topic))
                else:
                    print("Please specify a topic (e.g., 'practice SELECT')")
                    
            elif user_input.startswith("evaluate"):
                query = user_input[8:].strip()
                if query:
                    question = input("What was this query trying to do? ").strip()
                    print("\nEvaluating your query...\n")
                    print(self.evaluate_student_query(question, query))
                else:
                    print("Please provide a query to evaluate (e.g., 'evaluate SELECT * FROM students')")
                    
            elif user_input.startswith("query"):
                query = user_input[5:].strip()
                if query:
                    print("\nRunning your query...\n")
                    result = self.execute_sql(query)
                    if result["success"]:
                        print("Query successful!\n")
                        print(result["data"])
                    else:
                        print("Error in query:")
                        print(result["error"])
                else:
                    print("Please provide a query to run (e.g., 'query SELECT * FROM students')")
                    
            else:
                print("I didn't understand that. Type 'help' for available commands.")

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

def main():
    # Initialize the agent
    try:
        agent = SQLMentorAgent()
        print("SQL Mentor Agent initialized successfully!")
        print(f"Using database: {agent.db_path}")
        
        # Start interactive session
        agent.interactive_learning()
        
    except Exception as e:
        print(f"Failed to initialize SQL Mentor: {str(e)}")
    finally:
        if 'agent' in locals():
            agent.close()

if __name__ == "__main__":
    main()