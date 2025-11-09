from flask import Flask, render_template, request
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

    print('num of trips:', len(all_trips))
    for trip in all_trips:
        print('Trip:', dict(trip))
    return render_template('index.html', trips=all_trips)

@app.route('/form')
def add():
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
