from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

data_file = 'data.json'

app = Flask(__name__)


def load_data():
    if not os.path.exists(data_file):
        return {"players": {}, "goalkeepers": {}}
    with open(data_file, 'r') as f:
        return json.load(f)


def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    players_data = data["players"]
    goalkeepers_data = data["goalkeepers"]

    selected_players = request.form.getlist("player_name")
    selected_skills = request.form.getlist("player_skill")
    selected_gks = request.form.getlist("gk_name")
    selected_gk_skills = request.form.getlist("gk_skill")

    team1, team2 = [], []
    error = None

    if request.method == "POST":
        if len(selected_players) != 20 or len(selected_gks) != 2:
            error = "Please select exactly 20 players and 2 goalkeepers."
        else:
            players_combined = list(zip(selected_players, map(float, selected_skills)))
            gks_combined = list(zip(selected_gks, map(float, selected_gk_skills)))

            players_combined.sort(key=lambda x: x[1], reverse=True)
            team1 = players_combined[::2]
            team2 = players_combined[1::2]

            gk1 = gks_combined[0]
            gk2 = gks_combined[1]

            team1.insert(0, gk1)
            team2.insert(0, gk2)

    return render_template("index.html", players=players_data, goalkeepers=goalkeepers_data,
                           team1=team1, team2=team2, error=error,
                           selected_players=selected_players, selected_skills=selected_skills,
                           selected_gks=selected_gks, selected_gk_skills=selected_gk_skills)


@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    data = load_data()
    if request.method == 'POST':
        for i in range(20):
            name = request.form.get(f'name_{i}')
            skill = request.form.get(f'skill_{i}')
            if name and skill:
                try:
                    data['players'][name] = round(float(skill.replace(',', '.')), 2)
                except ValueError:
                    continue
        save_data(data)
        return redirect(url_for('index'))
    return render_template('add_player.html')


@app.route('/add_goalkeeper', methods=['GET', 'POST'])
def add_goalkeeper():
    data = load_data()
    if request.method == 'POST':
        for i in range(2):
            name = request.form.get(f'name_{i}')
            skill = request.form.get(f'skill_{i}')
            if name and skill:
                try:
                    data['goalkeepers'][name] = round(float(skill.replace(',', '.')), 2)
                except ValueError:
                    continue
        save_data(data)
        return redirect(url_for('index'))
    return render_template('add_goalkeeper.html')


@app.route('/remove_player', methods=['POST'])
def remove_player():
    name = request.form.get("player_name")
    data = load_data()
    data['players'].pop(name, None)
    save_data(data)
    return redirect(url_for('index'))


@app.route('/remove_goalkeeper', methods=['POST'])
def remove_goalkeeper():
    name = request.form.get("gk_name")
    data = load_data()
    data['goalkeepers'].pop(name, None)
    save_data(data)
    return redirect(url_for('index'))


@app.route('/get_skill/<player_type>/<name>')
def get_skill(player_type, name):
    data = load_data()
    skill = data[player_type].get(name, "")
    return jsonify({"skill": skill})


if __name__ == '__main__':
    app.run(debug=True)
