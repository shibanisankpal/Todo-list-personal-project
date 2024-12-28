import streamlit as st
import sqlite3
from datetime import datetime, timedelta

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
    conn = sqlite3.connect('todo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, description, category, due_date)
        VALUES (?, ?, ?, ?)
    ''', (title, description, category, due_date.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

# Function to get tasks for a date range
def get_tasks_by_date_range(start_date, end_date):
    conn = sqlite3.connect('todo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tasks
        WHERE due_date BETWEEN ? AND ?
        ORDER BY due_date ASC, created_at DESC
    ''', (start_date, end_date))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# Function to update task status
def update_task_status(task_id, new_status):
    conn = sqlite3.connect('todo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks SET status = ? WHERE id = ?
    ''', (new_status, task_id))
    conn.commit()
    conn.close()

# Function to delete a task
def delete_task(task_id):
    conn = sqlite3.connect('todo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM tasks WHERE id = ?
    ''', (task_id,))
    conn.commit()
    conn.close()

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

# Display tasks for the upcoming week
st.subheader("Tasks for the Upcoming Week")
today = datetime.now().date()
week_later = today + timedelta(days=7)
tasks = get_tasks_by_date_range(today, week_later)

if tasks:
    for i in range(7):  # Iterate over the next 7 days
        date = today + timedelta(days=i)
        st.write(f"### {date.strftime('%A, %d %B %Y')}")
        daily_tasks = [task for task in tasks if task[5] == date.strftime('%Y-%m-%d')]
        if daily_tasks:
            for task in daily_tasks:
                with st.container():
                    cols = st.columns([3, 1, 1])
                    task_title = f"**{task[1]}**" + (f" ({task[3]})" if task[3] else "")
                    cols[0].markdown(task_title)
                    cols[0].markdown(f"🗒️ {task[2]}" if task[2] else "")
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
            st.write("No tasks for this day.")
else:
    st.info("No tasks found for the upcoming week. Add some tasks to see them here!")

# Footer
st.write("Built with ❤️ using Streamlit")
