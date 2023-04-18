from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
"""实现: 1. 设置Session
        2. 设置管理员 ？手动设定：自动校验
        3. Sort排序
        4. 扩大搜索条件
"""
client = pymongo.MongoClient("localhost", 27017)
db_test = client.project
collection = db_test.emp

app = Flask(__name__)

@app.route('/')
def login_page():  # All Results, index page
    return render_template("login.html")

@app.route('/', methods=["Get","Post"])
def login():  # All Results, index page
    if request.method == 'Get':
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
            return render_template("index.html", data = emp)
        return render_template("index1.html", data = emp)
    else:
        return render_template("login.html", msg = 'The EEID or password you entered may be incorrect!')


@app.route('/index')
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
        if len(request.form.get('Bonus %')) > 0:
            get_dict['Bonus %'] = request.form.get('Bonus %') + '%'
        else:
            get_dict['Bonus %'] = request.form.get('Bonus %')
        get_dict['Country'] = request.form.get('Country')
        get_dict['Exit Date'] = request.form.get('Exit Date')

        get_query = {}
        for i in get_dict.items():
            if i[1] != '':
                if i[0] == 'Age':
                    get_query[i[0]] = int(get_dict[i[0]])
                elif i[0] == 'Annual Salary':
                    print(type(get_dict[i[0]]))
                    if int(get_dict[i[0]]) > 999:
                        get_query[i[0]] = '$' + get_dict[i[0]][:-3] + ',' + get_dict[i[0]][-3:]
                    else:
                        get_query[i[0]] = '$' + get_dict[i[0]]
                else:
                    get_query[i[0]] = get_dict[i[0]]
        print(get_query)
        a = collection.find(get_query, {"_id": 0})
        emp = []
        for i in a:
            emp.append(i)
        print(emp)
        return render_template("index.html", data=emp)

@app.route('/index1')
def index1():  # All Results, index page
    emp = []
    a = collection.find({}, {"_id": 0})
    for i in a:
        emp.append(i)
    return render_template("index1.html", data = emp)

@app.route('/index1/get', methods=['GET', 'POST'])
def get1():  # Search
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
        if len(request.form.get('Bonus %'))>0:
            get_dict['Bonus %'] = request.form.get('Bonus %') + '%'
        else:
            get_dict['Bonus %'] = request.form.get('Bonus %')
        get_dict['Country'] = request.form.get('Country')
        get_dict['Exit Date'] = request.form.get('Exit Date')

        get_query = {}
        for i in get_dict.items():
            if i[1] != '':
                if i[0] == 'Age' :
                    get_query[i[0]] = int(get_dict[i[0]])
                elif i[0] == 'Annual Salary' :
                    if int(get_dict[i[0]]) > 999:
                        get_query[i[0]] = '$' + get_dict[i[0]][:-3] + ',' + get_dict[i[0]][-3:]
                    else:
                        get_query[i[0]] = '$' + get_dict[i[0]]
                else:
                    get_query[i[0]] = get_dict[i[0]]

        a = collection.find(get_query, {"_id": 0})
        emp = []
        for i in a:
            emp.append(i)
        print(emp)
        return render_template("index1.html", data = emp)
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
        if len(request.form.get('Age')) > 0:
            get_dict['Age'] = int(request.form.get('Age'))
        else:
            get_dict['Age'] = request.form.get('Age')
        get_dict['Hire Date'] = request.form.get('Hire Date')
        if len(request.form.get('Annual Salary')) > 0:
            if len(request.form.get('Annual Salary')) > 3:
                get_dict['Annual Salary'] = '$'+request.form.get('Annual Salary')[:-3]+','+request.form.get('Annual Salary')[-3:]
            else:
                get_dict['Annual Salary'] = '$'+request.form.get('Annual Salary')
        else:
            get_dict['Annual Salary'] = request.form.get('Annual Salary')
        if len(request.form.get('Bonus %')) > 0:
            get_dict['Bonus %'] = request.form.get('Bonus %')+'%'
        else:
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
        if len(request.form.get('Age')) > 0:
            new_dict['Age'] = int(request.form.get('Age'))
        else:
            new_dict['Age'] = request.form.get('Age')
        new_dict['Hire Date'] = request.form.get('Hire Date')
        if len(request.form.get('Annual Salary')) > 0:
            if len(request.form.get('Annual Salary')) > 3:
                new_dict['Annual Salary'] = '$' + request.form.get('Annual Salary')[:-3] + ',' + request.form.get(
                    'Annual Salary')[-3:]
            else:
                new_dict['Annual Salary'] = '$' + request.form.get('Annual Salary')
        else:
            new_dict['Annual Salary'] = request.form.get('Annual Salary')
        if len(request.form.get('Bonus %')) > 0:
            new_dict['Bonus %'] = request.form.get('Bonus %') + '%'
        else:
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
