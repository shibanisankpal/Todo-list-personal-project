import streamlit as st
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('todo.db', check_same_thread=False)
cursor = conn.cursor()

# Create tasks table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT DEFAULT 'Pending',
    due_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Function to add a task
def add_task(title, description, category, due_date):
    cursor.execute('''
        INSERT INTO tasks (title, description, category, due_date)
        VALUES (?, ?, ?, ?)
    ''', (title, description, category, due_date))
    conn.commit()

# Function to get tasks
def get_tasks(filter_date=None):
    if filter_date:
        cursor.execute('''
            SELECT * FROM tasks WHERE due_date = ? ORDER BY created_at
        ''', (filter_date,))
    else:
        cursor.execute('''
            SELECT * FROM tasks ORDER BY due_date ASC, created_at DESC
        ''')
    return cursor.fetchall()

# Function to update task status
def update_task_status(task_id, new_status):
    cursor.execute('''
        UPDATE tasks SET status = ? WHERE id = ?
    ''', (new_status, task_id))
    conn.commit()

# Function to delete a task
def delete_task(task_id):
    cursor.execute('''
        DELETE FROM tasks WHERE id = ?
    ''', (task_id,))
    conn.commit()

# Streamlit app
st.title("📋 To-Do List App")

# Task creation form
with st.form("Add Task"):
    title = st.text_input("Task Title")
    description = st.text_area("Description")
    category = st.selectbox("Category", ["Work", "Personal", "Shopping", "Others"])
    due_date = st.date_input("Due Date")
    submitted = st.form_submit_button("Add Task")
    if submitted:
        if title.strip():
            add_task(title, description, category, due_date)
            st.success("Task added successfully!")
            st.experimental_rerun()
        else:
            st.error("Task title cannot be empty.")

# Task filtering
st.sidebar.header("🔍 Filter Tasks")
filter_date = st.sidebar.date_input("Filter by Due Date (optional)", value=None)
tasks = get_tasks(filter_date.strftime('%Y-%m-%d') if filter_date else None)

# Display tasks
st.subheader("Your Tasks")
if tasks:
    for task in tasks:
        with st.container():
            cols = st.columns([3, 1, 1, 1])
            task_title = f"**{task[1]}**" + (f" ({task[3]})" if task[3] else "")
            cols[0].markdown(task_title)
            cols[0].markdown(f"🗒️ {task[2]}" if task[2] else "")
            cols[0].markdown(f"📅 Due: {task[5]}")
            cols[0].markdown(f"🟢 Status: {task[4]}")

            if task[4] == "Pending":
                if cols[1].button("✅ Complete", key=f"complete_{task[0]}"):
                    update_task_status(task[0], "Completed")
                    st.experimental_rerun()
            else:
                cols[1].write("✔️ Completed")

            if cols[2].button("🗑️ Delete", key=f"delete_{task[0]}"):
                delete_task(task[0])
                st.experimental_rerun()
else:
    st.info("No tasks found. Add a new task to get started!")

# Footer
st.write("Built with ❤️ using Streamlit")
