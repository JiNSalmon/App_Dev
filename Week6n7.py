from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient

app = Flask(__name__)
auth = HTTPBasicAuth()

mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['student_db']
students_collection = db['students']

users = {
    'username': 'password',
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@app.route('/')
def welcome():
    return 'Welcome to Student Management API'

@app.route('/students', methods=['GET'])
@auth.login_required
def get_all_students():
    all_students = list(students_collection.find({}, {'_id': 0}))
    return jsonify(all_students)

@app.route('/students/<int:std_id>', methods=['GET'])
@auth.login_required
def get_student(std_id):
    student = students_collection.find_one({'id': std_id}, {'_id': 0})
    if student:
        return jsonify(student)
    else:
        abort(404, {"error": "Student not found"})

@app.route('/students', methods=['POST'])
@auth.login_required
def create_student():
    new_student_data = request.json
    existing_student = students_collection.find_one({'id': new_student_data['id']})
    if existing_student:
        abort(500, {"error": "Cannot create new student"})
    else:
        students_collection.insert_one(new_student_data)
        return jsonify(new_student_data), 200

@app.route('/students/<int:std_id>', methods=['PUT'])
@auth.login_required
def update_student(std_id):
    updated_student_data = request.json
    existing_student = students_collection.find_one({'id': std_id})
    if existing_student:
        students_collection.update_one({'id': std_id}, {'$set': updated_student_data})
        return jsonify(updated_student_data), 200
    else:
        abort(404, {"error": "Student not found"})

@app.route('/students/<int:std_id>', methods=['DELETE'])
@auth.login_required
def delete_student(std_id):
    result = students_collection.delete_one({'id': std_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Student deleted successfully"}), 200
    else:
        abort(404, {"error": "Student not found"})

if __name__ == '__main__':
    app.run(debug=True)
