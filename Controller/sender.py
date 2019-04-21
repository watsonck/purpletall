import smtplib

sender = 'purpletall@outlook.com'
recipient = ['speedbrendan@gmail.com']

msg = """From Purple Tall <purpletall@outlook.com>
To: Cameron Haddock <cameron.haddock@live.longwood.edu> 
Subject: test email

test
"""


server = smtplib.SMTP('smtp.office365.com', 587)
server.connect('smtp.office365.com', 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login("purpletall@outlook.com", "ProjectManager8")


server.sendmail(sender, recipient, msg)
print("success")
server.quit()

    
