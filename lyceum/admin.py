from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from lyceum import app, db
from lyceum.models import User, Lesson, Task


@app.route('/admin')
@login_required
def admin_page():
    lessons = db.session.query(Lesson).all()
    users = db.session.query(User).all()
    tasks = db.session.query(Task).all()
    return render_template('admin_templates/admin.html', lessons=lessons, users=users, tasks=tasks)


@app.route('/add-lesson', methods=["POST"])
@login_required
def add_lesson_page():
    title = request.form.get('title')
    deadline = request.form.get('deadline')
    lesson = Lesson(title=title, deadline=deadline)
    db.session.add(lesson)
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route('/add-task', methods=["POST"])
@login_required
def add_task_page():
    title = request.form.get('title')
    type = request.form.get('type')
    description = request.form.get('description')
    task = Task(title=title, type=type, description=description)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route('/add-task-lesson', methods=["POST"])
@login_required
def add_task_lesson_page():
    lesson_id = request.form.get('lesson')
    task_id = request.form.get('task')
    lesson = db.session.query(Lesson).get(lesson_id)
    task = db.session.query(Task).get(task_id)
    lesson.add_task(task)
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route('/add-user-lesson', methods=["POST"])
@login_required
def add_user_lesson_page():
    lesson_id = request.form.get('lesson')
    user_id = request.form.get('user')
    lesson = db.session.query(Lesson).get(lesson_id)
    user = db.session.query(User).get(user_id)
    user.add_lesson(lesson)
    db.session.commit()
    return redirect(url_for('admin_page'))


@app.route('/change-task-status', methods=["POST"])
@login_required
def change_task_status():
    user_id = request.form.get('user')
    task_id = request.form.get('task')
    status = request.form.get('status')
    user = db.session.query(User).get(user_id)
    user.change_task_status(task_id, status)
    db.session.commit()
    return redirect(url_for('admin_page'))