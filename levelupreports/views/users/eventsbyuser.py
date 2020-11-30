"""Module for generating games by user report"""
import sqlite3
from django.shortcuts import render
from levelupapi.models import Event
from levelupreports.views import Connection

def userevent_list(request):
    """Function to build an HTML report of games by user"""
    if request.method == 'GET':
        # Connect to project database
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # Query for all games, with related user info
            db_cursor.execute("""
                SELECT
                    e.id,
                    e.creator_id,
                    e.date,
                    e.time,
                    e.location,
                    game.name AS game_name,
                    u.first_name || ' ' || u.last_name AS full_name,
                    u.id AS user_id
                FROM
                    levelupapi_event e
                JOIN
                    levelupapi_game game ON e.game_id = game.id
                JOIN
                    levelupapi_eventgamer eg ON e.id = eg.event_id
                JOIN
                    levelupapi_gamer g ON eg.gamer_id = g.id
                JOIN
                    auth_user u ON g.user_id = u.id
            """)

            dataset = db_cursor.fetchall()

            events_by_user = {}

            for row in dataset:
                event = Event()
                event.id = row['id']
                event.date = row['date']
                event.time = row['time']
                event.location = row['location']
                event.creator_id = row['creator_id']
                event.game_name = row['game_name']

                uid = row['user_id']

                if uid in events_by_user:
                    events_by_user[uid]['events'].append(event)
                else:
                    events_by_user[uid] = {
                        "organizer_id": event.creator_id,
                        "full_name": row['full_name'],
                        "events": [ event ]
                    }

            user_events_list = events_by_user.values()

            template = "users/list_with_events.html"
            context = {
                "user_events": user_events_list
            }

            return render(request, template, context)
