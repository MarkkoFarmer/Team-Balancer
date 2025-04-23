from flask import Flask, render_template, request, send_file
import random
import io
from itertools import combinations

app = Flask(__name__)

def find_best_teams(players, goalkeepers):
    best_diff = float('inf')
    best_team1 = []
    best_team2 = []
    best_gk1 = None
    best_gk2 = None

    field_combinations = list(combinations(players, 10))
    random.shuffle(field_combinations)

    for team1 in field_combinations[:1000]:
        team2 = [p for p in players if p not in team1]
        team1_skill = sum(p['skill'] for p in team1)
        team2_skill = sum(p['skill'] for p in team2)

        for gk1, gk2 in [(goalkeepers[0], goalkeepers[1]), (goalkeepers[1], goalkeepers[0])]:
            total1 = team1_skill + gk1['skill']
            total2 = team2_skill + gk2['skill']
            diff = abs(total1 - total2)

            if diff < best_diff:
                best_diff = diff
                best_team1 = team1
                best_team2 = team2
                best_gk1 = gk1
                best_gk2 = gk2

    return (best_team1, best_gk1, best_team2, best_gk2, best_diff)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        players = []
        goalkeepers = []

        try:
            for i in range(20):
                name = request.form[f'name_{i}'].strip()
                skill = int(request.form[f'skill_{i}'])
                players.append({'name': name, 'skill': skill})

            for i in range(2):
                name = request.form[f'gk_name_{i}'].strip()
                skill = int(request.form[f'gk_skill_{i}'])
                goalkeepers.append({'name': name, 'skill': skill})

            best_team = find_best_teams(players, goalkeepers)
            result = {
                'team1': best_team[0],
                'gk1': best_team[1],
                'team2': best_team[2],
                'gk2': best_team[3],
                'diff': best_team[4]
            }
        except Exception as e:
            result = {'error': str(e)}

    return render_template('index.html', result=result)

@app.route('/download', methods=['POST'])
def download():
    team_data = request.form['export_data']
    file_stream = io.BytesIO()
    file_stream.write(team_data.encode('utf-8'))
    file_stream.seek(0)
    return send_file(file_stream, as_attachment=True, download_name="sestava.txt")

if __name__ == '__main__':
    app.run(debug=True)
