import requests, json, time, pyperclip, re, tldextract, sqlite3
from win10toast import ToastNotifier

#Add Logger


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


def scan(domainToAdd, db):
    toaster.show_toast("URLScan","Scanning URL...Don't visit URL yet!",icon_path="search.ico",duration=5)
    headers = {'API-Key':'432fddc8-c4e8-4f02-b30f-3fcc0ddf3270','Content-Type':'application/json'}
    data = {"url": domainToAdd, "visibility": "public"}
    response = requests.post('https://urlscan.io/api/v1/scan/',headers=headers, data=json.dumps(data))
    connection = sqlite3.connect(db)
    #cursor = connection.cursor()
    if response.status_code != 200:
        if response.status_code == 400:
            toaster.show_toast("ClipScanner","Warning! BLACKLISTED URL! Proceed with caution!",icon_path='warning.ico',duration=7)
            cmd = """INSERT INTO websites VALUES ("{}",{});""".format(domainToAdd,1)
            connection.execute(cmd)
        else:    
            toaster.show_toast("ClipScanner","Invalid URL",icon_path='warning.ico',duration=5)
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
    scan(domain, "local.db")
