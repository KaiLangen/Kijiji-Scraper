import email
import imaplib
from bs4 import BeautifulSoup

import KScraper as ks

user = 'kijiji.adserver1234@gmail.com'
passwd = 'sirchickendigby'
smtp_server = 'imap.gmail.com'
smtp_port = 993

def submit_scrape_request(msg):
    # extract the email sender info
    #email_from = msg['from']
    #print('From : ' + email_from + '\n')

    # extract the email body and turn it into a dict
    if msg.is_multipart():
        for payload in msg.get_payload():
            if payload.get_content_type() == "text/html":
                body = payload.get_payload(decode=True)
    else:
        body = msg.get_payload(decode=True)
    soup = BeautifulSoup(body, "html.parser")
    url = soup.find('a').get('href')

    request = {}
    for line in soup.findAll(text=True):
        for line2 in line.strip().split("\n"):
            if line and ':' in line:
                typ,data = line.split(':')
                request[typ.lower()] = data

    exclude_list = request["exclude"].split(',')

    # remove trailing spaces
    exclude_list = list(map(lambda x: x.strip(' '), exclude_list))
    print(exclude_list)
    print(request['delay'])
    ks.scrape(url, {}, exclude_list, "test_file.txt")


def read_email_from_gmail():
    mail = imaplib.IMAP4_SSL(smtp_server)
    mail.login(user, passwd)
    mail.select('Inbox')

    typ, msg_ids = mail.search(None, 'ALL')
    if typ != 'OK':
        print("No emails found!")
        return

    for num in msg_ids[0].split():
        typ, data = mail.fetch(num, '(RFC822)' )

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject = msg['subject']
                # only check emails with the right subjects
                if "new request" in email_subject:
                    submit_scrape_request(msg)


read_email_from_gmail()
