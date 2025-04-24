from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

DATA_FILE = "players.json"

players = {}
goalkeepers = {}
selected_players = []
selected_goalkeepers = []

# === 🔄 Funkce pro uložení a načtení dat ===
def load_data():
    global players, goalkeepers
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            players = data.get("players", {})
            goalkeepers = data.get("goalkeepers", {})

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "players": players,
            "goalkeepers": goalkeepers
        }, f, indent=2)

# === 🔧 Parsování skillu ===
def parse_skill(value):
    value = value.replace(",", ".")
    try:
        return round(float(value), 2)
    except ValueError:
        return None

@app.route("/")
def index():
    return render_template("index.html", players=players, goalkeepers=goalkeepers,
                           selected_players=selected_players, selected_goalkeepers=selected_goalkeepers)

@app.route("/add_player", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        name = request.form["name"].strip()
        skill = parse_skill(request.form["skill"])
        role = request.form["role"]

        if name and skill is not None:
            if role == "goalkeeper":
                goalkeepers[name] = skill
            else:
                players[name] = skill
            save_data()
        return redirect(url_for("add_player"))

    return render_template("add_player.html")

@app.route("/delete/<role>/<name>", methods=["POST"])
def delete_player(role, name):
    if role == "player" and name in players:
        del players[name]
    elif role == "goalkeeper" and name in goalkeepers:
        del goalkeepers[name]
    save_data()
    return redirect(url_for("index"))

@app.route("/generate_teams", methods=["POST"])
def generate_teams():
    global selected_players, selected_goalkeepers

    selected_players = request.form.getlist("selected_players")
    selected_goalkeepers = request.form.getlist("selected_goalkeepers")

    team1 = []
    team2 = []

    if len(selected_players) >= 2 and len(selected_goalkeepers) == 2:
        sorted_players = sorted([(p, players[p]) for p in selected_players], key=lambda x: x[1], reverse=True)

        for i, p in enumerate(sorted_players):
            (team1 if i % 2 == 0 else team2).append(p)

        team1.insert(0, (selected_goalkeepers[0], goalkeepers[selected_goalkeepers[0]]))
        team2.insert(0, (selected_goalkeepers[1], goalkeepers[selected_goalkeepers[1]]))

    return render_template("index.html", players=players, goalkeepers=goalkeepers,
                           selected_players=selected_players, selected_goalkeepers=selected_goalkeepers,
                           team1=team1, team2=team2)

if __name__ == "__main__":
    load_data()
    app.run(debug=True)
