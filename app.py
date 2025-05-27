from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
from datetime import datetime
import os
from todo_parser import parse_todo_with_deadline
from memory_manager import add_memory, search_memory
from llm_local import run_local_llm

app = Flask(__name__)

# ==== DEV MODE RESET ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dev_mode = True
if dev_mode:
    for db_name in ['chat_history.db', 'todo_list.db']:
        db_path = os.path.join(BASE_DIR, db_name)
        if os.path.exists(db_path):
            os.remove(db_path)


# ==== DB INITIALIZATION ====
def init_dbs():
    with sqlite3.connect('chat_history.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL
            )
        ''')

    with sqlite3.connect('todo_list.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                priority TEXT DEFAULT 'Low',
                completed BOOLEAN NOT NULL DEFAULT 0
            )
        ''')

init_dbs()

# ==== DB HELPERS ====
def insert_chat(user_message, bot_response):
    with sqlite3.connect('chat_history.db') as conn:
        conn.execute(
            'INSERT INTO chats (user_message, bot_response) VALUES (?, ?)',
            (user_message, bot_response)
        )

def get_chat_history():
    with sqlite3.connect('chat_history.db') as conn:
        return conn.execute(
            'SELECT timestamp, user_message, bot_response FROM chats ORDER BY id ASC'
        ).fetchall()

def get_tasks():
    with sqlite3.connect('todo_list.db') as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()

def add_task(task, description=None, deadline=None, priority="Low"):
    with sqlite3.connect('todo_list.db') as conn:
        conn.execute(
            'INSERT INTO tasks (task, description, deadline, priority, completed) VALUES (?, ?, ?, ?, ?)',
            (task, description, deadline, priority, False)
        )

def update_task(task_id, completed):
    with sqlite3.connect('todo_list.db') as conn:
        conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))

def delete_task(task_id):
    with sqlite3.connect('todo_list.db') as conn:
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

# ==== Prompt formatter for Phi-3 Mini ====
def format_phi3_prompt(user_input: str) -> str:
    return f"<|user|>\n{user_input}\n<|assistant|>\n"

# ==== ROUTES ====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html', history=get_chat_history())

    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # === Remember command ===
    if user_message.lower().startswith("remember"):
        memory_content = user_message[len("remember"):].strip()
        if memory_content:
            add_memory(memory_content)
            bot_response = "Got it. I'll remember that."
            insert_chat(user_message, bot_response)
            return jsonify({'response': bot_response})

    # === To-do parser ===
    parsed = parse_todo_with_deadline(user_message)
    if parsed.get("is_todo"):
        task_name = parsed.get("task_name", user_message)
        deadline_dt = parsed.get("deadline")
        deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M") if deadline_dt else None
        add_task(task_name, deadline=deadline_str)
        bot_response = f"📝 Task '{task_name}' added to your to-do list!"
        insert_chat(user_message, bot_response)
        return jsonify({'response': bot_response})

    # === Memory-based response ===
    memory_hits = search_memory(user_message)
    if memory_hits:
        memory_context = memory_hits[-1]
        raw_prompt = (
            f"The user previously told you:\n\"\"\"{memory_context}\"\"\"\n\n"
            f"Now they asked:\n\"{user_message}\"\n\n"
            "If their question relates to the previous information, use it to answer. "
            "Otherwise, answer normally. Always explain clearly and helpfully."
        )
        prompt = format_phi3_prompt(raw_prompt)
        bot_response = run_local_llm(prompt)
        insert_chat(user_message, bot_response)
        return jsonify({'response': bot_response})

    # === Default LLM chat ===
    try:
        prompt = format_phi3_prompt(user_message)
        bot_response = run_local_llm(prompt)
        insert_chat(user_message, bot_response)
        return jsonify({'response': bot_response})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        task = request.form.get('title')
        description = request.form.get('description')
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Low')
        if task:
            add_task(task, description, deadline, priority)
        return redirect('/todo')
    return render_template('todotrial.html', tasks=get_tasks())

@app.route('/todo/update/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    completed = request.form.get('completed') == 'on'
    update_task(task_id, completed)
    return redirect('/todo')

@app.route('/todo/delete/<int:task_id>', methods=['POST'])
def remove_task(task_id):
    delete_task(task_id)
    return redirect('/todo')

@app.route('/todo/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = request.form.get('task')
    description = request.form.get('description')
    date = request.form.get('deadline_date')
    time = request.form.get('deadline_time')
    deadline = f"{date} {time}" if date and time else None
    priority = request.form.get('priority')
    with sqlite3.connect('todo_list.db') as conn:
        conn.execute(
            'UPDATE tasks SET task = ?, description = ?, deadline = ?, priority = ? WHERE id = ?',
            (task, description, deadline, priority, task_id)
        )
    return redirect('/todo')

@app.route('/calendar')
def calendar():
    with sqlite3.connect('todo_list.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            'SELECT id, task, deadline FROM tasks WHERE deadline IS NOT NULL'
        ).fetchall()

    events = []
    for row in rows:
        try:
            dt = datetime.strptime(row['deadline'], "%Y-%m-%d %H:%M")
            events.append({'title': row['task'], 'start': dt.isoformat(), 'allDay': False})
        except ValueError:
            continue
    return render_template('calendar.html', calendar_events=events)

# ==== RUN APP ====
if __name__ == '__main__':
    import threading
    import webview

    # Start the Flask app in a separate thread
    def run_flask():
        app.run(debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Create desktop GUI window
    webview.create_window("AronaOS", "http://127.0.0.1:5000")
    webview.start()
