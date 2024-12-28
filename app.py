import streamlit as st
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('todo.db')
cursor = conn.cursor()

# Create tasks table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'Pending',
    due_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Function to add a task
def add_task(title, description, due_date):
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date)
        VALUES (?, ?, ?)
    ''', (title, description, due_date))
    conn.commit()

# Function to get tasks
def get_tasks(filter_date=None):
    if filter_date:
        cursor.execute('''
            SELECT * FROM tasks WHERE due_date = ? ORDER BY created_at
        ''', (filter_date,))
    else:
        cursor.execute('''
            SELECT * FROM tasks ORDER BY created_at
        ''')
    return cursor.fetchall()

# Function to mark task as completed
def mark_completed(task_id):
    cursor.execute('''
        UPDATE tasks SET status = 'Completed' WHERE id = ?
    ''', (task_id,))
    conn.commit()

# Streamlit app
st.title("To-Do List App")

# Add a task
with st.form("Add Task"):
    title = st.text_input("Task Title")
    description = st.text_area("Description", "")
    due_date = st.date_input("Due Date")
    submitted = st.form_submit_button("Add Task")
    if submitted:
        add_task(title, description, due_date)
        st.success("Task added!")

# Filter tasks
filter_date = st.date_input("Filter by Due Date (optional)", value=None)
tasks = get_tasks(filter_date.strftime('%Y-%m-%d') if filter_date else None)

# Display tasks
for task in tasks:
    st.write(f"**{task[1]}**")
    st.write(f"Description: {task[2]}")
    st.write(f"Due Date: {task[4]}")
    st.write(f"Status: {task[3]}")
    if st.button(f"Mark Completed {task[0]}"):
        mark_completed(task[0])
        st.experimental_rerun()
