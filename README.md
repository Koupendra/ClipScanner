# ClipScanner

What Is This?
-------------

This is a Python application that scans the URL in your clipboard (if URL is the only content of clipboard) using the urlscan.io API and gives appropriate notification(s) depending on scanned result of the URL. The scan results will be stored in a Local Database, so the results will be faster for same URL if being scanned again.


How To Use This?
----------------

1. Download the project.
2. Run `pip install -r requirements.txt` to install dependencies inside the project folder.
3. Run `setup.py` and complete the setup. Tutorial to generate API Key is included in setup.
4. Run `main.py` (which is the acutal application).
5. You can start this application at login by configuring your Task Scheduler.
6. You can also run `manageDB.py` to mark domains as "Blacklisted, "Malicious, or "Verified", manually, which will only affect your local database only.


NOTE
----

1. This will work only on Windows 10 as of now (I will try to extend it for Linux in future).
2. The project is still in development, so it might have bugs.
3. The URL Scan results are purely based on results from urlscan.io. I am not responsible for a website being reported as "Blacklisted", "Malicious" or "Verified".
