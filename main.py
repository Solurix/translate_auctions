from os import replace
from settings import *
import smtplib
import time
import imaplib
import email
import traceback
import sys
from email.header import Header
from email.header import decode_header, make_header
from lxml import etree
from io import StringIO
from googletrans import Translator
from email.message import EmailMessage
# import mailparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from currency_converter import CurrencyConverter
from itertools import chain
import csv
from datetime import datetime as dt, timezone
import re

def main():
    global NOW
    NOW = dt.now(timezone.utc)
    # old_emails = manage_saved_data("r")

    # Get emails from your gmail
    emails = get_new_emails(FETCH_LABEL)

    print(f"Got {len(emails)} email(s).")

    translated_emails = parse_emails(emails)
    send_email(translated_emails)



def get_new_emails(label: str) -> list:
    emails = []

    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        print(EMAIL)
        print(PASSWORD)
        mail.login(EMAIL, PASSWORD)
        mail.select(label)
        mail._mode_utf8()

        inbox_mails = mail.search(None, 'ALL')
        id_list = inbox_mails[1][0].split()

        for _id in reversed(id_list):
            data = mail.fetch(str(int(_id)), '(RFC822)')
            if data[0] == 'OK':
                # msg = email.message_from_string("".join([str(x, 'utf-8') for x in data[1][0]]))
                msg = email.message_from_string(str(data[1][0][1], 'utf-8'))
                email_date = msg['date']
                if not check_date(email_date):
                    break

                msg_dict = {
                    "id": int(_id),
                    "subject": str(make_header(decode_header(msg['subject']))),
                    "body": msg.get_payload(decode=True).decode("utf-8", "replace"),
                    "date": email_date
                }
                emails.append(msg_dict)

    except Exception as e:
        traceback.print_exc()
        print(str(e))

    return emails


def check_date(email_date):
    # change date format
    new_dt = dt.strptime(email_date[:-6], "%a, %d %b %Y %H:%M:%S %z")
    if (NOW - new_dt).total_seconds() < FETCH_TIME:
        return True
    return False


def parse_emails(_emails):
    translator = Translator()
    translated_emails = []
    cc = CurrencyConverter()
    for _email in _emails:

        translated_email = {}
        body = _email['body']
        body = re.sub(r"(?<=\d) 日", "日間", body)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(body), parser)
        def func(x): return len(x.strip()) > 2
        # Translator has some problems with "@" sign.
        # To avoid the problem below lines split strings that have it.
        texts = sorted(set([y.strip() for y in (chain.from_iterable([x.split("@") for x in filter(
            func, tree.xpath("//*/text()"))])) if func(y) and '円' not in y]), key=len, reverse=True)

        # To help with translations
        # texts = [re.sub(r"(?<=\d) 日", "日間", text) for text in texts]

        prices = set(filter(lambda x: x.strip(), tree.xpath(
            "//b[contains(text(), '円')]/text()")))

        for price in prices:
            try:
                cleaned_price = int(price.replace(",", "").replace("円", ""))
                price_in_pln = cc.convert(cleaned_price, 'JPY', DEST_CURRENCY)
                body = body.replace(price, f" {int(price_in_pln):,} {DEST_CURRENCY}")
            except Exception as e:
                print(e)

        print(f"Found {len(texts)} strings to translate.")
        for text in texts:
            try:
                translation = translator.translate(
                    text, src='ja', dest=DEST_LANGUAGE).text
                # print(text, ">", translation)
                body = body.replace(text, translation)
            except Exception as e:
                print(e)
        translated_email['body'] = body
        translated_email['subject'] = translator.translate(
            _email['subject'], src='ja', dest=DEST_LANGUAGE).text
        translated_emails.append(translated_email)
    return translated_emails


def send_email(emails):
    for email in emails:
        msg = MIMEMultipart()
        msg.attach(MIMEText(email['body'], "html", _charset="UTF-8"))
        msg['Subject'] = email['subject']
        msg['From'] = EMAIL
        msg['To'] = EMAIL_TO

        # s = smtplib.SMTP(SMTP_SERVER)
        # s.send_message(msg)
        # s.quit()

        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(EMAIL_FROM, PASSWORD_FROM)  # login with mail_id and password
        text = msg.as_string()
        session.sendmail(EMAIL, EMAIL_TO, text)
        session.quit()
        print('Mail Sent')


if __name__ == "__main__":
    main()


# def manage_saved_data(r_a, rows=[]):
#     with open("received.csv", r_a, newline='', encoding="UTF-8") as file:
#         if r_a == "r":
#             reader = csv.reader(file, delimiter=',')
#             return list(reader)
#         elif r_a == "a":
#             writer = csv.writer(file, delimiter=',')
#             for row in rows:
#                 writer.writerow(row)
