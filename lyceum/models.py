from flask_login import UserMixin
from datetime import datetime

from lyceum import db, manager


user_lesson = db.Table('user_lesson', 
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
        db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), nullable=False),
        db.Column('is_open', db.Boolean, nullable=False, default=False))

user_task = db.Table('user_task', 
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
        db.Column('lesson_id', db.Integer, nullable=False, default=0),
        db.Column('task_id', db.Integer, db.ForeignKey('task.id'), nullable=False),
        db.Column('status', db.String(128), nullable=False, default="None")) # None, Wrong, Right

lesson_task = db.Table('lesson_task', 
        db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), nullable=False),
        db.Column('task_id', db.Integer, db.ForeignKey('task.id'), nullable=False))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(128), nullable=False, default='Classwork') # Classwork, Homework, Addwork
    description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Task {}>'.format(self.title)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    tasks = db.relationship('Task', secondary=lesson_task, backref=db.backref('lessons', lazy='dynamic'))
    type = db.Column(db.String(128), nullable=False, default='normal')
    
    def add_task(self, task):
        if task not in self.tasks:
            self.tasks.append(task)
            self.update_task_in_user()
    
    def update_task_in_user(self):
        for user in self.users:
            user.add_tasks()
    
    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'numTasks': len(self.tasks),
        }
        return data

    def __repr__(self):
        return '<Lesson {}>'.format(self.title)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False, default='default_avatar.jpg')
    role = db.Column(db.String(255), nullable=False, default='student') # student, teacher, admin
    score = db.Column(db.Integer, nullable=False, default='0')
    lessons = db.relationship('Lesson', secondary=user_lesson, backref=db.backref('users', lazy='dynamic'))
    tasks = db.relationship('Task', secondary=user_task, backref=db.backref('users', lazy='dynamic'))
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def add_lesson(self, lesson):
        if lesson not in self.lessons:
            self.lessons.append(lesson)
            self.add_tasks()

    # Переписать
    def add_tasks(self):
        for lesson in self.lessons:
            for task in lesson.tasks:
                if task not in self.tasks:
                    self.tasks.append(task)
        db.session.commit()
        self.update_task_lesson()

    def update_task_lesson(self):
        for lesson in self.lessons:
            for task in lesson.tasks:
                db.session.execute(user_task.update().where(user_task.c.task_id == task.id).where(user_task.c.user_id == self.id).values(lesson_id = lesson.id))

    def get_lesson(self, lesson_id):
        return db.session.query(Lesson).get(lesson_id)

    def get_task(self, task_id):
        return db.session.query(Task).get(task_id)

    def get_task_status(self, task_id):
        return db.session.query(user_task).filter(user_task.c.task_id == task_id).filter(user_task.c.user_id == self.id).first()[3]
    
    def get_count_passed_task(self, lesson_id):
        return db.session.query(user_task).filter(user_task.c.status == "Right").filter(user_task.c.user_id == self.id).filter(user_task.c.lesson_id == lesson_id).count()

    def get_task_in_lesson(self, lesson_id):
        return db.session.query(user_task).filter(user_task.c.user_id == self.id).filter(user_task.c.lesson_id == lesson_id).count()

    def get_percent_of_passed(self, lesson_id):
        if self.get_task_in_lesson(lesson_id):
            return self.get_count_passed_task(lesson_id) * 100 // self.get_task_in_lesson(lesson_id)
        else:
            return 0

    def change_task_status(self, task_id, status):
        db.session.execute(user_task.update().where(user_task.c.task_id == task_id).where(user_task.c.user_id == self.id).values(status = status))
    
    def check_lesson(self, lesson_id):
        return db.session.query(Lesson).get(lesson_id) in self.lessons
    
    def __repr__(self):
        return '<User {}>'.format(self.login) 


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(128), nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(128), nullable=False, default="None")

    def __repr__(self):
        return '<Solution {}>'.format(self.id) 


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)