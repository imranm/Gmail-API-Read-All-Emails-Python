# Gmail API - Export all mail messages into CSV

By default API fetch only 100 messages in single request and they have provided limit of max 500 messages for single request. So, this script will help to fetch mail messages more than 500 or all emails.

* Python version 3.6.0
* To turn on the Gmail API follow instruction mentioned on [Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
* Use [this wizard](https://console.developers.google.com/flows/enableapi?apiid=gmail) to create or select a project in the Google Developers Console and automatically turn on the API.
* Put the client_secret.json credentials file (downloaded from Google Developers Console) in the same directory
* Execute gmail_export_all_emails.py
* Script will generate new .csv file in same directory.
* Exported CSV file contain headers DateTime, Subject, Body
* You can manupulate this script as per your requirement (adding new fields in export or importing this date in DB or sniffing emails of specific pattern)

[Python script](https://raw.githubusercontent.com/imranm/Gmail-API-Read-All-Emails-Python/master/gmail_export_all_emails.py)
