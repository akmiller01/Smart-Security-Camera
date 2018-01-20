import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from localtime import LocalTime
import miniupnpc

lt = LocalTime("Baltimore")
u = miniupnpc.UPnP()
u.discoverdelay = 200;
u.discover()
u.selectigd()
print 'external ip address:', u.externalipaddress()
# Email you want to send the update from (only works with gmail)
fromEmail = 'email@gmail.com'
# You can generate an app password here to avoid storing your password in plain text
# https://support.google.com/accounts/answer/185833?hl=en
fromEmailPassword = 'password'

# Email you want to send the update to
toEmail = 'email2@gmail.com'

def sendEmail(image):
	msgRoot = MIMEMultipart('related')
	timestamp = lt.now()
	ts = timestamp.strftime("%Y-%m-%d %H:%M")
	msgRoot['Subject'] = 'Security Update '+ts
	msgRoot['From'] = fromEmail
	msgRoot['To'] = toEmail
	msgRoot.preamble = 'Raspberry pi security camera update'

	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)
	msgText = MIMEText('Smart security cam found object')
	msgAlternative.attach(msgText)

	msgText = MIMEText('<a href="{}:5000">Click here to live</a><img src="cid:image1">'.format(u.externalipaddress()), 'html')
	msgAlternative.attach(msgText)

	msgImage = MIMEImage(image)
	msgImage.add_header('Content-ID', '<image1>')
	msgRoot.attach(msgImage)

	smtp = smtplib.SMTP('smtp.gmail.com', 587)
	smtp.starttls()
	smtp.login(fromEmail, fromEmailPassword)
	smtp.sendmail(fromEmail, toEmail, msgRoot.as_string())
	smtp.quit()
