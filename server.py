import json
from flask import Flask, render_template, request, redirect, flash, url_for, session


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


def init_booking_tracker():
    return [{
        "name": comp["name"],
        "alreadyBooked": "0"
    } for comp in competitions]


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()
placeCost = 1   # Point(s)
maxPlaces = 12  # Maximum places per competition, per club


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email')
    club = next((club for club in clubs if club['email'] == email), None)

    if not club:
        flash("Sorry, that email wasn't found.")
        return redirect(url_for('index'))
    
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )
    else:
        flash("Something went wrong-please try again")
        return render_template("welcome.html", club=club, competitions=competitions)


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
            flash('Competition or club not found!')
            return render_template('welcome.html', club=club, competitions=competitions)
        
        # 1. Input validation
        placesRequired = int(request.form['places'])
        if placesRequired <= 0:
            flash('Places to book must be a positive integer.')
            return render_template('welcome.html', club=club, competitions=competitions)

        # 2. Competition/Places availability
        available_places = int(competition['numberOfPlaces'])
        if available_places == 0:
            flash('This competition is full.')
            return render_template('welcome.html', club=club, competitions=competitions)
        if placesRequired > available_places:
            flash("This competition does not have this amount available.")
            return render_template('welcome.html', club=club, competitions=competitions)

        # 3. Booking limit validation
        booking_tracker = session['booking_tracker']
        current_booking = next((b for b in booking_tracker if b['name'] == competition['name']), None)
        if not current_booking:
            current_booking = {"name": competition['name'], "alreadyBooked": "0"}
            booking_tracker.append(current_booking)
        total_booked = int(current_booking['alreadyBooked']) + placesRequired
        if total_booked > maxPlaces:
            flash(f"Clubs are limited to {maxPlaces} places for one competition.")
            return render_template('welcome.html', club=club, competitions=competitions)

        # 4. Points validation
        points_needed = placesRequired * placeCost
        if points_needed > int(club['points']):
            flash('Not enough points!')
            return render_template('welcome.html', club=club, competitions=competitions)

        # Everything validated, update values
        competition['numberOfPlaces'] = str(available_places - placesRequired)
        club['points'] = str(int(club['points']) - points_needed)
        current_booking['alreadyBooked'] = str(total_booked)
        session['booking_tracker'] = booking_tracker
        
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)
        
    except ValueError:
        flash('Invalid number of places!')
        return render_template('welcome.html', club=club, competitions=competitions)
    except Exception as e:
        app.logger.error(f"Error in purchasePlaces: {str(e)}")
        flash('An unexpected error occurred. Please try again.')
        return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
