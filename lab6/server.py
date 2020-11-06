from flask import Flask
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
import csv

app = Flask(__name__)
# to clear the database first
# app.config["MONGO_URI"] = "mongodb://localhost:27017/database"
# app.config['MONGO_DBNAME'] = 'database'
# mongo = PyMongo(app)
# mongo.db.drop_collection("database")

app.config["MONGO_URI"] = "mongodb://localhost:27017/database"
app.config['MONGO_DBNAME'] = 'database'
mongo = PyMongo(app)
db = mongo.db


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'


@app.route('/post', methods=['POST'])
def post_data():
    x = request.json['x']
    y = request.json['y']
    z = request.json['z']
    database = mongo.db.database
    database.insert_one({'x': x, 'y': y, 'z': z})

    new_coordinate = database.find_one({'x': x} and {'y': y} and {'z': z})
    output = {'x': new_coordinate['x'], 'y': new_coordinate['y'],'z': new_coordinate['z']}

    return jsonify({'result': output})


@app.route('/get', methods=['GET'])
def get_data():
    database = mongo.db.database
    documents = database.find()
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    return json.dumps(response)


@app.route('/download', methods=['GET'])
def download():
    database = mongo.db.database
    documents = database.find()
    f = csv.writer(open("dataA.csv", "w"))
    f.writerow(["_id", "x", "y", "z"])
    for row in documents:
        f.writerow([str(row['_id']), str(row['x']), str(row['y']), str(row['z'])])
    # output = make_response(f.getvalue())
    # output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    # output.headers["Content-type"] = "text/csv"
    # return output
    return "export csv_file"


app.run(debug=True, host="0.0.0.0", port=8080)