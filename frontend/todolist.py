import os
import psycopg2
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__,template_folder='../templates')

if not os.path.exists("../logs"):
    os.mkdir("../logs")

file_handler = RotatingFileHandler('../logs/app.log', maxBytes=10240, backupCount=2)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))

file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Todolist app startup....')

DB_HOST     = os.environ.get('DB_HOST', 'localhost')
DB_NAME     = os.environ.get('DB_NAME', 'todolist')
DB_USER     = os.environ.get('DB_USER', 'postgres')
DB_PASS     = os.environ.get('DB_PASS','password')


def get_db_connection():
    try:
        conn =  psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        app.logger.error(f"DB connection error: {e}")
        return None

#Tao route cho app
@app.route('/', methods=['GET','POST'])
def index():
    conn = get_db_connection()
    error = None
    tasks = []
    #1. Xu ly POST
    if request.method == 'POST':
        content = request.form.get('content')
        if content and conn:
            try:
                cur = conn.cursor()
                cur.execute('INSERT INTO tasks (content) VALUES (%s)', (content,))
                conn.commit()
                cur.close ()
                app.logger.info(f"Task added successfully: {content}")
            except Exception as e:
                app.logger.error(f"Failed to add task: {e}")
                error = str(e)
    
    #2. Xy ly GET
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM tasks ORDER BY id DESC;')
            tasks = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            app.logger.error(f"Fetch tasks errors: {e}")
            error = str(e)
    else:
        error = "Could not connect database!"
        app.logger.critical("Database connection is DOWN !")

    return render_template('index.html', tasks=tasks, error=error, hostname=os.environ.get('HOSTNAME', 'local'))

@app.route('/init', methods=['POST'])
def init_db():
    conn = get_db_connection()
    if not conn: return "DB error", 500
    try:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS tasks (id serial PRIMARY KEY, content varchar(255));')
        conn.commit()
        cur.close()
        conn.close()
        app.logger.info("Database initialized successfully")
        return "Init Success"
    except Exception as e:
        app.logger.error(f"Init DB failed: {e}")
        return f"Error: {e}", 500

if __name__=="__main__":
    app.run(host='0.0.0.0', port=3007)