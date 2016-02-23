#
# Copyright 2014-2016 MessageMedia
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import suds
from cache import ExtendedObjectCache

from suds.transport.http import HttpTransport as SudsHttpTransport

from .exceptions import *


class MMSoapClient(object):
    """
    Message Media SOAP Client.

    This class is a wrapper for the Suds SOAP client and implements the operations
    found in the following wsdl: http://soap.m4u.com.au/?wsdl'.
    """
    WSDL_URL = "https://soap.m4u.com.au/?wsdl"

    def __init__(self, userId=None, password=None, **kwargs):
        """
        Initialise the SOAP client.

        :param userId: User ID for authenticating requests. Defaults to None.
        :param password: Password for authenticating requests. Defaults to None.
        :param kwargs: Additional arguments to set on the client. Currently only 'cache_location' is supported.
        """
        object_cache = ExtendedObjectCache()
        object_cache.setduration(days=10)
        if 'cache_location' in kwargs:
            object_cache.setlocation(kwargs["cache_location"])

        self.client = suds.client.Client(self.WSDL_URL,
                                         cache=object_cache,
                                         transport=WellBehavedHttpTransport())

        self.authentication = self.create('AuthenticationType')
        if userId and password:
            self.authentication.userId = userId
            self.authentication.password = password

    def create(self, object_name):
        """Short-hand for creating WSDL objects."""
        return self.client.factory.create(object_name)

    def set_userId(self, userId):
        """ Set user id on the authentication element. """
        self.authentication.userId = userId

    def set_password(self, password):
        """ Set password on the authentication element. """
        self.authentication.password = password

    def check_user(self):
        """
        Check user account details.

        :return: The account details including used and remaining credit limits.
        """
        return self.client.service.checkUser(self.authentication).accountDetails

    def send_messages(self, recipients, content, send_mode='normal', scheduled=None, report=None, seq=None):
        """
        Send a single message to `recipients`.

        :param recipients: Iterable of recipient numbers
        :param content: Message content
        :param send_mode: Used for testing. Should be one of:
                            * normal (default) -- send as normal.
                            * dropAll -- drop (not send) the requested messages, return a mix of errors and successes.
                            * dropAllWithErrors -- drop the requested messages, return all as errors.
                            * dropAllWithSuccess -- drop the requested messages, return all as success.
        :param scheduled: Scheduled date/time of the message in UTC format.
        :param report: Request a delivery report for this message.

        :return: Response containing count of sent, scheduled, failed and any associated error code types.
        """
        recipients_type = self.create('RecipientsType')

        for recipient in recipients:
            this_recipient = self.create('RecipientType')
            this_recipient.value = recipient
            # add uid here
            recipients_type.recipient.append(this_recipient)

        message = self.create('MessageType')
        message.recipients = recipients_type
        message.content = content

        if seq:
            message._sequenceNumber = seq

        if scheduled:
            message.scheduled = scheduled

        if report:
            message.deliveryReport = report

        message_list = self.create('MessageListType')
        message_list.message = message
        message_list._sendMode = send_mode

        request_body = self.create('SendMessagesBodyType')
        request_body.messages = message_list

        response = self.client.service.sendMessages(self.authentication, request_body)

        self.raise_for_response(response)

        return response

    def raise_for_response(self, response):
        """
        Raise an exception for a given error code in a SOAP response.

        :param response: SOAP Response containing the error code.
        :raises An exception matching the error code.
        """
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
        """
        Check replies to any sent messages.

        :param maximum_replies: Limits the number of replies returned in the response.
                                Default is to return all if this value isn't supplied.

        :return: Iterable containing the replies, never null.
        """
        request_body = self.create('CheckRepliesBodyType')

        if maximum_replies is int and maximum_replies >= 0:
            request_body.maximumReplies = maximum_replies

        response = self.client.service.checkReplies(self.authentication, request_body)
        return response.reply if 'reply' in response else []

    def confirm_replies(self, message_receipt_ids):
        """
        Confirm replies which were previously retrieved with the check_replies function.

        :param message_receipt_ids: Iterable containing the receipt id's of the replies to confirm.
                                    These must correspond to id's previously retrieved using the
                                    check_replies function.

        :return: Response containing the number of replies confirmed.
        """
        confirm_reply_list = self.create('ConfirmReplyListType')
        for receipt_id in message_receipt_ids:
            this_confirm_item = self.create('ConfirmItemType')
            this_confirm_item._receiptId = receipt_id
            confirm_reply_list.reply.append(this_confirm_item)
        request_body = self.create('ConfirmRepliesBodyType')
        request_body.replies = confirm_reply_list

        return self.client.service.confirmReplies(self.authentication, request_body)

    def check_reports(self, maximum_reports=None):
        """
        Check delivery reports to any sent messages.

        :param maximum_reports: Limits the number of reports returned in the response.
                                Default is to return all if this value isn't supplied.

        :return: Iterable containing the reports, never null.
        """
        request_body = self.create('CheckReportsBodyType')

        if maximum_reports is int and maximum_reports >= 0:
            request_body.maximumReports = maximum_reports

        response = self.client.service.checkReports(self.authentication, request_body)
        return response.report if 'report' in response else []

    def confirm_reports(self, delivery_report_ids):
        """
        Confirm reports which were previously retrieved with the check_reports function.

        :param delivery_report_ids: Iterable containing the id's of the reports to confirm.
                                    These must correspond to id's previously retrieved using the
                                    check_reports function.

        :return: Response containing the number of reports confirmed.
        """
        confirm_report_list = self.create('ConfirmReportListType')

        for report_id in delivery_report_ids:
            this_confirm_item = self.create('ConfirmItemType')
            this_confirm_item._deliveryReportd = report_id
            confirm_report_list.report.append(this_confirm_item)

        request_body = self.create('ConfirmReportsBodyType')
        request_body.reports = confirm_report_list

        return self.client.service.confirmReports(self.authentication, request_body)

    def delete_scheduled_messages(self, message_ids):
        """
        Delete scheduled messages.

        :param message_ids: Iterable of message ids to be deleted. These must correspond to message id's previously
                            used in the send_messages function where a scheduled date was set.

        :return: Response containing the count of unscheduled messages.
        """
        messages = self.create('MessageIdListType')

        for msg_id in message_ids:
            item = self.create('MessageIdType')
            item._messageId = msg_id
            messages.message.append(item)

        request_body = self.create('DeleteScheduledMessagesBodyType')
        request_body.messages = messages

        return self.client.service.deleteScheduledMessages(self.authentication, request_body)

    def block_numbers(self, numbers):
        """
        Blocks a list of numbers.

        :param numbers: Iterable of numbers to be blocked.

        :return: Count of blocked and failed.
                 If there are failures the response will contain an associate error code type
                 containing the recipient that was in error.
        """
        request = self.create_recipients_request_body('BlockNumbersBodyType', numbers)
        return self.client.service.blockNumbers(self.authentication, request)

    def get_blocked_numbers(self, maximum_numbers=None):
        """
        Retrieves currently blocked numbers.

        :param maximum_numbers: Max number of recipients to return in the response.
                                Defaults to ll items returned if this value is not supplied.

        :return: Response containing the blocked numbers, never null.
        """
        request_body = self.create('GetBlockedNumbersBodyType')

        if maximum_numbers is int and maximum_numbers >= 0:
            request_body.maximumRecipients = maximum_numbers

        response = self.client.service.getBlockedNumbers(self.authentication, request_body)
        return response.recipients.recipient if 'recipient' in response.recipients else []

    def unblock_numbers(self, numbers):
        """
        Unblocks a list of numbers.

        :param numbers: Iterable of numbers to be unblocked. The provided values must correspond
                        to those previously used in the block_numbers request.

        :return: Count of unblocked and failed. If there are failures the response will contain
                 an associate error code type containing the recipient that was in error.
        """
        request = self.create_recipients_request_body('UnblockNumbersBodyType', numbers)
        return self.client.service.unblockNumbers(self.authentication, request)

    def create_recipients(self, recipients):
        recipients_type = self.create('RecipientsType')

        for r in recipients:
            recipient_type = self.create('RecipientType')
            recipient_type.value = r
            recipients_type.recipient.append(recipient_type)

        return recipients_type

    def create_recipients_request_body(self, tag, recipients):
        """
        Create an xml element for recipients.

        :param tag: Name of the tag which will wrap the recipients.
        :param recipients: Iterable of recipients to wrap.

        :return: Created tag with the name specified in tag containing the recipients.
        """
        request_body = self.create(tag)
        request_body.recipients = self.create_recipients(recipients)
        return request_body


class WellBehavedHttpTransport(SudsHttpTransport):
    """
    HttpTransport which properly obeys the ``*_proxy`` environment
    variables.
    """

    def u2handlers(self):
        """
        Return a list of specific handlers to add.

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
