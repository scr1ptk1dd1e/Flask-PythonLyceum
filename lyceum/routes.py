from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from flask_wtf import FlaskForm
from flask_codemirror.fields import CodeMirrorField


from lyceum import app, db
from lyceum.models import User, Lesson, Task, Solution
import lyceum.admin


@app.route('/register', methods=["GET", "POST"])
@app.route('/register/', methods=["GET", "POST"])
def register_page():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login and password and password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
@app.route('/login/', methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('lessons_page'))

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            user = User.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                if request.args.get('next'):
                    next_page = request.args.get('next')
                else:
                    next_page = url_for('lessons_page')
                return redirect(next_page)
            else:
                flash('Not correct')
        else:
            flash('empty')

    return render_template('login.html')


@app.route('/')
@app.route('/lessons')
@app.route('/lessons/')
@login_required
def lessons_page():
    return render_template('lessons.html')


@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson_page(lesson_id):
    if current_user.check_lesson(lesson_id):
        return render_template('lesson.html', lesson_id=lesson_id)
    else:
        return abort(404, description="Lesson not found")


class CodeForm(FlaskForm):
    source_code = CodeMirrorField(language='python', config={'lineNumbers': 'true', 'readOnly': 'true'})

@app.route('/task/<int:task_id>')
@login_required
def task_page(task_id):
    if not db.session.query(Task).get(task_id):
        return abort(404)

    if current_user not in db.session.query(Task).get(task_id).users:
        return abort(404)

    solutions = db.session.query(Solution).filter_by(user_id=current_user.id, task_id=task_id).all()
    
    form = CodeForm()

    if solutions:
        last_solution = solutions[-1]

        with open(f'solution_files/{current_user.id}/{task_id}/{last_solution.file}', 'r', encoding='utf-8') as solution:
            form.source_code.data = solution.read()
    
    return render_template('task.html', task_id=task_id, solutions=solutions, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['py'])

@app.route('/send-solution/<int:task_id>', methods=["POST"])
def send_solution(task_id):
    file = request.files["solution"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename2 = filename
        path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), str(task_id))
        i = 1

        while os.path.isfile(os.path.join(path_to_save, filename2)):
            i += 1
            filename2 = filename.rsplit('.', 1)[0] + '_' + str(i) + '.' + filename.rsplit('.', 1)[1]

        if filename2 != filename:
            filename = filename2

        try:
            file.save(os.path.join(path_to_save, filename))
        except Exception:
            os.makedirs(path_to_save)
            file.save(os.path.join(path_to_save, filename))

        solution = Solution(file=filename, task_id=task_id, user_id=current_user.id)
        db.session.add(solution)
        db.session.commit()

        return redirect(request.referrer)
    return "only .py"


@app.errorhandler(401)
def redirect_to_signin(error):
    return redirect(url_for('login_page') + '?next=' + request.url)

@app.errorhandler(413)
def err_413(error):
    return render_template("Размеры файла превышают 1 МБ")