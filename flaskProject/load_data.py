import pymongo, json

client = pymongo.MongoClient("localhost", 27017)
# Define database "project" and collection in the database named "emp"
db_test = client.project
collection = db_test.emp

# load the initial data from Employee.json
def load_initial_data():
    try:
        with open("sampleData/Employee.json", 'r') as f:
            data = json.load(f)

        collection.insert_many(data)
        print("Initial data loaded successfully.")
    except FileNotFoundError:
        print("Employee.json not found. No initial data loaded.")

# create indices for every field
def create_indices():
    fields = ["EEID", "Full Name", "Job Title", "Department", "Business Unit", "Gender", "Age", "Hire Date",
              "Annual Salary", "Bonus %", "Country", "Exit Date"]
    for field in fields:
        collection.create_index(field)
    print("Indices created successfully.")

if __name__ == "__main__":
    if collection.count_documents({}) == 0:
        load_initial_data()
        create_indices()
