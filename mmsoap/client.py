import suds
from cache import ExtendedObjectCache

class MMSoapClient:
    WSDL_URL = "https://soap.m4u.com.au/?wsdl"

    def __init__(self, userId = None, password = None, **kwargs):
        object_cache = ExtendedObjectCache()
        object_cache.setduration(days=10)
        if "cache_location" in kwargs:
            object_cache.setlocation(kwargs["cache_location"])

        self.client = suds.client.Client(self.WSDL_URL, cache=object_cache)

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

    def check_replies(self, maximumReplies = None):
        request_body = self.create("CheckRepliesBodyType")

        if maximumReplies is int and maximumReplies >= 0:
            request_body.maximumReplies = maximumReplies

        return self.client.service.checkReplies(self.authentication, request_body).replies.reply

    def confirm_replies(self, message_receipt_ids):
        confirm_reply_list = self.create("ConfirmReplyListType")
        for receipt_id in message_receipt_ids:
            this_confirm_item = self.create("ConfirmItemType")
            this_confirm_item._receiptId = receipt_id
            confirm_reply_list.reply.append(this_confirm_item)
        request_body = self.create("ConfirmRepliesBodyType")
        request_body.replies = confirm_reply_list

        return self.client.service.confirmReplies(self.authentication, request_body)