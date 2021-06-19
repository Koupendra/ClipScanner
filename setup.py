import requests, json, sqlite3, time

def api_validator(api):
    headers = {'API-Key': api,'Content-Type':'application/json'}
    data = {"url": "google.com", "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers, data=json.dumps(data)).json()
    if response['message'] == "API key supplied but not found in database!":
        return False
    return True

print("="*30)
print("Welcome to ClipScanner Setup")
print("="*30)
print()
print("To use Clip Scanner, you need to have an API Key from urlscan.io.")
print("If you are not sure how to get one, we'll guide you to get one.\n")
while True:
    print()
    print("1. Tutorial on how to get API Key")
    print("2. Enter API Key")
    print("3. Repair files and also erase local database")
    print("4. Repair file(s) without erasing local database")
    print("5. Exit Setup :(")
    user = input("Enter Option: ")

    if user == "5":
        print("We're sorry to see you leave. Have a nice day!")
        exit()
    if user in ["2","3","4"]:
        user_api = input("Key: ")
        if api_validator(user_api):
            if user != "4":
                conn = sqlite3.connect("local.db")
                cursor = conn.cursor()
                cursor.execute("""CREATE TABLE websites (site TEXT NOT NULL, malicious INTEGER NOT NULL);""")
                conn.commit()
                conn.close()
            break
        else:
            print("You've entered an Invalid API Key. Please try again! Check tutorial if you are unsure on how to get an API Key.")
            continue
        
    else:
        print("----- Tutorial -----")
        print("Press any key to continue after each step")
        print("Step 1: Visit https://urlscan.io/user/login/")
        input()
        print("Step 2: If you have an account, login, else create one.")
        input()
        print("Step 3: After login, head to https://urlscan.io/user/apikey/new/")
        input()
        print("Step 4: Provide a description of your choice and create a API Key")
        input()
        print("Step 5: You will automatically be redirected to https://urlscan.io/user/profile/")
        print("Copy the key alone (will be of the format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)")
    

with open("api","w") as f:
    f.write(str(user_api))
print()
print("SETUP SUCCESSFUL!")
print("Have a wonderful day! Exiting...")
time.sleep(3)
