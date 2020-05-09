from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_moment import Moment
from flask_codemirror import CodeMirror

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 # 1 MB
app.config['UPLOAD_FOLDER'] = 'solution_files'
app.config['CODEMIRROR_LANGUAGES'] = ['python', 'html']
#app.config['CODEMIRROR_THEME'] = '3024-day'

api = Api(app)
db = SQLAlchemy(app)
manager = LoginManager(app)
moment = Moment(app)
codemirror = CodeMirror(app)

from lyceum.lessons_resources import LessonResource, LessonsListResource

api.add_resource(LessonResource, '/api/student/lessons/<int:lesson_id>')
api.add_resource(LessonsListResource, '/api/student/lessons')

migrate = Migrate(app, db)
db_manager = Manager(app)
db_manager.add_command('db', MigrateCommand)

from lyceum import models, routes

db.create_all()