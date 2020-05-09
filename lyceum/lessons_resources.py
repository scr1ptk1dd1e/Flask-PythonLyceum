# Не юзается

from flask_restful import Resource, reqparse
from flask import abort, jsonify
from flask_login import current_user

from lyceum import api, db
from lyceum.models import Lesson


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('numTasks', required=True, type=int)
parser.add_argument('numPassed', required=True, type=int)
parser.add_argument('deadline', required=True)
parser.add_argument('type', required=False)

def abort_if_smth():
    abort(404, message='aborted')


class LessonResource(Resource):
    def get(self, lesson_id):
        lessons = db.session.query(Lesson).get(lesson_id)
        return jsonify({'lesson': lessons.to_dict()})


class LessonsListResource(Resource):
    def get(self):
        lessons = current_user.lessons
        return jsonify({'lessons': [lesson.to_dict() for lesson in lessons]})
    
    def post(self):
        args = parser.parse_args()
        lesson = Lesson(
            title=args['title'],
            numTasks=args['numTasks'],
            numPassed=args['numPassed'],
            deadline=args['deadline'],
            type=args['type']
        )
        db.session.add(lesson)
        db.session.commit()
        return jsonify({'success': 'OK'})