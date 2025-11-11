from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key='ISA12_SE'

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
        trip_image = request.form.get('trip_description')
        trip_description = request.form.get('trip_description')
        rating = request.form.get('rating')

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


@app.route('/journal')
def journal():
    return render_template('journal.html')

@app.route('/album')
def album():
    return render_template('album.html')

@app.route('/trip')
def trip():
    return render_template('trip.html')



if __name__ == '__main__':
    app.run(debug=True)
    
