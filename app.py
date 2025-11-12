from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.secret_key='ISA12_SE'

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/')
def index():
    conn = sqlite3.connect('part_a.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Trips')
    all_trips = cursor.fetchall()
    conn.close()
    return render_template('index.html', trips=all_trips)

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        trip_location = request.form.get('trip_location')
        trip_start = request.form.get('trip_start')
        trip_end = request.form.get('trip_end')
        trip_description = request.form.get('trip_description')
        rating = request.form.get('rating')
        
        # Handle file upload
        if 'trip_image' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['trip_image']
        
        if file.filename == '':
            return "No file selected", 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to make filename unique
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            trip_image = f"uploads/{filename}"
        else:
            return "Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP", 400

        conn = sqlite3.connect('part_a.db')
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO Trips (trip_location, trip_start, trip_end, trip_image, trip_description, rating)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (trip_location, trip_start, trip_end, trip_image, trip_description, rating))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('form.html')

@app.route('/update/<int:trip_id>', methods=['POST','GET'])
def update(trip_id):
    conn = sqlite3.connect('part_a.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        trip_location = request.form.get('trip_location')
        trip_start = request.form.get('trip_start')
        trip_end = request.form.get('trip_end')
        trip_description = request.form.get('trip_description')
        rating = request.form.get('rating')

        import re
        from datetime import datetime
        
        if not re.match(r'^[a-zA-Z\s,.-]+$', trip_location):
            conn.close()
            return "Invalid location format. Only letters, spaces, commas, periods, and hyphens allowed.", 400
        
        try:
            start = datetime.strptime(trip_start, '%Y-%m-%d')
            end = datetime.strptime(trip_end, '%Y-%m-%d')
            if end < start:
                conn.close()
                return "End date must be after start date.", 400
        except ValueError:
            conn.close()
            return "Invalid date format.", 400
        
        if trip_description and len(trip_description) > 250:
            conn.close()
            return "Description must be 250 characters or less.", 400
        
        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                conn.close()
                return "Rating must be between 1 and 5.", 400
        except (ValueError, TypeError):
            conn.close()
            return "Invalid rating. Please select a rating.", 400

        # Handle file upload for update
        if 'trip_image' in request.files and request.files['trip_image'].filename != '':
            file = request.files['trip_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                trip_image = f"uploads/{filename}"
            else:
                conn.close()
                return "Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP", 400
        else:
            # Keep the existing image if no new file uploaded
            cursor.execute('SELECT trip_image FROM Trips WHERE trip_id = ?', (trip_id,))
            result = cursor.fetchone()
            trip_image = result['trip_image'] if result else None

        cursor.execute('''
            UPDATE Trips 
            SET trip_location = ?, 
                trip_start = ?, 
                trip_end = ?, 
                trip_image = ?,
                trip_description = ?,
                rating = ?
            WHERE trip_id = ?
        ''', (trip_location, trip_start, trip_end, trip_image, trip_description, rating, trip_id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    else:
        cursor.execute('SELECT * FROM Trips WHERE trip_id = ?', (trip_id,))
        trip = cursor.fetchone()
        conn.close()

        if trip is None:
            return "Trip not found", 404
        
        return render_template('update.html', trip=trip)

@app.route('/delete/<int:trip_id>')
def delete(trip_id):
    conn = sqlite3.connect('part_a.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Trips WHERE trip_id=?', (trip_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/journal')
def journal():
    return render_template('journal.html')

@app.route('/album')
def album():
    return render_template('album.html')

@app.route('/trip/<int:trip_id>')
def trip(trip_id):
    conn = sqlite3.connect('part_a.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Trips WHERE trip_id = ?', (trip_id,))
    trip = cursor.fetchone()
    conn.close()
    
    if trip is None:
        return "Trip not found", 404
    
    return render_template('trip.html', trip=trip)

if __name__ == '__main__':
    app.run(debug=True)
    
