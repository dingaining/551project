from flask import Flask, request, jsonify, render_template
import pymongo
import json
import uuid
from flask_socketio import SocketIO, emit

client = pymongo.MongoClient("localhost", 27017)
# Define database "project" and collection in the database named "emp"
db_test = client.project
collection = db_test.emp

app = Flask(__name__)
# Create the SocketIO object after creating the Flask app
socketio = SocketIO(app, cors_allowed_origins="*")
@app.route('/')
def login_page():  # All Results, index page
    return render_template("login.html")

@app.route('/', methods=["GET","POST"])
def login():  # All Results, index page
    if request.method == 'GET':
        return render_template("login.html")
    eeid = request.form.get('email')
    pwd = request.form.get('password')
    a = collection.find({}, {"_id": 0})
    emp = []
    verify = False
    admin = False
    for i in a:
        emp.append(i)
        if i['EEID'] == eeid and pwd == 'password':
            verify = True
            if eeid == 'E02387':
                admin = True
    if verify:
        if admin:
            return render_template("admin_page.html", data = emp)
        return render_template("page.html", data = emp)
    else:
        return render_template("login.html", msg = 'The EEID or password you entered may be incorrect!')

# GET and filtering function: orderBy=”$key”/”$value”/”name”, limitToFirst/Last, equalTo, startAt/endAt for the whole data

def ws_get_employees(orderBy=None, limitToFirst=0, limitToLast=0, equalTo=None, startAt=None, endAt=None):
    # check if orderBy is not defined while other query parameters are present
    if not orderBy and (limitToFirst or limitToLast or equalTo or startAt or endAt):
        return {"error": "orderBy must be defined when other query parameters are defined"}
    if orderBy:
        orderBy = orderBy.replace('"', '')
        # initialize the query
        query = []

        # set match query as equalTo or to integrate startAt and endAt in the same part
        match_query = {}
        if equalTo:
            equalTo = equalTo.replace('"', '')
            if orderBy == 'Age':
                equalTo = int(equalTo)
            match_query[orderBy] = equalTo
        else:
            if startAt:
                startAt = startAt.replace('"', '')
                if orderBy == 'Age':
                    startAt = int(startAt)
                match_query[orderBy] = {"$gte": startAt}
            if endAt:
                endAt = endAt.replace('"', '')
                if orderBy == 'Age':
                    endAt = int(endAt)
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
    else:
        emp = []
        a = collection.find({}, {"_id": 0})
        for i in a:
            emp.append(i)
    return emp

# command line # eg. curl -X GET 'http://localhost:5000/employees.json' to get the whole data
# or using filtering function eg. curl -X GET 'http://localhost:5000/employees.json?orderBy="Full%20Name"&limitToFirst=5' ; curl -X GET 'http://localhost:5000/employees.json?orderBy="Bonus%20%25"&equalTo="25%"'
@app.route('/employees.json', methods=['GET'])
def get_employees():
    orderBy = request.args.get('orderBy', default=None)
    limitToFirst = int(request.args.get('limitToFirst', default=0))
    limitToLast = int(request.args.get('limitToLast', default=0))
    equalTo = request.args.get('equalTo', default=None)
    startAt = request.args.get('startAt', default=None)
    endAt = request.args.get('endAt', default=None)
    result = ws_get_employees(orderBy, limitToFirst, limitToLast, equalTo, startAt, endAt)
    # Check if the result is an error and handle it
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
        return jsonify(result[0]), result[1]

    return jsonify(result)

# WebSocket event handler for getting employees
@socketio.on('get_employees')
def handle_get_employees(data):
    orderBy = data.get('orderBy')
    limitToFirst = int(data.get('limitToFirst', 0))
    limitToLast = int(data.get('limitToLast', 0))
    equalTo = data.get('equalTo')
    startAt = data.get('startAt')
    endAt = data.get('endAt')

    result = ws_get_employees(orderBy, limitToFirst, limitToLast, equalTo, startAt, endAt)
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
        emit('employees_received', result[0], broadcast=True)
    emit('employees_received', result, broadcast=True)

# PUT for adding new employee or overwriting employee's information by its EEID
def ws_put_employee(eeid, dicts):
    try:
        # To adjust the order of keys
        data = {}
        data['EEID'] = eeid
        data.update(dicts)
        # check if employee with eeid already exists
        if collection.count_documents({'EEID': eeid}) > 0:
            # overwrite existing employee with new data
            # reference: Update Operation part on https://www.mongodb.com/docs/v4.4/crud/
            # As it can replace the whole document, it's corresponded to the overwrite function when data exists.
            collection.replace_one({'EEID': eeid}, data)
            return {"message": f"Employee {eeid} updated successfully."}
        else:
            # insert new employee with eeid
            collection.insert_one(data)
            return {"message": f"Employee {eeid} added successfully."}
    except Exception as e:
        return {"error": str(e)}

