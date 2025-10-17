from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app import mysql

main_bp = Blueprint('main', __name__)

# --- Home route ---
@main_bp.route('/')
def home():
    return render_template('home.html')


# --- Dashboard route (list all doctors) ---
@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()

    return render_template('dashboard.html', doctors=doctors)


# --- Book appointment route ---
@main_bp.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
def book_appointment(doctor_id):
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        patient_id = session['user_id']

        # Basic validation
        if not date or not time:
            flash('Please select both date and time.', 'danger')
            return redirect(url_for('main.book_appointment', doctor_id=doctor_id))

        try:
            with mysql.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (%s, %s, %s, %s)",
                    (patient_id, doctor_id, date, time)
                )
                mysql.connection.commit()
            flash('Appointment booked successfully!', 'success')
        except Exception as e:
            flash(f'Error booking appointment: {e}', 'danger')
            return redirect(url_for('main.book_appointment', doctor_id=doctor_id))

        return redirect(url_for('main.my_appointments'))

    # GET request: fetch doctor details
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors WHERE id = %s", [doctor_id])
        doctor = cursor.fetchone()

    return render_template('book.html', doctor=doctor)


# --- List all upcoming appointments for current user ---
@main_bp.route('/my_appointments')
def my_appointments():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    patient_id = session['user_id']

    with mysql.connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, d.name AS doctor_name, d.specialty, a.date, a.time
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.patient_id = %s
            ORDER BY a.date, a.time
        """, [patient_id])
        appointments = cursor.fetchall()

    return render_template('my_appointments.html', appointments=appointments)


@main_bp.route('/test-db')
def test_db():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE();")
    db = cur.fetchone()
    return f"Connected to: {db}"


