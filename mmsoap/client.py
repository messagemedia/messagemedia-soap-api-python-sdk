import suds

class MMSoapClient:
    WSDL_URL = "http://soap.m4u.com.au/?wsdl"

    def __init__(self, userId = None, password = None):
        self.client = suds.client.Client(self.WSDL_URL)
        self.authentication = None
        self.authentication = self.create("AuthenticationType")
        if userId and password:
            self.authentication.userId = userId
            self.authentication.password = password

    def create(self, object_name):
        """Short-hand for creating WSDL objects."""
        return self.client.factory.create(object_name)

    def set_userId(self, userId):
        self.authentication.userId = userId

    def set_password(self, password):
        self.authentication.password = password

    def send_messages(self, recipients, content):
        recipients_type = self.create("RecipientsType")

        for recipient in recipients:
            this_recipient = self.create("RecipientType")
            this_recipient.value = recipient
            recipients_type.recipient.append(this_recipient)

        message = self.create("MessageType")
        message.recipients = recipients_type
        message.content = content

        message_list = self.create("MessageListType")
        message_list.message = [message]

        request_body = self.create("SendMessagesBodyType")
        request_body.messages = message_list

        return self.client.service.sendMessages(self.authentication, request_body)