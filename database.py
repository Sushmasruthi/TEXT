import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def create_connection():
    try:
        conn = sqlite3.connect('education.db')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            
            # Create students table
            c.execute('''CREATE TABLE IF NOT EXISTS students
                        (id TEXT PRIMARY KEY, 
                         full_name TEXT NOT NULL,
                         department TEXT NOT NULL,
                         password TEXT NOT NULL)''')
            
            # Create teachers table
            c.execute('''CREATE TABLE IF NOT EXISTS teachers
                        (id TEXT PRIMARY KEY,
                         full_name TEXT NOT NULL,
                         department TEXT NOT NULL,
                         specialization TEXT NOT NULL,
                         password TEXT NOT NULL)''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

def check_existing_id(user_id):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            
            # Check in students table
            c.execute('SELECT id FROM students WHERE id = ?', (user_id,))
            if c.fetchone():
                return True, "Student ID already exists"
            
            # Check in teachers table
            c.execute('SELECT id FROM teachers WHERE id = ?', (user_id,))
            if c.fetchone():
                return True, "Teacher ID already exists"
            
            return False, ""
        finally:
            conn.close()
    return True, "Database error"

def register_student(student_id, full_name, department, password):
    # Check if ID already exists
    exists, message = check_existing_id(student_id)
    if exists:
        return False, message
    
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO students (id, full_name, department, password) VALUES (?, ?, ?, ?)',
                     (student_id, full_name, department, hashed_password))
            conn.commit()
            return True, "Student registration successful!"
        except sqlite3.Error as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error"

def register_teacher(teacher_id, full_name, department, specialization, password):
    # Check if ID already exists
    exists, message = check_existing_id(teacher_id)
    if exists:
        return False, message
    
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO teachers (id, full_name, department, specialization, password) VALUES (?, ?, ?, ?, ?)',
                     (teacher_id, full_name, department, specialization, hashed_password))
            conn.commit()
            return True, "Teacher registration successful!"
        except sqlite3.Error as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error"

def verify_student(student_id, password):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            student = c.fetchone()
            
            if not student:
                return False, "Invalid Student ID"
            
            if check_password_hash(student[3], password):
                return True, {
                    "id": student[0],
                    "full_name": student[1],
                    "department": student[2]
                }
            return False, "Invalid Password"
        finally:
            conn.close()
    return False, "Database connection error"

def verify_teacher(teacher_id, password):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,))
            teacher = c.fetchone()
            
            if not teacher:
                return False, "Invalid Teacher ID"
            
            if check_password_hash(teacher[4], password):
                return True, {
                    "id": teacher[0],
                    "full_name": teacher[1],
                    "department": teacher[2]
                }
            return False, "Invalid Password"
        finally:
            conn.close()
    return False, "Database connection error"

class Database:
    def __init__(self, db_file="exam_analysis.db"):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create Teachers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    department TEXT NOT NULL
                )
            ''')

            # Create Classes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year TEXT NOT NULL,  -- FY, SY, TY, Final
                    department TEXT NOT NULL,
                    academic_year TEXT NOT NULL
                )
            ''')

            # Create Subjects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    class_id INTEGER,
                    teacher_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes (id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
                )
            ''')

            # Create Exams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exam_type TEXT NOT NULL,  -- MID1, MID2
                    subject_id INTEGER,
                    date_conducted DATE NOT NULL,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            ''')

            # Create Student Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exam_id INTEGER,
                    roll_number TEXT NOT NULL,
                    Q1a INTEGER, Q1b INTEGER, Q1c INTEGER, Q1d INTEGER,
                    Q2a INTEGER, Q2b INTEGER, Q2c INTEGER, Q2d INTEGER,
                    Q3a INTEGER, Q3b INTEGER, Q3c INTEGER, Q3d INTEGER,
                    Q4a INTEGER, Q4b INTEGER, Q4c INTEGER, Q4d INTEGER,
                    Q5a INTEGER, Q5b INTEGER, Q5c INTEGER, Q5d INTEGER,
                    Q6a INTEGER, Q6b INTEGER, Q6c INTEGER, Q6d INTEGER,
                    total_marks INTEGER,
                    FOREIGN KEY (exam_id) REFERENCES exams (id)
                )
            ''')

    def save_exam_results(self, exam_data, results_data):
        """Save exam results to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert exam details
            cursor.execute('''
                INSERT INTO exams (exam_type, subject_id, date_conducted)
                VALUES (?, ?, ?)
            ''', (exam_data['exam_type'], exam_data['subject_id'], datetime.now().date()))
            
            exam_id = cursor.lastrowid
            
            # Insert student results
            for result in results_data:
                cursor.execute('''
                    INSERT INTO student_results (
                        exam_id, roll_number,
                        Q1a, Q1b, Q1c, Q1d,
                        Q2a, Q2b, Q2c, Q2d,
                        Q3a, Q3b, Q3c, Q3d,
                        Q4a, Q4b, Q4c, Q4d,
                        Q5a, Q5b, Q5c, Q5d,
                        Q6a, Q6b, Q6c, Q6d,
                        total_marks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    exam_id,
                    result['roll_number'],
                    *[result['questions'][f'Q{i}'][part] for i in range(1, 7) for part in ['a', 'b', 'c', 'd']],
                    result['total_marks']
                ))

    def get_analysis(self, class_id=None, exam_type=None, subject_id=None):
        """Get analysis of exam results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_students,
                    COUNT(CASE WHEN total_marks >= 40 THEN 1 END) as passed_students,
                    MAX(total_marks) as highest_mark,
                    MIN(total_marks) as lowest_mark,
                    AVG(total_marks) as average_mark
                FROM student_results sr
                JOIN exams e ON sr.exam_id = e.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE 1=1
            """
            params = []
            
            if class_id:
                query += " AND s.class_id = ?"
                params.append(class_id)
            
            if exam_type:
                query += " AND e.exam_type = ?"
                params.append(exam_type)
                
            if subject_id:
                query += " AND s.id = ?"
                params.append(subject_id)
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                total_students, passed_students, highest, lowest, average = result
                pass_percentage = (passed_students / total_students * 100) if total_students > 0 else 0
                
                return {
                    'total_students': total_students,
                    'pass_percentage': round(pass_percentage, 2),
                    'highest_mark': highest,
                    'lowest_mark': lowest,
                    'average_mark': round(average, 2) if average else 0
                }
            return None

class ResultsDatabase:
    def __init__(self, db_file="exam_results.db"):
        self.db_file = db_file
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables for storing results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_number TEXT NOT NULL,
                    class_year TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    exam_type TEXT NOT NULL,
                    academic_year TEXT NOT NULL,
                    total_marks FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(roll_number, subject, exam_type, academic_year)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    question_number INTEGER NOT NULL,
                    part_a FLOAT DEFAULT 0,
                    part_b FLOAT DEFAULT 0,
                    part_c FLOAT DEFAULT 0,
                    part_d FLOAT DEFAULT 0,
                    FOREIGN KEY (result_id) REFERENCES students_results(id),
                    UNIQUE(result_id, question_number)
                )
            ''')

    def save_results(self, results, class_year, subject, exam_type, academic_year):
        """Save results to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for entry in results:
                try:
                    # Insert student result
                    cursor.execute('''
                        INSERT INTO students_results 
                        (roll_number, class_year, subject, exam_type, academic_year, total_marks)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        entry['roll_number'],
                        class_year,
                        subject,
                        exam_type,
                        academic_year,
                        entry['total_marks']
                    ))
                    
                    result_id = cursor.lastrowid
                    
                    # Insert question marks
                    for q_num, q_data in entry['questions'].items():
                        q_num = int(q_num[1])  # Extract number from 'Q1', 'Q2', etc.
                        cursor.execute('''
                            INSERT INTO question_marks 
                            (result_id, question_number, part_a, part_b, part_c, part_d)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            result_id,
                            q_num,
                            q_data['a'],
                            q_data['b'],
                            q_data['c'],
                            q_data['d']
                        ))
                    
                except Exception as e:
                    print(f"Error saving result for {entry.get('roll_number')}: {str(e)}")
                    continue

# Initialize the database when the module is imported
init_db() 