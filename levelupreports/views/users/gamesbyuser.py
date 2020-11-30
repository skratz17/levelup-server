"""Module for generating games by user report"""
import sqlite3
from django.shortcuts import render
from levelupapi.models import Game
from levelupreports.views import Connection

def usergame_list(request):
    """Function to build an HTML report of games by user"""
    if request.method == 'GET':
        # Connect to project database
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # Query for all games, with related user info
            db_cursor.execute("""
                SELECT
                    g.id,
                    g.name,
                    g.game_type_id,
                    g.num_players,
                    g.skill_level,
                    u.id user_id,
                    u.first_name || ' ' || u.last_name AS full_name
                FROM
                    levelupapi_game g
                JOIN
                    levelupapi_gamer gr ON g.creator_id = gr.id
                JOIN
                    auth_user u ON gr.user_id = u.id
            """)

            dataset = db_cursor.fetchall()

            games_by_user = {}

            for row in dataset:
                game = Game()
                game.name = row['name']
                game.game_type_id = row['game_type_id']
                game.num_players = row['num_players']
                game.skill_level = row['skill_level']

                uid = row['user_id']

                # If we've already encountered this user, add this game to their list of games
                if uid in games_by_user:
                    games_by_user[uid]['games'].append(game)

                # Otherwise add a new key-value pair for this user
                else:
                    games_by_user[uid] = {
                        "id": uid,
                        "full_name": row["full_name"],
                        "games": [ game ]
                    }
            
            # dict.values() is akin to Object.values(obj) in JS
            list_of_users_with_games = games_by_user.values()

            # Specify Django template and provide data context
            template = 'users/list_with_games.html'
            context = {
                'usergame_list': list_of_users_with_games
            }

            return render(request, template, context)
