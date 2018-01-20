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
exip = u.externalipaddress()
print 'external ip address:', exip
# Email you want to send the update from (only works with gmail)
fromEmail = 'email@gmail.com'
# You can generate an app password here to avoid storing your password in plain text
# https://support.google.com/accounts/answer/185833?hl=en
fromEmailPassword = 'password'

# Email you want to send the update to
toEmail = 'email2@gmail.com'

def sendEmail(image):
	msgRoot = MIMEMultipart()
	timestamp = lt.now()
	ts = timestamp.strftime("%Y-%m-%d_%H-%M")
	msgRoot['Subject'] = 'Security Update '+ts
	msgRoot['From'] = fromEmail
	msgRoot['To'] = toEmail
	msgRoot.preamble = 'Raspberry pi security camera update'
	
	plain_text_message = "Link to view live: http://{}:5000".format(exip)
	html_message = """\
	<html>
	  <head></head>
	  <body>
	    <p>
	       <a href="http://{}:5000">Click here to view live</a>
	    </p>
	  </body>
	</html>
	""".format(exip)
	part1 = MIMEText(plain_text_message,'plain')
	part2 = MIMEText(html_message,'html')
	msgRoot.attach(part1)
	msgRoot.attach(part2)
	msgImage = MIMEImage(image,name="Pi_footage_{}.jpeg".format(ts))
	msgRoot.attach(msgImage)

	smtp = smtplib.SMTP('smtp.gmail.com', 587)
	smtp.starttls()
	smtp.login(fromEmail, fromEmailPassword)
	smtp.sendmail(fromEmail, toEmail, msgRoot.as_string())
	smtp.quit()
