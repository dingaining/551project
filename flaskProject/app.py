from flask import Flask, render_template, request, session, redirect, url_for
import pymongo

client = pymongo.MongoClient("localhost", 27017)
db_test = client.project
collection = db_test.emp

app = Flask(__name__)


@app.route('/')
def index():  # All Results, index page
    emp = []
    a = collection.find({}, {"_id": 0})
    for i in a:
        emp.append(i)
    return render_template("index.html", data = emp)

@app.route('/index/get', methods=['GET', 'POST'])
def get():  # Search
    if request.method == 'POST':
        get_dict = {}
        get_dict['EEID'] = request.form.get('EEID')
        get_dict['Full Name'] = request.form.get('Full Name')
        get_dict['Job Title'] = request.form.get('Job Title')
        get_dict['Department'] = request.form.get('Department')
        get_dict['Business Unit'] = request.form.get('Business Unit')
        get_dict['Gender'] = request.form.get('Gender')
        get_dict['Age'] = request.form.get('Age')
        get_dict['Hire Date'] = request.form.get('Hire Date')
        get_dict['Annual Salary'] = request.form.get('Annual Salary')
        get_dict['Bonus %'] = request.form.get('Bonus %')
        get_dict['Country'] = request.form.get('Country')
        get_dict['Exit Date'] = request.form.get('Exit Date')

        get_query = {}
        for i in get_dict.items():
            if i[1] != '':
                if i[0] == 'Age' or i[0] == 'Annual Salary':
                    get_query[i[0]] = int(get_dict[i[0]])
                else:
                    get_query[i[0]] = get_dict[i[0]]
        a = collection.find(get_query, {"_id": 0})
        emp = []
        for i in a:
            emp.append(i)
        print(emp)
        return render_template("index.html", data = emp)

@app.route('/index/put', methods=['GET', 'POST'])
def put():  # Put
    if request.method == 'POST':
        get_dict = {}
        get_dict['EEID'] = request.form.get('EEID')
        get_dict['Full Name'] = request.form.get('Full Name')
        get_dict['Job Title'] = request.form.get('Job Title')
        get_dict['Department'] = request.form.get('Department')
        get_dict['Business Unit'] = request.form.get('Business Unit')
        get_dict['Gender'] = request.form.get('Gender')
        get_dict['Age'] = request.form.get('Age')
        get_dict['Hire Date'] = request.form.get('Hire Date')
        get_dict['Annual Salary'] = request.form.get('Annual Salary')
        get_dict['Bonus %'] = request.form.get('Bonus %')
        get_dict['Country'] = request.form.get('Country')
        get_dict['Exit Date'] = request.form.get('Exit Date')

        res = collection.insert_one(get_dict)
        emp = []
        a = collection.find({}, {"_id": 0})
        for i in a:
            emp.append(i)
        return render_template("index.html", data=emp)
        print(res)

@app.route('/index/del', methods=['GET', 'POST'])
def delete():  # delete
    if request.method == 'POST':
        get_dict = {}
        get_dict['EEID'] = request.form.get('eid')
        res = collection.delete_one(get_dict)
        emp = []
        a = collection.find({}, {"_id": 0})
        for i in a:
            emp.append(i)
        return render_template("index.html", data=emp)

@app.route('/index/upd', methods=['GET', 'POST'])
def upd():  # update
    if request.method == 'POST':
        old_dict = {}
        old_dict['EEID'] = request.form.get('EEID')
        new_dict = {}
        new_dict['EEID'] = request.form.get('EEID')
        new_dict['Full Name'] = request.form.get('Full Name')
        new_dict['Job Title'] = request.form.get('Job Title')
        new_dict['Department'] = request.form.get('Department')
        new_dict['Business Unit'] = request.form.get('Business Unit')
        new_dict['Gender'] = request.form.get('Gender')
        new_dict['Age'] = request.form.get('Age')
        new_dict['Hire Date'] = request.form.get('Hire Date')
        new_dict['Annual Salary'] = request.form.get('Annual Salary')
        new_dict['Bonus %'] = request.form.get('Bonus %')
        new_dict['Country'] = request.form.get('Country')
        new_dict['Exit Date'] = request.form.get('Exit Date')
        res = collection.update_one(old_dict,{ "$set": new_dict })
        emp = []
        a = collection.find({}, {"_id": 0})
        for i in a:
            emp.append(i)
        return render_template("index.html", data=emp)

@app.route('/sort')
def sort(sort_by):  # put application's code here
    a = collection.find({}, {"_id":0}).sort(sort_by)
    emp = []
    for i in a:
        emp.append(i)
    return render_template("sort.html", data = emp)


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == '__main__':
    app.run()
