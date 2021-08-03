from credentials import *
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


def get_emails(label: str) -> list:
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select(label)

        data = mail.search(None, 'ALL')
        mail_ids = data[1]
        id_list = mail_ids[0].split()   
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        # keys_to_decode = ['Subject', 'From']
        # decoded_keys = ['Date']

        for i in range(latest_email_id,first_email_id, -1):
            data = mail.fetch(str(i), '(RFC822)' )
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1],'utf-8'))

                    msg_dict = {
                        "id": i,
                        "subject": str(make_header(decode_header(msg['subject']))),
                        "body": msg.get_payload(decode=True).decode("utf-8", "replace")
                    }
                    emails.append(msg_dict)
                    # email_subject = msg['subject']
                    # email_from = msg['from']
                    # print(str(make_header(decode_header('From : ' + email_from + '\n'))))
                    # print(str(make_header(decode_header('Subject : ' + email_subject + '\n'))))
    except Exception as e:
        traceback.print_exc() 
        print(str(e))
    
    return emails

emails = get_emails("Aukcje")
print(len(emails))

def parse_emails(_emails):
    translator = Translator()
    translated_emails = []
    for _email in _emails:
        translated_email = {}
        # body = mailparser.parse_from_string(_email['body'])
        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(_email['body']), parser)
        # texts = list(filter(None, tree.xpath("//*/text()")))
        # texts = set(filter(lambda x: x != " ", tree.xpath("//font/text() | //a/text()")))
        texts = set(filter(lambda x: x.strip(), tree.xpath("//*/text()")))
        print(f"Found {len(texts)} texts to translate.")
        body = _email['body']
        # print(texts)
        translations = [translator.translate(text, src='ja', dest='en') for text in texts]
        for text in texts:
            try:
                translation = translator.translate(text, src='ja', dest='pl').text
                # print(text, ">", translation)
                body = body.replace(text, translation)
            except Exception as e:
                print(e)
        translated_email['body'] = body
        translated_email['subject'] = translator.translate(_email['subject'], src='ja', dest='pl').text
        translated_emails.append(translated_email)
        # auctions = tree.xpath("//table[@class='mB10']")
        # print([x.text for x in translations])
        # for auction in auctions:

        # print(_email['body'])
    return translated_emails
translated_emails = parse_emails(emails)
# print(translated_emails)

emails = [{"subject": "test_subject", "body": "test_body"}]

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

        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(EMAIL, PASSWORD) #login with mail_id and password
        text = msg.as_string()
        session.sendmail(EMAIL, EMAIL_TO, text)
        session.quit()
        print('Mail Sent')


send_email(translated_emails)
# send_email(emails)