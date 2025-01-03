import json
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()
placeCost = 1  # point(s)


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
        # Look for club & competition data
        competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
        club = next((c for c in clubs if c['name'] == request.form['club']), None)
        
        if not competition or not club:
            flash('Competition or club not found!')
            return redirect(url_for('index'))

        # Converting to int
        placesRequired = int(request.form['places'])
        points_needed = placesRequired * placeCost
        club_points = int(club['points'])
        
        # Update club points
        club['points'] = str(club_points - points_needed)
        
        flash('Great, booking complete!')
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
