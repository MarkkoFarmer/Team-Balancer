from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Paths
DATA_FILE = 'players.json'

# Load or initialize JSON file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"players": {}, "goalkeepers": {}}, f)


def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    players = list(data["players"].keys())
    goalkeepers = list(data["goalkeepers"].keys())
    team1 = team2 = []

    if request.method == 'POST':
        names = request.form.getlist("player_name")
        skills = request.form.getlist("player_skill")

        gk_names = request.form.getlist("gk_name")
        gk_skills = request.form.getlist("gk_skill")

        all_players = []
        for name, skill in zip(names, skills):
            if name and skill:
                all_players.append((name, int(skill)))

        for name, skill in zip(gk_names, gk_skills):
            if name and skill:
                all_players.append((name + " (GK)", int(skill)))

        if len(all_players) != 22:
            return "Please select exactly 20 players and 2 goalkeepers"

        all_players.sort(key=lambda x: x[1], reverse=True)
        team1 = all_players[::2]
        team2 = all_players[1::2]

    return render_template("index.html", players=players, goalkeepers=goalkeepers,
                           team1=team1, team2=team2)


@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        data = load_data()
        for i in range(20):
            name = request.form.get(f'player_name_{i}')
            skill = request.form.get(f'player_skill_{i}')
            if name and skill:
                data['players'][name] = int(skill)
        save_data(data)
        return redirect(url_for('index'))
    return render_template('add_player.html')


@app.route('/add_goalkeeper', methods=['GET', 'POST'])
def add_goalkeeper():
    if request.method == 'POST':
        data = load_data()
        for i in range(2):
            name = request.form.get(f'gk_name_{i}')
            skill = request.form.get(f'gk_skill_{i}')
            if name and skill:
                data['goalkeepers'][name] = int(skill)
        save_data(data)
        return redirect(url_for('index'))
    return render_template('add_goalkeeper.html')


@app.route('/remove_player', methods=['POST'])
def remove_player():
    name = request.form['player_name']
    data = load_data()

    if name in data['players']:
        del data['players'][name]
    elif name in data['goalkeepers']:
        del data['goalkeepers'][name]
    elif name.endswith(" (GK)"):
        raw_name = name.replace(" (GK)", "")
        data['goalkeepers'].pop(raw_name, None)

    save_data(data)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
