from flask import Flask, flash, redirect, render_template, request, jsonify, url_for, session  # type: ignore
from flask_mail import Mail, Message  # type: ignore
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Configure Flask-Mail using .env
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER", 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS", 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

mail = Mail(app)

# Simulated photographers data
photographers = [
    {"id": "p1", "name": "amit", "skills": ["Wedding", "Portrait"], "image": "amit.jpg", "location": "Hyderabad"},
    {"id": "p2", "name": "sana", "skills": ["Fashion", "Event"], "image": "sana.jpg", "location": "Mumbai"},
    {"id": "p3", "name": "robo", "skills": ["All Events", "Event"], "image": "photo.jpg", "location": "Benguluru"}
]

availability_data = {
    "p1": ["2025-06-20", "2025-06-23"],
    "p2": ["2025-06-19", "2025-06-22"],
    "p3": ["2025-07-21", "2025-07-26"]
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        booking = {
            "photographer_id": request.form.get('photographer_id'),
            "user_id": request.form.get('user_id'),
            "date": request.form.get('booking_date'),
            "full_name": request.form.get('full_name'),
            "email": request.form.get('email'),
            "contact": request.form.get('contact'),
            "location": request.form.get('location'),
            "notes": request.form.get('notes')
        }
        session['booking_details'] = booking
        return redirect(url_for("payment"))
    return render_template('book.html')

@app.route('/show-photographers')
def show_photographers():
    query = request.args.get('location', '').lower()
    filtered = [p for p in photographers if query in p['location'].lower()] if query else photographers
    return render_template('photographers.html', photographers=filtered, availability_data=availability_data, request=request)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # For demo: Allow any username/password
        session['user'] = username
        return redirect('/')  # Redirect to home page after login

    return render_template('login.html')




@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('newUsername')
    password = request.form.get('newPassword')

    # For demo: Simply store username in session
    session['user'] = username
    flash('Signup successful! You are now logged in.')
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', photographers=photographers, availability_data=availability_data)

@app.route('/my-bookings')
def my_bookings():
    bookings = []  # Placeholder for real booking data
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/search')
def search_photographers():
    category = request.args.get('category')
    location = request.args.get('location')
    results = [
        p for p in photographers
        if category in p['skills'] and location.lower() in p['location'].lower()
    ]
    return render_template('results.html', results=results, category=category, location=location)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    booking = session.get("booking_details")
    if not booking:
        return redirect(url_for("book"))

    if request.method == "POST":
        selected_package = request.form.get("package")
        return redirect(url_for("confirmation", package=selected_package))

    return render_template("payment.html", booking=booking)

@app.route('/confirmation', methods=['POST'])
def confirmation():
    package = request.args.get("package") or request.form.get("package")
    booking = session.get("booking_details")

    if booking:
        msg = Message(
            subject="📸 Booking Confirmed - Capture Moments",
            sender=app.config['MAIL_USERNAME'],
            recipients=[booking["email"]],
            body=f"""Hello {booking['full_name']},

Thank you for booking with Capture Moments!

✔️ Photographer ID: {booking['photographer_id']}
📅 Date: {booking['date']}
📦 Package: {package}
📍 Location: {booking['location']}

We’ll follow up with details and confirmations. Feel free to reach out if you need anything.

— The Capture Moments Team"""
        )
        mail.send(msg)

    return render_template("confirmation.html", booking=booking, package=package)

if __name__ == '__main__':
    app.run(debug=True)
