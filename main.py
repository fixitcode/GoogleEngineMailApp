#Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITiIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import webapp2
import sendgrid
import json

from sendgrid.helpers import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

import email
from email.utils import parseaddr
from email.parser import Parser 
from google.appengine.api import mail as g_mail
from StringIO import StringIO
import base64
import sys

SENDGRID_API_KEY ='REPLACE_WITH_SENDGRID_API'
SENDGRID_SENDER ='REPLACE_WITH_SENDGRID_SENDER'

event_dict ={}


def create_template():
	sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
	
	data = {   
  		  "name": "sender_name", 
  	          "plain_content": "This is a template mail", 
                  "subject": "test mail"
	}
	response = sg.client.templates.post(request_body=data)
	print("template create status",response.status_code)
	print ("***************************")
	print("template create body",response.body)
	print ("***************************")
	print("template craete headers",response.headers)
	

def get_template():

# Retrieve all transactional templates. 
# GET /templates #
	
	sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
	response = sg.client.templates.get()
	print("Get Template statuts",response.status_code)
	print ("***************************")
	print("Get templaate bdy ",response.body)
	print ("***************************")
	print("get template headers",response.headers)

def send_simple_message(recipient):
	sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
	to_email = mail.Email(recipient)
	from_email = mail.Email(SENDGRID_SENDER)
	subject = 'This is a test email'
	content = mail.Content('text/plain', 'Example sendgrid message.')
	message = mail.Mail(from_email, subject, to_email, content)
	message.template_id='b9bcf210-ed49-416c-8bed-f70b0f831693'
        logging.info("send_simple_message before ")
	try:
		response = sg.client.mail.send.post(request_body=message.get())
	except:
		print("Received Exception, exoiting()")
		exit()
        logging.info("send_simple_message after")
	print ("***************************")
        logging.info("%s",response.status_code)
	print ("***************************")
        logging.info("%s",response.headers)
	print ("***************************")
	return response



class SendEmailHandler(webapp2.RequestHandler):
    	def post(self):
        	recipient = self.request.get('recipient')
		if (recipient == ''):
			logging.info("Post request body:%s" ,self.request.body)
			parsed_body=json.loads(self.request.body)
			logging.info("Recipient %s:",parsed_body['recipient'])
        		sg_response = send_simple_message(parsed_body['recipient'])
		else:
        		sg_response = send_simple_message(recipient)
		logging.info(" Send response message id %s",sg_response.headers['x-message-id'])
        	self.response.content_type = 'text/html'
        	self.response.write("""
        	<!doctype html>
        	<html><body>
        	<form action="/track" method="GET">
		Your message id is:
		 """+sg_response.headers['x-message-id']+"""
		<input type="hidden" name="mid" value= """+sg_response.headers['x-message-id']+""">
        	<input type="submit" name="submit" value="Track mail status">
        	</form>
        	</body></html>
        	""")
        	#self.response.set_status(sg_response.status_code)
        	#self.response.write(sg_response.body)
	

class TrackEmailStatusHandler(webapp2.RequestHandler):
	def post(self):
	        self.parsed_body = json.loads(self.request.body)
		#logging.info("Track LOG Parsed Body Attribute is %s: ",self.parsed_body)
		for z in self.parsed_body:
			mid_list =z['sg_message_id'].split('.')
			event_dict[mid_list[0]] = z['event']
			logging.info("Track LOG Current staus of message is %s ",event_dict)
			logging.info("Track LOG Current message id %s",mid_list[0])
    	def get(self):
        	mid = self.request.get('mid')
		logging.info("Track get message mid %s ",mid)
                try:
			logging.info("Track LOG status event dict %s ",event_dict[mid])
			status= event_dict[mid]
		except:
			status= "Sent"
        	self.response.content_type = 'text/html'
        	self.response.write("""
        	<!doctype html>
        	<html><body>
        	<label for "status">Current Mail Status is</label> """+ status +"""
		<br>Press back to check recent status update
        	</body></html>
        	""")


def parse_attachment(message_part):
    logging.info("Parse recieved attachments")
    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        print("Parse attachments :content disposition")
	if ("attachment" in content_disposition) and ( "filename" in content_disposition):
          dispositions = content_disposition.strip().split(";")
          content_lst= [content for content in dispositions if "attachment" in content]
          if content_lst:
	     
    	    print("Parse attachments :content is attachmnet")
    	    logging.info("-----------Parse attachments :- content is attachment------- --")
            file_data = message_part.get_payload(decode=True)
            attachment = {}
            attachment['type'] = message_part.get_content_type()
            attachment['size'] = len(file_data)
            attachment['name'] = None
	    try:
	    	attachment['contents']= base64.b64encode(file_data)
	    except :
		print("Not able to decode attacmnet body")
		attachment['contents']=None

            for param in dispositions[1:]:
    	        print("Parse attachments :param",param)
                name,value = param.split("=")
                name = name.lower()

                if name == "filename":
                    attachment['name'] = value
    	            print("Parse attachments:filename",value)
            return attachment

    return None

