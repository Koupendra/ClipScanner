import sqlite3, os, time, tldextract

print("="*40)
print("   ClipScanner Manage Local Database")
print("="*40)

if not (os.path.exists("local.db") and os.path.isfile("local.db")):
    print("File(s) Missing. Please re-run Setup")
    time.sleep(2)
    print("Exiting...")
    time.sleep(2)
    exit()
conn = sqlite3.connect("local.db")
cursor = conn.cursor()

while True:
    print()
    print("1. Add or Update Domain as Verified")
    print("2. Add or Update Domain as Blacklisted")
    print("3. Add or Update Domain as Malicious")
    print("4. Remove Domain from Database")
    print("5. Exit")
    user = input("Enter Option: ")
    if user == "5":
        break
    if user in ["1","2","3","4"]:
        url = input("Enter URL: ")
        extract = tldextract.extract(url)
        if extract.domain and extract.suffix:
            domain = extract.domain + "." + extract.suffix
        else:
            print("Inavlid URL!")
            continue

        if user == "1":
            cursor.execute("""REPLACE INTO websites (site, malicious) VALUES ("{}", {});""".format(domain, 3))
        elif user == "2":
            cursor.execute("""REPLACE INTO websites (site, malicious) VALUES ("{}", {});""".format(domain, 1))
        elif user == "3":
            cursor.execute("""REPLACE INTO websites (site, malicious) VALUES ("{}", {});""".format(domain, 2))
        elif user == "4":
            cursor.execute("""DELETE FROM websites WHERE site = "{}";""".format(domain))      
    
        print("Database Updated Successfully!")
        time.sleep(1)
conn.commit()
conn.close()
print("Exiting...")
time.sleep(3)
