from flask import Flask, render_template, request, redirect, url_for
import json
import random
import os

app = Flask(__name__)

DATA_FILE = 'players.json'

# Načítání a ukládání hráčů do souboru
def load_players():
    if not os.path.exists(DATA_FILE):
        return {"players": {}, "goalkeepers": {}}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading players data: {e}")
        return {"players": {}, "goalkeepers": {}}

def save_players(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving players data: {e}")

# Funkce pro vyvážení týmů
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
    try:
        data = load_players()
        players = data["players"]
        goalkeepers = data["goalkeepers"]
    except Exception as e:
        print(f"Error in index route: {e}")
        players = goalkeepers = {}

    if request.method == "POST":
        try:
            # Přidání nových hráčů
            if "new_player_name" in request.form:
                new_players = dict(zip(request.form.getlist("new_player_name"), map(int, request.form.getlist("new_player_skill"))))
                players.update(new_players)
                save_players({"players": players, "goalkeepers": goalkeepers})

            # Přidání nových brankářů
            if "gk_name" in request.form:
                new_goalies = dict(zip(request.form.getlist("gk_name"), map(int, request.form.getlist("gk_skill"))))
                goalkeepers.update(new_goalies)
                save_players({"players": players, "goalkeepers": goalkeepers})

            # Výběr hráčů pro týmy
            selected_players = request.form.getlist("selected_players")

            if len(selected_players) != 20:
                return "Please select exactly 20 players", 400

            selected_players_dict = {player: players[player] for player in selected_players}
            team1, team2 = balance_teams(selected_players_dict, goalkeepers)

            return render_template("index.html", team1=team1, team2=team2, players=players, goalkeepers=goalkeepers)
        except Exception as e:
            print(f"Error processing form data: {e}")
            return "Error processing the form data", 500

    return render_template("index.html", team1=[], team2=[], players=players, goalkeepers=goalkeepers)

@app.route("/add_player", methods=["GET", "POST"])
def add_player():
    try:
        data = load_players()
        players = data["players"]
        goalkeepers = data["goalkeepers"]
    except Exception as e:
        print(f"Error in add_player route: {e}")
        players = goalkeepers = {}

    if request.method == "POST":
        try:
            player_name = request.form["player_name"]
            player_skill = int(request.form["player_skill"])
            players[player_name] = player_skill
            save_players({"players": players, "goalkeepers": goalkeepers})
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Error adding player: {e}")
            return "Error adding the player", 500

    return render_template("add_player.html", players=players)

@app.route("/remove_player", methods=["POST"])
def remove_player():
    try:
        data = load_players()
        players = data["players"]
        goalkeepers = data["goalkeepers"]

        player_name = request.form["player_name"]
        if player_name in players:
            del players[player_name]
            save_players({"players": players, "goalkeepers": goalkeepers})

        return redirect(url_for("index"))
    except Exception as e:
        print(f"Error removing player: {e}")
        return "Error removing the player", 500

if __name__ == "__main__":
    app.run(debug=True)