def parse(content):
    #p = EmailParser()
    msgobj = Parser().parsestr(content)
    logging.info("-----------Receive Message type--------- --%s" ,type(msgobj))
    #logging.info("-----------Receive subject--------- --%s", msgobj['subject'])
    #msgobj = p.parsestr(content)
    if msgobj['Subject'] is not None:
    	logging.info("-----------Receive subject decode--------- --%s", msgobj['subject'])
        '''decodefrag = decode_header(msgobj['Subject'])
        subj_fragments = []
        for s , enc in decodefrag:
            if enc:
                s = unicode(s , enc).encode('utf8','replace')
            subj_fragments.append(s)
        subject = ''.join(subj_fragments)'''
	subject= msgobj['Subject']
    else:
        subject = None
    sender= None
    attachments = []
    body = None
    html = None
    to= None
    text =None
    i=0
    for part in msgobj.walk():
	print("*******Parse msgonj.walk************")
    	logging.info("-----------Receive subject while msgwalk------- --%s", part['Subject'])
	payload = part.get_payload()
    	logging.info("-----------Receive part Content type--------- --%s", part.get_content_type())
    	logging.info("-----------Receive part items--------- --%s", part.items())
	token_list= part.items()
	part_hdr = token_list[0][1].split(';')
	if 'name="subject"' in (part_hdr[1]):
		subject = payload.strip()
		logging.info("-----------Receive SUBJECT in part payload --------- --%s", payload.strip())
	if 'name="from"' in (part_hdr[1]):
		sender = payload.strip()
		logging.info("-----------Receive FROM in part payload --------- --%s", payload.strip())
	if 'name="to"' in (part_hdr[1]):
		to=payload.strip()
		logging.info("-----------Receive TO in part payload --------- --%s", payload.strip())
	if 'name="text"' in (part_hdr[1]):
		text=payload.strip()
		logging.info("-----------Receive Text in part payload --------- --%s", payload.strip())
    	logging.info("-----------Receive part payload --------- --%s", part.get_payload())
	if (i==0 and payload):
		logging.info("-----------Receive type of  part payload --------- --%s", type(payload))
    		logging.info("-----------Receive part payload 0  --------- --%s ", payload[0])
		'''for item in payload:
    			logging.info("-----------Receive content in part payload lopp--------- --%s", item.get_content_type())
			if item['name']=="subject":
				 logging.info("-----------Receive subject in part payload loop--------- --%s", item.get_payload())
			if item['name']=="from":
				 logging.info("-----------Receive from in part payload loop--------- --%s", item.get_payload())'''
	i+=1	
        attachment = parse_attachment(part)
        if attachment:
            attachments.append(attachment)
	
    return {
        'subject' : subject,
        'from' : sender,
        'to' : to, 
	'text' : text,
        'attachments': attachments,
    }


class ReceiveEmailHandler(webapp2.RequestHandler):
	def post(self):
		logging.info("ReceiveEmailHandler: parsing the received body ")
        	try:
			content_type = self.request.headers["Content-Type"]
        	except :
                	logging.info("Received error while parsing Content type, Mail format not recognized")
                	exit()
        	# Attach content-type header to body so that email library can decode it correctly
        	message = "Content-Type: " + self.request.headers["Content-Type"] + "\r\n"
        	message += self.request.body
		
		parsed_mail = parse(message)
		'''
		# Below functionality handles forwarding received mail
		#Currently for testing , forwaded mail to the sender itself.
		# TO DO: Providing GUI to see inbox and select sender for mail forwarding
		'''
		if parsed_mail:

        		sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        		to_email = mail.Email(parsed_mail['from'])
        		from_email = mail.Email(parsed_mail['to'])
        		subject = parsed_mail['subject']
        		content = mail.Content('text/plain', parsed_mail['text'])
        		message = mail.Mail(from_email, subject, to_email, content)
        		try:
                		response = sg.client.mail.send.post(request_body=message.get())
        		except :
                		logging.info("Received error while forwarding email, exiting")
                	else:
		   		logging.info("%s",response.status_code)
        			logging.info("%s",response.headers)

class MainPage(webapp2.RequestHandler):
    	def get(self):
        	self.response.content_type = 'text/html'
        	self.response.write("""
        	<!doctype html>
        	<html><body>
        	<form action="/send" method="POST">
        	<input type="text" name="recipient" placeholder="Enter recipient email">
        	<input type="submit" name="submit" value="Send simple email">
        	</form>
        	</body></html>
        	""")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/send', SendEmailHandler),
    ('/track',TrackEmailStatusHandler),
    ('/receive',ReceiveEmailHandler)
], debug=True)

