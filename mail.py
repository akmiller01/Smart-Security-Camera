import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from localtime import LocalTime
# import miniupnpc
import json
import requests

conf = json.load(open("mail_conf.json"))
lt = LocalTime("Baltimore")
# u = miniupnpc.UPnP()
# u.discoverdelay = 200;
# u.discover()
# u.selectigd()
# exip = u.externalipaddress()
try:
    exip = requests.get('https://checkip.amazonaws.com').text.strip()
except requests.exceptions.ConnectionError:
    exip = "0.0.0.0"

print 'external ip address:', exip
# Email you want to send the update from (only works with gmail)
fromEmail = conf["email1"]
# You can generate an app password here to avoid storing your password in plain text
# https://support.google.com/accounts/answer/185833?hl=en
fromEmailPassword = conf["email1password"]

# Email you want to send the update to
toEmail = conf["email2"]

def sendEmail(image):
        msgRoot = MIMEMultipart('related')
        timestamp = lt.now()
        ts = timestamp.strftime("%Y-%m-%d %I:%M")
        msgRoot['Subject'] = 'Security Update '+ts
        msgRoot['From'] = fromEmail
        msgRoot['To'] = toEmail
        msgRoot.preamble = 'Raspberry pi security camera update'
        
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
                
        plain_text_message = "Link to view live: http://{}:5000".format(exip)
        html_message = """\
        <html>
          <head></head>
          <body>
            <p>
               <a href="http://{}:5000">Click here to view live</a>
            </p>
            <p>
               <img src="cid:image1">
            </p>
          </body>
        </html>
        """.format(exip)
        part1 = MIMEText(plain_text_message,'plain')
        part2 = MIMEText(html_message,'html')
        msgAlternative.attach(part1)
        msgAlternative.attach(part2)
        
        msgImage = MIMEImage(image)
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(fromEmail, fromEmailPassword)
        smtp.sendmail(fromEmail, toEmail, msgRoot.as_string())
        smtp.quit()
