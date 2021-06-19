import requests, json, time, pyperclip, re, tldextract, sqlite3
from win10toast import ToastNotifier

#Add Logger

def api_validator(api):
    headers = {'API-Key': api,'Content-Type':'application/json'}
    data = {"url": "google.com", "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers, data=json.dumps(data)).json()
    if response['message'] == "API key supplied but not found in database!":
        return False
    return True

def valid_url(urlToScan):
    if (not urlToScan) or (" " in urlToScan) or ("." not in urlToScan):
        return False
    flg = 0
    try:
        float(urlToScan)
        flg = 1
    except:
        pass
    if flg:
        return False
    check = re.match("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:\/?#[\]@!\$&'\(\)\*\+,;=.]+$",urlToScan)
    if check and (check[0] != urlToScan):
        return False
    return True


def domain_in_db(urlToScan,db):
    extract = tldextract.extract(urlToScan)
    domain = extract.domain + "." + extract.suffix
    connection = sqlite3.connect(db)
    #cursor = connection.cursor()
    cmd = """SELECT malicious FROM websites WHERE site = "{}";""".format(extract)
    val = connection.execute(cmd).fetchall()
    connection.close()
    if len(val)==0:
        return 0, domain
    if val[0][1]==0:
        return 1, domain
    if val[0][1]==1:
        return 2, domain


def scan(domainToAdd, db, apiKey):
    toaster.show_toast("ClipScanner","Scanning URL...Don't visit URL yet!",icon_path="search.ico",duration=5)
    headers = {'API-Key':apiKey, 'Content-Type':'application/json'}
    data = {"url": domainToAdd, "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers, data=json.dumps(data))
    connection = sqlite3.connect(db)
    if response.status_code != 200:
        if response.status_code == 400:
            toaster.show_toast("ClipScanner","Blacklisted URL! Proceed with caution!",icon_path='warning.ico',duration=7)
            cmd = """INSERT INTO websites VALUES ("{}",{});""".format(domainToAdd,1)
            connection.execute(cmd)
        else:
            print(domainToAdd)
            toaster.show_toast("ClipScanner","Warning! Invalid URL",icon_path='warning.ico',duration=5)
        connection.commit()
        connection.close()
        return

    res = response.json()

    while True:
        time.sleep(3)
        op = requests.get(res['api'])
        if op.status_code == 200:
            if 'message' in op.json().keys():
                continue    
            break
    time.sleep(3)
    
    malicious = op.json()['verdicts']['overall']['malicious']

    if malicious:
        toaster.show_toast("ClipScanner","Warning! Potential Malicious URL detected in clipboard. Proceed with caution!",icon_path='warning.ico',duration=10)
        cmd = """INSERT INTO websites VALUES ("{}",{})""".format(domainToAdd,1)
        connection.execute(cmd)
    else:
        toaster.show_toast("ClipScanner","URL verified. Good to go",icon_path="verified.ico",duration=10)
        cmd = """INSERT INTO websites VALUES ("{}",{})""".format(domainToAdd,0)
        connection.execute(cmd)
    connection.commit()
    connection.close()
        
    
prev = ""
toaster = ToastNotifier()

try:
    with open("api","r") as f:
        apiKey = f.read().strip("\n")
except:
    toaster.show_toast("ERROR!","File(s) for ClipScanner missing! Please re-run setup! Exiting...",icon_path='warning.ico',duration=15)
    exit(1)
    
if not api_validator(apiKey):
    toaster.show_toast("ERROR!","File(s) for ClipScanner corrupted! Please re-run setup! Exiting...",icon_path='warning.ico',duration=15)
    exit(1)
    
while True:
    time.sleep(0.5)
    urlToScan = pyperclip.paste()
    
    if urlToScan != prev:
        prev = urlToScan
    else:
        continue
    
    if not valid_url(urlToScan):
        continue    

    inDB, domain =  domain_in_db(urlToScan,"local.db")
    if inDB==1:
        toaster.show_toast("ClipScanner","URL verified. Good to go",icon_path="verified.ico",duration=5)
        continue
    elif inDB==2:
        toaster.show_toast("ClipScanner","Warning! Potential Malicious URL detected in clipboard. Proceed with Caution",icon_path='warning.ico',duration=5)
        continue
    scan(domain, "local.db", apiKey)
