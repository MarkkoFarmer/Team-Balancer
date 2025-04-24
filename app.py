import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Nastavení aplikace
app = Flask(__name__)

# Připojení k PostgreSQL databázi (tuto URL nastavíš na Renderu)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Nastavení pro Render
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model pro hráče
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Player {self.name}>'

# Model pro brankáře
class Goalkeeper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Goalkeeper {self.name}>'

# Funkce pro vytvoření tabulek v databázi při startu aplikace
@app.before_first_request
def create_tables():
    db.create_all()

# Route pro indexovou stránku
@app.route('/', methods=['GET', 'POST'])
def index():
    players = Player.query.all()  # Získáme všechny hráče z databáze
    goalkeepers = Goalkeeper.query.all()  # Získáme všechny brankáře z databáze

    if request.method == 'POST':
        selected_players = request.form.getlist('selected_players')  # Seznam vybraných hráčů
        selected_goalkeepers = request.form.getlist('selected_goalkeepers')  # Seznam vybraných brankářů

        team1 = []
        team2 = []

        # Generování týmů
        for player in players:
            if player.name in selected_players:
                if len(team1) < len(selected_players) // 2:
                    team1.append((player.name, player.skill))
                else:
                    team2.append((player.name, player.skill))

        for goalkeeper in goalkeepers:
            if goalkeeper.name in selected_goalkeepers:
                if len(team1) < len(selected_goalkeepers) // 2:
                    team1.append((goalkeeper.name, goalkeeper.skill))
                else:
                    team2.append((goalkeeper.name, goalkeeper.skill))

        return render_template('index.html', players=players, goalkeepers=goalkeepers, team1=team1, team2=team2)

    return render_template('index.html', players=players, goalkeepers=goalkeepers)

# Route pro přidání nového hráče nebo brankáře
@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        skill = float(request.form['skill'])
        role = request.form['role']

        if role == 'goalkeeper':
            new_goalkeeper = Goalkeeper(name=name, skill=skill)
            db.session.add(new_goalkeeper)
        else:
            new_player = Player(name=name, skill=skill)
            db.session.add(new_player)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_player.html')

# Route pro smazání hráče nebo brankáře
@app.route('/delete_player/<int:id>')
def delete_player(id):
    player = Player.query.get_or_404(id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_goalkeeper/<int:id>')
def delete_goalkeeper(id):
    goalkeeper = Goalkeeper.query.get_or_404(id)
    db.session.delete(goalkeeper)
    db.session.commit()
    return redirect(url_for('index'))

# Spuštění aplikace
if __name__ == '__main__':
    app.run(debug=True)
