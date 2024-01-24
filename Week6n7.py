from flask import Flask,jsonify,request
from pymongo.mongo_client import MongoClient
from flask_basicauth import BasicAuth
import certifi

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'name'
app.config['BASIC_AUTH_PASSWORD'] = 'pass'
basic_auth = BasicAuth(app)

ca = certifi.where()
uri = "mongodb+srv://new-user1:Y1AGgX1NGUy1ZHwg@cluster0.fdsqycw.mongodb.net/"

try:
    client = MongoClient(uri, tlsCAFile=ca)
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route("/")
def Greet():
    return "<p>Welcome to Student Management AP</p>"

@app.route("/students",methods=["GET"])
@basic_auth.required
def get_all_student():
    try:
        db = client["students"]
        collection = db["std_info"]
        all_student = list(collection.find())
        return jsonify(all_student)
    except Exception as e:
        print(e)

@app.route("/students/<string:std_id>", methods=["GET"])
def get_id_student(std_id):
    try:
        db = client["students"]
        collection = db["std_info"]
        all_student = list(collection.find())
        std = next((s for s in all_student if s["_id"] == std_id), None)
        if(std):
            return jsonify(std)
        else:
            return jsonify({"error":"Student not found"}), 404
    except Exception as e:
        print(e)

@app.route("/students", methods=["POST"])
def add_new_student():
    try:
        db = client["students"]
        collection = db["std_info"]
        data = request.get_json()
        new_student={
            "_id":data["_id"],
            "fullname": data["fullname"],
            "major": data["major"],
            "gpa": data["gpa"]
        }
        all_student = list(collection.find())
        if(next((s for s in all_student if s["_id"] == data["_id"]), None)):
            return jsonify( {"error":"Cannot create new student"}),500
        else:
            collection.insert_one(new_student)
            return jsonify(new_student),200
        
    except Exception as e:
        print(e)

@app.route("/students/<string:std_id>", methods=["PUT"])
def update_student(std_id):
    try:
        db = client["students"]
        collection = db["std_info"]
        data = request.get_json()
        new_fullname = {"$set":{"fullname":data["fullname"]}}
        new_major = {"$set":{"major":data["major"]}}
        new_gpa = {"$set":{"gpa":data["gpa"]}}
        all_student = list(collection.find())
        if(next((s for s in all_student if s["_id"] == data["_id"]), None)):
            print("Found")
            collection.update_one({"_id" : std_id}, new_fullname)
            collection.update_one({"_id" : std_id}, new_major)
            collection.update_one({"_id" : std_id}, new_gpa)
            return jsonify(data),200
        else:
            return jsonify({"error":"Student not found"}),404
        
    except Exception as e:
        print(e)

@app.route("/students/<string:std_id>", methods=["DELETE"])
def delete_student(std_id):
    try:
        db = client["students"]
        collection = db["std_info"]
        all_student = list(collection.find())
        if(next((s for s in all_student if s["_id"] == std_id), None)):
            collection.delete_one({"_id":std_id})
            return jsonify({"message":"Student deleted successfully"}),200
        else:
            return jsonify({"error":"Student not found"}),404
        
    except Exception as e:
        print(e)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)

print("disconnected")
client.close()