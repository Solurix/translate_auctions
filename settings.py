import os

EMAIL = str(os.getenv("EMAIL"))
PASSWORD = str(os.getenv("PASSWORD"))
SMTP_SERVER = str(os.getenv("SMTP_SERVER"))
EMAIL_TO = eval(os.getenv("EMAIL_TO"))
EMAIL_FROM = EMAIL
PASSWORD_FROM = PASSWORD
FETCH_TIME = 24 * 3600 # fetch mails that are no older than this value (seconds)
FETCH_LABEL = "Aukcje" # label from which to fetch emails
DEST_LANGUAGE = "en"
DEST_CURRENCY = "PLN"