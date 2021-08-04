import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
EMAIL_TO = eval(os.getenv("SMTP_SERVER"))
EMAIL_FROM = EMAIL
PASSWORD_FROM = PASSWORD
FETCH_TIME = 24 * 3600 # fetch mails that are no older than this value (seconds)
FETCH_LABEL = "Aukcje" # label from which to fetch emails
DEST_LANGUAGE = "en"
DEST_CURRENCY = "PLN"