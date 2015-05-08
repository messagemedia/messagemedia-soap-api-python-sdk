"""
    Copyright 2014 MessageMedia
    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License.  You may obtain a copy
    of the License at http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import suds
from cache import ExtendedObjectCache

from suds.transport.http import HttpTransport as SudsHttpTransport

from .exceptions import *


class WellBehavedHttpTransport(SudsHttpTransport):
    """
    HttpTransport which properly obeys the ``*_proxy`` environment
    variables.
    """

    def u2handlers(self):
        """Return a list of specific handlers to add.

        The urllib2 logic regarding ``build_opener(*handlers)`` is:

        - It has a list of default handlers to use

        - If a subclass or an instance of one of those default handlers is
        given in ``*handlers``, it overrides the default one.

        Suds uses a custom {'protocol': 'proxy'} mapping in self.proxy, and
        adds a ProxyHandler(self.proxy) to that list of handlers.  This
        overrides the default behaviour of urllib2, which would otherwise use
        the system configuration (environment variables on Linux, System
        Configuration on Mac OS, ...) to determine which proxies to use for the
        current protocol, and when not to use a proxy (no_proxy).

        Thus, passing an empty list will use the default ProxyHandler which
        behaves correctly.
        """
        return []


class MMSoapClient(object):
    WSDL_URL = "https://soap.m4u.com.au/?wsdl"

    def __init__(self, userId=None, password=None, **kwargs):
        object_cache = ExtendedObjectCache()
        object_cache.setduration(days=10)
        if "cache_location" in kwargs:
            object_cache.setlocation(kwargs["cache_location"])

        self.client = suds.client.Client(self.WSDL_URL,
                                         cache=object_cache,
                                         transport=WellBehavedHttpTransport())

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

    def check_user(self):
        return self.client.service.checkUser(self.authentication)\
            .accountDetails

    def send_messages(self, recipients, content, send_mode='normal'):
        """
        Send a message to `recipients`.

        Arguments:
        recipients -- iterable of recipient numbers
        content -- message content

        Keyword arguments:
        send_mode -- used for testing. One of:
            * normal (default) -- send as normal
            * dropAll -- drop (not send) the requested messages, return
              random errors and successes
            * dropAllWithErrors -- drop the requested messages,
              return errors
            * dropAllWithSuccess -- drop the requested messages,
              return success
        """
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
        message_list._sendMode = send_mode

        request_body = self.create("SendMessagesBodyType")
        request_body.messages = message_list

        response = self.client.service.sendMessages(self.authentication,
                                                    request_body)
        self.raise_for_response(response)

        return response

    def raise_for_response(self, response):
        try:
            code = response.errors[0][0]._code

            if code == 'invalidRecipient':
                raise InvalidRecipientException()
            elif code == 'recipientBlocked':
                raise RecipientBlockedException()
            elif code == 'emptyMessageContent':
                raise EmptyMessageContentException()
            elif code == 'other':
                raise OtherMMSOAPException()
            else:
                pass

        except AttributeError:
            pass

    def check_replies(self, maximum_replies=None):
        request_body = self.create("CheckRepliesBodyType")

        if maximum_replies is int and maximum_replies >= 0:
            request_body.maximumReplies = maximum_replies

        reply_response = self.client.service.checkReplies(self.authentication,
                                                          request_body).replies

        if "reply" in reply_response:
            return reply_response.reply
        else:
            return []

    def confirm_replies(self, message_receipt_ids):
        confirm_reply_list = self.create("ConfirmReplyListType")
        for receipt_id in message_receipt_ids:
            this_confirm_item = self.create("ConfirmItemType")
            this_confirm_item._receiptId = receipt_id
            confirm_reply_list.reply.append(this_confirm_item)
        request_body = self.create("ConfirmRepliesBodyType")
        request_body.replies = confirm_reply_list

        return self.client.service.confirmReplies(self.authentication,
                                                  request_body)
