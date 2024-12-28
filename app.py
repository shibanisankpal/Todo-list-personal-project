import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# Database setup
conn = sqlite3.connect('todo.db', check_same_thread=False)
cursor = conn.cursor()

# Drop the existing table if it exists (only for development; comment this out in production)
cursor.execute('DROP TABLE IF EXISTS tasks')

# Create the updated tasks table
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
    ''', (title, description, category, due_date.strftime('%Y-%m-%d')))
    conn.commit()

# Function to get tasks for a date range
def get_tasks_by_date_range(start_date, end_date):
    cursor.execute('''
        SELECT * FROM tasks
        WHERE due_date BETWEEN ? AND ?
        ORDER BY due_date ASC, created_at DESC
    ''', (start_date, end_date))
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
    title = st.text_input("Task Title", value="")
    description = st.text_area("Description", value="")
    category = st.selectbox("Category", ["Work", "Personal", "Shopping", "Others"])
    due_date = st.date_input("Due Date", min_value=datetime.today().date())
    submitted = st.form_submit_button("Add Task")
    
    if submitted:
        if title.strip():
            add_task(title, description, category, due_date)
            st.success("Task added successfully!")
            # Use session state to trigger UI update
            if "refresh" not in st.session_state:
                st.session_state.refresh = True
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
                        if cols[1].button(f"✅ Complete {task[0]}"):
                            update_task_status(task[0], "Completed")
                            if "refresh" not in st.session_state:
                                st.session_state.refresh = True
                    else:
                        cols[1].write("✔️ Completed")

                    if cols[2].button(f"🗑️ Delete {task[0]}"):
                        delete_task(task[0])
                        if "refresh" not in st.session_state:
                            st.session_state.refresh = True
        else:
            st.write("No tasks for this day.")
else:
    st.info("No tasks found for the upcoming week. Add some tasks to see them here!")

# Handle refresh
if "refresh" in st.session_state and st.session_state.refresh:
    st.session_state.refresh = False
    st.experimental_rerun()  # Re-run only when required
