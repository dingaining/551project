# Instruction:

packages needed: flask; pymongo; flask_socketio
environment needed: have downloaded MongoDB Community and make an connection on localhost:27017

(1) run load_data.py to initialize the database, which include loading the dataset from sampleData/Employee.json and indexing all the fields

(2) run command.py, which is the only backend of this project

(3-1) use normal curl command to CREATE, UPDATE, READ and DELETE. for example:

    curl -X GET 'http://localhost:5000/employees.json'
    curl -X GET 'http://localhost:5000/employees.json?orderBy="Full%20Name"&limitToFirst=5' 
    curl -X GET 'http://localhost:5000/employees.json?orderBy="Bonus%20%25"&equalTo="25%"'
    curl -X GET 'http://localhost:5000/employees.json?orderBy="Age"&startAt=25&endAt=26'
    curl -X PUT 'http://localhost:5000/employees/E100000.json' -d '{"Full Name": "George Bush","Job Title": "President","Department": "Politics","Business Unit": "Overall Development","Gender": "Male","Age": 94,"Hire Date": "1/20/1989","Annual Salary": "$400,000","Bonus %": "15%","Country": "United States","Exit Date": "01/20/1993"}'
    curl -X POST 'http://localhost:5000/employees.json' -d '{"Full Name": "John Doe","Job Title": "Developer","Department": "IT","Business Unit": "Software","Gender": "Male","Age": 28,"Hire Date": "10/01/2017","Annual Salary": "$80,000","Bonus %": "5%","Country": "United States","Exit Date": ""}'
    curl -X PATCH 'http://localhost:5000/employees/E100000.json' -d '{"Business Unit": "Overall Leadership", "Bonus %": "20%"}'
    curl -X DELETE 'http://localhost:5000/employees/E100000.json'
OR:

(3-2) open localhost:5000 with browser, it will show login.html. login with the eeid of employee. Currently the EEID of E02387 with password of "password" is the administrator with permission to CREATE, UPDATE, READ and DELETE. Other EEIDs(eg. E04105) with password of "password" are the users with permission to READ. After log in, it will jump to corresponding page: admin_page.html and page.html

(4-1) For administrator, it has 4 buttons:
    Delete Employee: delete employee by EEID
    Add or Overwrite Employee: if you input value for EEID, it will call the PUT to add or overwrite the employee's information for the EEID. if no value input for EEID, it will call the POST to randomly generate new EEID and add the employee for the new EEID. Other fields are optional.
    Update Employee: EEID is required. it will call the PATCH to update certain fields for this EEID.
    Filter: with Order By, Limit To First, Limit To Last, Equal To, Start At, End At. Order By is required if other fields have values. Same as usage method of curl command but no need to quote.

(4-2) For user, it has only Filter buttons. Same as Filter stated above.

About real-time syncing:
The localhost:5000 allow multiple users after logging in. Every user can do their own things without interrupt. The only situation is that if someone successfully changed(put/post/patch/delete) the data and confirm the change, the whole data will update to everyone at the same time. 

file current in use: 

load_data.py
command.py
/templates/login.html
/templates/page.html
/templates/admin_page.html
/static/javaex/pc/css/common.css
/static/javaex/pc/css/skin/tina.css

### TODO:

(1) (DONE)Multiple clients at the same time connect to the server do different things but sync with each other.

(2) (DONE)Error message or successful message to report on the frontend webpage.

(3) Thoroughly test to ensure everything is working correctly.

(4) (DONE)Log out function

(5) (DONE with 3 admin of Vice President for Human Resources department and Corporate Unit)  More reasonable way to set the users' permission. eg. select Job Title: Vice President, Department: Human Resources to be the administrator?

(6) (DONE) The normal user is not in url: http://localhost:5000/user. And the admin is now in url: http://localhost:5000/admin. But it cannot directly access. It will redirect to the login page if not log in. 
