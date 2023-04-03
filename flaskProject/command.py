from flask import Flask, request, jsonify
import pymongo
import json
import uuid

client = pymongo.MongoClient("localhost", 27017)
# Define database "project" and collection in the database named "emp"
db_test = client.project
collection = db_test.emp

app = Flask(__name__)

'''This part below is to support command line. Using curl -X to manipulate the data'''

# GET and filtering function: orderBy=”$key”/”$value”/”name”, limitToFirst/Last, equalTo, startAt/endAt for the whole data
# eg. curl -X GET 'http://localhost:5000/employees.json' to get the whole data
# or using filtering function eg. curl -X GET 'http://localhost:5000/employees.json?orderBy="Full%20Name"&limitToFirst=5' ; curl -X GET 'http://localhost:5000/employees.json?orderBy="Bonus%20%25"&equalTo="25%"'
@app.route('/employees.json', methods=['GET'])
def get_employees():
    orderBy = request.args.get('orderBy', default=None)
    limitToFirst = int(request.args.get('limitToFirst', default=0))
    limitToLast = int(request.args.get('limitToLast', default=0))
    equalTo = request.args.get('equalTo', default=None)
    startAt = request.args.get('startAt', default=None)
    endAt = request.args.get('endAt', default=None)

    # check if orderBy is not defined while other query parameters are present
    if not orderBy and (limitToFirst or limitToLast or equalTo or startAt or endAt):
        return jsonify({"error": "orderBy must be defined when other query parameters are defined"}), 400

    if orderBy:
        orderBy = orderBy.replace('"', '')
        # Age is store as number rather than string in MongoDB
        if orderBy == 'Age':
            if startAt:
                startAt = int(startAt)
            if endAt:
                endAt = int(endAt)
        # initialize the query
        query = []

        # set match query as equalTo or to integrate startAt and endAt in the same part
        match_query = {}
        if equalTo:
            equalTo = equalTo.replace('"', '')
            match_query[orderBy] = equalTo
        else:
            if startAt:
                startAt = startAt.replace('"', '')
                match_query[orderBy] = {"$gte": startAt}
            if endAt:
                endAt = endAt.replace('"', '')
                if orderBy in match_query:
                    match_query[orderBy].update({"$lte": endAt})
                else:
                    match_query[orderBy] = {"$lte": endAt}
        if match_query:
            query.append({"$match": match_query})

        # Sorting and limiting
        # handle the special case for orderBy
        if orderBy == "$key":
            pass
        elif orderBy == "$value":
            first_doc = collection.find_one({}, {"_id": 0})
            first_field = next(iter(first_doc)) if first_doc else None
            if first_field:
                query.append({"$sort": {f"{first_field}": -1 if limitToLast > 0 else 1}})
        else:
            query.append({"$sort": {f"{orderBy}": -1 if limitToLast > 0 else 1}})
        if limitToFirst > 0:
            query.append({"$limit": limitToFirst})
        elif limitToLast > 0:
            query.append({"$limit": limitToLast})
        query.append({"$project": {"_id": 0}})

        emp = [i for i in collection.aggregate(query)]
        return jsonify(emp)
    else:
        emp = []
        a = collection.find({}, {"_id": 0})
        for i in a:
            emp.append(i)
        return jsonify(emp)

# PUT for adding new employee or overwriting employee's information by its EEID
# eg. curl -X PUT 'http://localhost:5000/employees/E100000.json' -d '{"Full Name": "George Bush","Job Title": "President","Department": "Politics","Business Unit": "Overall Development","Gender": "Male","Age": 94,"Hire Date": "1/20/1989","Annual Salary": "$400,000","Bonus %": "15%","Country": "United States","Exit Date": "01/20/1993"}'
@app.route('/employees/<string:eeid>.json', methods=['PUT'])
def put_employee(eeid):
    try:
        # try to parse request data as JSON
        data = request.get_json(silent=True)
        # if parsing failed or data is empty, try to parse request data as form data
        # for curl without -H "Content-Type: application/json" in the format as Firebase, it cannot be recognized as json
        # It will be retrieve as a key(though I don't know why). Try to retrieve the key-value pairs
        if not data:
            data = request.form.to_dict()
            for key, value in data.items():
                dict = json.loads(key)
        # To adjust the order of keys
        data = {}
        data['EEID'] = eeid
        data.update(dict)
        # check if employee with eeid already exists
        if collection.count_documents({'EEID': eeid}) > 0:
            # overwrite existing employee with new data
            # reference: Update Operation part on https://www.mongodb.com/docs/v4.4/crud/
            # As it can replace the whole document, it's corresponded to the overwrite function when data exists.
            collection.replace_one({'EEID': eeid}, data)
            return jsonify({"message": f"Employee {eeid} updated successfully."})
        else:
            # insert new employee with eeid
            collection.insert_one(data)
            return jsonify({"message": f"New employee {eeid} added successfully."})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

# POST: Create a new employee without specifying EEID (server generates EEID automatically).
# eg. curl -X POST 'http://localhost:5000/employees.json' -d '{"Full Name": "John Doe","Job Title": "Developer","Department": "IT","Business Unit": "Software","Gender": "Male","Age": 28,"Hire Date": "10/01/2017","Annual Salary": "$80,000","Bonus %": "5%","Country": "United States","Exit Date": ""}'
@app.route('/employees.json', methods=['POST'])
def post_employee():
    try:
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()
            for key, value in data.items():
                dict = json.loads(key)

        # Generate a unique EEID using the uuid library
        eeid = f'E{str(uuid.uuid4())[:6].upper()}'
        data = {}
        data['EEID'] = eeid
        data.update(dict)
        collection.insert_one(data)
        return jsonify({"message": f"New employee {eeid} added successfully."})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

# PATCH: Update specific fields of an existing employee by their EEID.
# eg. curl -X PATCH 'http://localhost:5000/employees/E100000.json' -d '{"Business Unit": "Overall Leadership", "Bonus %": "20%"}'
@app.route('/employees/<string:eeid>.json', methods=['PATCH'])
def patch_employee(eeid):
    try:
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()
            for key, value in data.items():
                dict = json.loads(key)
            data = dict

        # update the specified fields or create them if they don't exist
        # insert a new document with the EEID and data if the document doesn't exist
        result = collection.update_one({'EEID': eeid}, {'$set': data}, upsert=True)

        if result.matched_count > 0:
            return jsonify({"message": f"Employee {eeid} updated successfully."})
        else:
            return jsonify({"error": f"Employee {eeid} not found but upserted successfully"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

# DELETE: Remove an existing employee by their EEID.
# eg. curl -X DELETE 'http://localhost:5000/employees/E100000.json'
@app.route('/employees/<string:eeid>.json', methods=['DELETE'])
def delete_employee(eeid):
    try:
        # Check if employee with eeid exists
        result = collection.delete_one({'EEID': eeid})
        count = result.deleted_count
        if count > 0:
            return jsonify({"message": f"Employee {eeid} deleted successfully, {count} record of employee deleted"})
        else:
            return jsonify({"error": f"Employee {eeid} not found."}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
