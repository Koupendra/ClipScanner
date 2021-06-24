import requests, json, time, pyperclip, re, tldextract, sqlite3, os
from win10toast import ToastNotifier

   
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
    cmd = """SELECT malicious FROM websites WHERE site = "{}";""".format(domain)
    val = connection.execute(cmd).fetchall()
    connection.close()
    if len(val)==0:
        return 0, domain
    return val[0][0], domain


def scan(domainToAdd, db, apiKey):
    toaster.show_toast("ClipScanner","Scanning URL...Don't visit URL yet!",icon_path="search.ico",duration=5)
    headers = {'API-Key':apiKey, 'Content-Type':'application/json'}
    data = {"url": domainToAdd, "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers, data=json.dumps(data))
    connection = sqlite3.connect(db)
    if response.status_code != 200:
        if response.status_code == 400:
            blacklisted_url()
            cmd = """INSERT INTO websites VALUES ("{}",{});""".format(domainToAdd,1)
            connection.execute(cmd)
        else:
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
        malicious_url()
        cmd = """INSERT INTO websites VALUES ("{}",{})""".format(domainToAdd,2)
        connection.execute(cmd)
    else:
        verified_url()
        cmd = """INSERT INTO websites VALUES ("{}",{})""".format(domainToAdd,3)
        connection.execute(cmd)
    connection.commit()
    connection.close()
        
    
prev = ""
toaster = ToastNotifier()
def blacklisted_url():
    toaster.show_toast("ClipScanner","Blacklisted URL! Proceed with caution!",icon_path='warning.ico',duration=7)
    
def malicious_url():
    toaster.show_toast("ClipScanner","Warning! Potential Malicious URL detected in clipboard. Proceed with caution!",icon_path='warning.ico',duration=10)

def verified_url():
    toaster.show_toast("ClipScanner","URL verified. Good to go",icon_path="verified.ico",duration=10)

if os.path.exists("api") and os.path.isfile("api") and os.path.exists("local.db") and os.path.isfile("local.db"):
    with open("api","r") as f:
        apiKey = f.read().strip("\n")
else:
    toaster.show_toast("ERROR!","File(s) for ClipScanner missing! Please re-run setup! Exiting...",icon_path='warning.ico',duration=15)
    exit(1)
    
if not api_validator(apiKey):
    toaster.show_toast("ERROR!","Invalid API Key! Please re-run setup! Exiting...",icon_path='warning.ico',duration=15)
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
        blacklisted_url()
        continue
    elif inDB==2:
        malicious_url()
        continue
    elif inDB==3:
        verified_url()
        continue
    scan(domain, "local.db", apiKey)
