from flask import Flask, render_template, request, redirect, url_for
import json
import random
import os

app = Flask(__name__)

DATA_FILE = 'players.json'


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"players": {}, "goalkeepers": {}}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading players data: {e}")
        return {"players": {}, "goalkeepers": {}}


def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving players data: {e}")


def balance_teams(players, goalkeepers):
    all_players = list(players.items())
    random.shuffle(all_players)
    team1, team2 = [], []
    skill1, skill2 = 0, 0

    for name, skill in all_players:
        if len(team1) < 9 and (skill1 <= skill2 or len(team2) >= 9):
            team1.append((name, skill))
            skill1 += skill
        else:
            team2.append((name, skill))
            skill2 += skill

    gk = list(goalkeepers.items())
    random.shuffle(gk)
    team1.append(("Goalkeeper: " + gk[0][0], gk[0][1]))
    team2.append(("Goalkeeper: " + gk[1][0], gk[1][1]))

    return team1, team2


@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()
    players = data["players"]
    goalkeepers = data["goalkeepers"]

    if request.method == "POST":
        try:
            # Přidání více hráčů a brankářů
            new_players = dict(zip(request.form.getlist("player_name"), map(int, request.form.getlist("player_skill"))))
            new_goalkeepers = dict(zip(request.form.getlist("gk_name"), map(int, request.form.getlist("gk_skill"))))

            players.update(new_players)
            goalkeepers.update(new_goalkeepers)

            save_data({"players": players, "goalkeepers": goalkeepers})

            team1, team2 = balance_teams(players, goalkeepers)

            return render_template("index.html", team1=team1, team2=team2, players=players, goalkeepers=goalkeepers)

        except Exception as e:
            print(f"Error processing form data: {e}")
            return "Error processing the form data", 500

    return render_template("index.html", team1=[], team2=[], players=players, goalkeepers=goalkeepers)


@app.route("/remove_player", methods=["POST"])
def remove_player():
    data = load_data()
    players = data["players"]
    goalkeepers = data["goalkeepers"]

    player_name = request.form["player_name"]
    if player_name in players:
        del players[player_name]
        save_data({"players": players, "goalkeepers": goalkeepers})

    return redirect(url_for("index"))


@app.route("/remove_goalkeeper", methods=["POST"])
def remove_goalkeeper():
    data = load_data()
    players = data["players"]
    goalkeepers = data["goalkeepers"]

    gk_name = request.form["gk_name"]
    if gk_name in goalkeepers:
        del goalkeepers[gk_name]
        save_data({"players": players, "goalkeepers": goalkeepers})

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
