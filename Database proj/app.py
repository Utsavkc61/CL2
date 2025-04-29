from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password="root",  
    database="champions_league"
)
cursor = db.cursor(dictionary=True)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/groups")
def groups():
    return render_template('group.html')

@app.route("/players")
def players():
    return render_template('player.html')

@app.route("/matches")
def matches():
    return render_template('matches.html')

@app.route("/api/players")
def get_players():
    query = """
        SELECT p.name, t.name AS team, p.position, 
               SUM(ps.goals) AS goals, SUM(ps.assists) AS assists
        FROM Player p
        JOIN Team t ON p.team_id = t.team_id
        LEFT JOIN PlayerMatchStats ps ON p.player_id = ps.player_id
        GROUP BY p.player_id
    """
    cursor.execute(query)
    players = cursor.fetchall()
    return jsonify(players)

@app.route("/api/matches")
def get_matches():
    query = """
        SELECT 
            m.match_id,
            m.date AS match_date,
            GROUP_CONCAT(CASE WHEN mt.is_home THEN t.name ELSE NULL END) AS home_team,
            GROUP_CONCAT(CASE WHEN NOT mt.is_home THEN t.name ELSE NULL END) AS away_team
        FROM Matches m
        JOIN MatchTeam mt ON m.match_id = mt.match_id
        JOIN Team t ON mt.team_id = t.team_id
        GROUP BY m.match_id
        ORDER BY m.date
    """
    cursor.execute(query)
    matches = cursor.fetchall()
    return jsonify(matches)

@app.route("/api/standings/<group_name>")
def get_standings(group_name):
    query = """
        SELECT t.name AS team_name, s.wins, s.loss, s.draw, 
               s.points, s.goal_difference
        FROM Standings s
        JOIN Team t ON s.team_id = t.team_id
        JOIN GroupTable g ON s.group_id = g.group_id
        WHERE g.name = %s
        ORDER BY s.points DESC, s.goal_difference DESC
    """
    cursor.execute(query, (group_name,))
    standings = cursor.fetchall()
    return jsonify(standings)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
