from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import init_db, register_student, register_teacher, verify_student, verify_teacher
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Initialize the database
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('portal.html')

@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        try:
            # Try to get JSON data first
            if request.is_json:
                data = request.get_json()
                student_id = data.get('studentId')
                full_name = data.get('fullName')
                department = data.get('department')
                password = data.get('password')
            else:
                # Fall back to form data
                student_id = request.form.get('studentId')
                full_name = request.form.get('fullName')
                department = request.form.get('department')
                password = request.form.get('password')

            if not all([student_id, full_name, department, password]):
                return jsonify({
                    'success': False,
                    'message': 'All fields are required'
                }), 400

            success, message = register_student(student_id, full_name, department, password)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Please login.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    return render_template('student_register.html')

@app.route('/teacher/register', methods=['GET', 'POST'])
def teacher_register():
    if request.method == 'POST':
        try:
            # Try to get JSON data first
            if request.is_json:
                data = request.get_json()
                teacher_id = data.get('teacherId')
                full_name = data.get('fullName')
                department = data.get('department')
                specialization = data.get('specialization')
                password = data.get('password')
            else:
                # Fall back to form data
                teacher_id = request.form.get('teacherId')
                full_name = request.form.get('fullName')
                department = request.form.get('department')
                specialization = request.form.get('specialization')
                password = request.form.get('password')

            if not all([teacher_id, full_name, department, specialization, password]):
                return jsonify({
                    'success': False,
                    'message': 'All fields are required'
                }), 400

            success, message = register_teacher(teacher_id, full_name, department, specialization, password)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Please login.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    return render_template('teacher_register.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        try:
            # Try to get JSON data first
            if request.is_json:
                data = request.get_json()
                student_id = data.get('studentId')
                password = data.get('password')
            else:
                # Fall back to form data
                student_id = request.form.get('studentId')
                password = request.form.get('password')

            if not student_id or not password:
                return jsonify({'success': False, 'message': 'Both ID and password are required'}), 400

            success, result = verify_student(student_id, password)
            
            if success:
                session['user_id'] = student_id
                session['user_type'] = 'student'
                session['full_name'] = result['full_name']
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return jsonify({'success': False, 'message': result}), 401
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
            
    return render_template('student_login.html')

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        try:
            # Try to get JSON data first
            if request.is_json:
                data = request.get_json()
                teacher_id = data.get('teacherId')
                password = data.get('password')
            else:
                # Fall back to form data
                teacher_id = request.form.get('teacherId')
                password = request.form.get('password')

            if not teacher_id or not password:
                return jsonify({'success': False, 'message': 'Both ID and password are required'}), 400

            success, result = verify_teacher(teacher_id, password)
            
            if success:
                session['user_id'] = teacher_id
                session['user_type'] = 'teacher'
                session['full_name'] = result['full_name']
                return jsonify({'success': True, 'message': 'Login successful'})
            else:
                return jsonify({'success': False, 'message': result}), 401
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
            
    return render_template('teacher_login.html')

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if session.get('user_type') != 'student':
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    return render_template('student_dashboard.html', name=session.get('full_name'))

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('user_type') != 'teacher':
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    return render_template('teacher_dashboard.html',
                         teacher_name=session.get('full_name'),
                         department=session.get('department'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)