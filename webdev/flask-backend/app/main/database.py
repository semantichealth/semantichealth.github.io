from flask import current_app, g
import psycopg2

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(**current_app.config['PG_CONFIG'])
    return db

def log_query(session_id, state, age, zipcode, health):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO Queries (session_id, state, age, zipcode, health) VALUES (%s, %s, %s, %s, %s)", (session_id, state, age, zipcode, health))
    conn.commit()
    cur.close()

def log_click(session_id, plan_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO Clicks (session_id, plan_id) VALUES (%s, %s)", (session_id, plan_id))
    conn.commit()
    cur.close()

def log_ranks(session_id, plan_id, plan_score):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO Ranks (session_id, plan_id, plan_score) VALUES (%s, %s, %s)", (session_id, plan_id, plan_score))
    conn.commit()
    cur.close()
