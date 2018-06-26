'''
This file exclusively handles the incoming mail when 
receiver email address contains google app domain
 instead of mails coming for some other domains
'''
import logging, email
import webapp2
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        print("*******LogSenderHandler *******", mail_message)
        _subject = mail_message.subject
        _sender=mail_message.sender
        logging.info("Received a message from: " + mail_message.sender)
        logging.info("Received a message from: " + mail_message.subject)
        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')

        for content_type, body in html_bodies:
        	decoded_html = body.decode()
                print("LogSenderHandler :- body ", decoded_html)
        allBodies = ""
        #for body in bodies:
        #  allBodies = allBodies + "\n---------------------------\n" + body[1].decode()
        #m= mail.EmailMessage(sender="zjm1126@gmail.com ",subject="reply to "+_subject)
        #m.to = _sender
        #m.body =allBodies
        #m.send()
        '''message = mail.EmailMessage(sender="zjm1126@gmail.com",
                                        subject="Your account has been approved")
        message.to = _sender
        message.body = 
        Dear Albert:

        Your example.com account has been approved.  You can now visit
        http://www.example.com/ and sign in using your Google Account to
        access new features.

        Please let us know if you have any questions.

        The example.com Team
        """
	'''
        



app = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
