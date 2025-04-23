from flask import Flask, render_template, request, redirect
import json
import random
import os

app = Flask(__name__)

DATA_FILE = 'players.json'


def load_players():
    if not os.path.exists(DATA_FILE):
        return {"players": {}, "goalkeepers": {}}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_players(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


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

    # pick goalies
    gk = list(goalkeepers.items())
    random.shuffle(gk)
    team1.append(("Goalkeeper: " + gk[0][0], gk[0][1]))
    team2.append(("Goalkeeper: " + gk[1][0], gk[1][1]))

    return team1, team2


@app.route("/", methods=["GET", "POST"])
def index():
    data = load_players()
    players = data["players"]
    goalkeepers = data["goalkeepers"]

    if request.method == "POST":
        new_players = dict(zip(request.form.getlist("player_name"), map(int, request.form.getlist("player_skill"))))
        new_goalies = dict(zip(request.form.getlist("gk_name"), map(int, request.form.getlist("gk_skill"))))

        # update JSON
        players.update(new_players)
        goalkeepers.update(new_goalies)
        save_players({"players": players, "goalkeepers": goalkeepers})

        team1, team2 = balance_teams(new_players, new_goalies)
        return render_template("index.html", team1=team1, team2=team2, players=players, goalkeepers=goalkeepers)

    return render_template("index.html", team1=[], team2=[], players=players, goalkeepers=goalkeepers)


if __name__ == "__main__":
    app.run(debug=True)
