import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, url_for, session


def loadClubs():
    with open("clubs.json", 'r', encoding='utf-8') as club:
        listOfClubs = json.load(club)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json", 'r', encoding='utf-8') as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


def init_booking_tracker():
    return [{
        "name": comp["name"],
        "alreadyBooked": "0"
    } for comp in competitions]


app = Flask(__name__)
app.secret_key = "something_special"
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)    # Lifetime of sessions
#app.config['SESSION_REFRESH_EACH_REQUEST'] = True                  # Session refresh behavior
#app.config["SESSION_COOKIE_SECURE"] = True                         # True if using HTTPS, else false
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"                       # Or "Strict"


competitions = loadCompetitions()
clubs = loadClubs()
placeCost = 1            # Point(s)
maxPlaces = 12           # Maximum places per competition, per club
bookingDeadlineDays = 1  # Booking possible until X days before competition date


@app.route("/")
def index():
    session.clear()  # or better session.pop('connected', None)
    return render_template("index.html")


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email')
    club = next((club for club in clubs if club['email'] == email), None)

    if not club:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    
    # Add session bool
    session['connected'] = True
    
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions,
        bookingDeadlineDays=bookingDeadlineDays
    )


@app.route("/book/<competition>/<club>", methods=["GET"])
def book(competition, club):
    # Club & Competition lookup
    foundClub = next((c for c in clubs if c["name"] == club), None)
    foundCompetition = next((c for c in competitions if c["name"] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Invalid club or competition. Please log in again.", "error")
        return redirect(url_for("index"))

    # Render booking
    return render_template(
        "booking.html",
        club=foundClub,
        competition=foundCompetition,
        maxPlaces=maxPlaces
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    try:
        # Initialize booking_tracker
        if 'booking_tracker' not in session:
            session['booking_tracker'] = init_booking_tracker()

        # Look for club & competition data
        competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
        club = next((c for c in clubs if c['name'] == request.form['club']), None)

        if not competition or not club:
            flash("Competition or club not found!")
            return redirect(url_for('index'))

        # 1. Date validation
        competition_date = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        booking_deadline = competition_date - timedelta(days=bookingDeadlineDays)
        if current_date >= booking_deadline:
            flash("This competition is no longer bookable.")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )

        # 2. Input validation
        placesRequired = int(request.form['places'])
        if placesRequired <= 0:
            flash("Places to book must be a positive integer.")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions
            )

        # 3. Competition/Places availability
        available_places = int(competition['numberOfPlaces'])
        if available_places == 0:
            flash("This competition is full.")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )
        if placesRequired > available_places:
            flash("This competition does not have this amount available.")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )

        # 4. Booking limit validation
        booking_tracker = session['booking_tracker']
        current_booking = next((b for b in booking_tracker if b['name'] == competition['name']), None)
        if not current_booking:
            current_booking = {"name": competition['name'], "alreadyBooked": "0"}
            booking_tracker.append(current_booking)
        total_booked = int(current_booking['alreadyBooked']) + placesRequired
        if total_booked > maxPlaces:
            flash(f"Clubs are limited to {maxPlaces} places for one competition.")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )

        # 5. Points validation
        points_needed = placesRequired * placeCost
        if points_needed > int(club['points']):
            flash("Not enough points!")
            return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )

        # Everything validated, update values
        competition['numberOfPlaces'] = str(available_places - placesRequired)
        club['points'] = str(int(club['points']) - points_needed)
        current_booking['alreadyBooked'] = str(total_booked)
        session['booking_tracker'] = booking_tracker

        flash("Great-booking complete!")
        return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )

    except ValueError:
        flash("Invalid number of places!")
        return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )
    except Exception as e:
        app.logger.error(f"Error in purchasePlaces: {str(e)}")
        flash("An unexpected error occurred. Please try again.")
        return render_template(
                'welcome.html',
                club=club,
                competitions=competitions,
                bookingDeadlineDays=bookingDeadlineDays
            )


@app.route('/board')
def board():
    return render_template(
        'board.html',
        clubs=clubs,
        connected=session.get('connected', False)
    )


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