# copmmand line eg. curl -X PUT 'http://localhost:5000/employees/E100000.json' -d '{"Full Name": "George Bush","Job Title": "President","Department": "Politics","Business Unit": "Overall Development","Gender": "Male","Age": 94,"Hire Date": "1/20/1989","Annual Salary": "$400,000","Bonus %": "15%","Country": "United States","Exit Date": "01/20/1993"}'
@app.route('/employees/<string:eeid>.json', methods=['PUT'])
def put_employee(eeid):
    # try to parse request data as JSON
    data = request.get_json(silent=True)
    # if parsing failed or data is empty, try to parse request data as form data
    # for curl without -H "Content-Type: application/json" in the format as Firebase, it cannot be recognized as json
    # It will be retrieved as a key(though I don't know why). Try to retrieve the key-value pairs
    if not data:
        data = request.form.to_dict()
        for key, value in data.items():
            dicts = json.loads(key)
    result = ws_put_employee(eeid, dicts)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

# WebSocket event handler for adding or overwriting employees
@socketio.on('put_employee')
def handle_put_employee(data):
    eeid = data.get('EEID')
    # employee_data needs to be a dictionary
    dicts = data
    result = ws_put_employee(eeid, dicts)
    emit('employees_put', result, broadcast=True)
    emit('get_employees', {}, broadcast=True)

# POST: Create a new employee without specifying EEID (server generates EEID automatically).
def ws_post_employee(dicts):
    try:
        # Generate a unique EEID using the uuid library
        eeid = f'E{str(uuid.uuid4())[:6].upper()}'
        data = {}
        data['EEID'] = eeid
        data.update(dicts)
        data['EEID'] = eeid
        collection.insert_one(data)
        return {"message": f"New employee {eeid} added successfully."}
    except Exception as e:
        return {"error": str(e)}

# command line eg. curl -X POST 'http://localhost:5000/employees.json' -d '{"Full Name": "John Doe","Job Title": "Developer","Department": "IT","Business Unit": "Software","Gender": "Male","Age": 28,"Hire Date": "10/01/2017","Annual Salary": "$80,000","Bonus %": "5%","Country": "United States","Exit Date": ""}'
@app.route('/employees.json', methods=['POST'])
def post_employee():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()
        for key, value in data.items():
            dicts = json.loads(key)

    result = ws_post_employee(dicts)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

# WebSocket event handler for posting new employees
@socketio.on('post_employee')
def handle_post_employee(data):
    result = ws_post_employee(data)
    emit('employees_posted', result, broadcast=True)
    emit('get_employees', {}, broadcast=True)

# PATCH: Update specific fields of an existing employee by their EEID.
def ws_patch_employee(eeid, data):
    try:
        # update the specified fields or create them if they don't exist
        # insert a new document with the EEID and data if the document doesn't exist
        result = collection.update_one({'EEID': eeid}, {'$set': data}, upsert=True)

        if result.matched_count > 0:
            return {"message": f"Employee {eeid} updated successfully."}
        else:
            return {"error": f"Employee {eeid} not found but upserted successfully"}, 404
    except Exception as e:
        return {"error": str(e)}, 400

# command line eg. curl -X PATCH 'http://localhost:5000/employees/E100000.json' -d '{"Business Unit": "Overall Leadership", "Bonus %": "20%"}'
@app.route('/employees/<string:eeid>.json', methods=['PATCH'])
def patch_employee(eeid):
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()
        for key, value in data.items():
            dicts = json.loads(key)
        data = dicts
    result = ws_patch_employee(eeid, data)
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
        return jsonify(result[0]), result[1]
    return jsonify(result)

# WebSocket event handler for patching employee
@socketio.on('patch_employee')
def handle_patch_employee(data):
    eeid = data.get('eeid')
    # employee_data needs to be a dictionary
    data = data.get('employee_data')

    result = ws_patch_employee(eeid, data)
    emit('employee_updated', result, broadcast=True)
    emit('get_employees', {}, broadcast=True)

# DELETE: Remove an existing employee by their EEID.
def ws_delete_employee(eeid):
    try:
        print(eeid)
        print(type(eeid))
        # Check if employee with eeid exists
        result = collection.delete_one({'EEID': eeid})

        count = result.deleted_count
        if count > 0:
            return {"message": f"Employee {eeid} deleted successfully, {count} record of employee deleted"}
        else:
            return {"error": f"Employee {eeid} not found."}, 404
    except Exception as e:
        return {"error": str(e)}, 400

# eg. curl -X DELETE 'http://localhost:5000/employees/E100000.json'
@app.route('/employees/<string:eeid>.json', methods=['DELETE'])
def delete_employee(eeid):
    result = ws_delete_employee(eeid)
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
        return jsonify(result[0]), result[1]
    return jsonify(result)

# WebSocket event handler for deleting employee
@socketio.on('delete_employee')
def handle_delete_employee(eeid):
    result = ws_delete_employee(eeid)
    emit('employee_deleted', result, broadcast=True)
    emit('get_employees', {}, broadcast=True)

# WebSocket basic event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
