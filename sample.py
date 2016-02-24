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

import mmsoap
import os
import tempfile
from datetime import datetime, timedelta


def create_client():
    """
    Creates a SOAP client and configures cache_location (e.g. /tmp/mmsoap for Linux or C:/temp/mmsoap for Windows)
    :return: Initialised MMSoapClient
    """
    user = 'your-userId'
    password = 'your-password'

    return mmsoap.MMSoapClient(user, password, cache_location=os.path.join(tempfile.gettempdir(), 'mmsoap'))


def check_user():
    """ Example showing the check_user function. Prints credit limit and credit remaining. """
    print 'Checking user'
    client = create_client()
    details = client.check_user()

    print "Credit limit: %d / Credit remaining: %d" % (details._creditLimit, details._creditRemaining)


def send_messages():
    """
    Example showing the send_messages function. Sends a single message to 1 recipient.
    Prints the resulting sent, scheduled and failed to the console.
    """
    print 'Sending messages'
    client = create_client()
    result = client.send_messages(["+61412345671"], "Hello from messagemedia-python!")

    print "Sent %d messages, scheduled %d messages, %d messages failed" % (
        result._sent, result._scheduled, result._failed)


def check_confirm_replies():
    """
    Example showing checking and confirming of replies. Retrieves replies first via a call to check_replies
    then iterates through the result. Requests user input and confirms each individually calling confirm_replies.
    """
    print 'Checking & confirming replies'
    client = create_client()
    replies = client.check_replies()

    for reply in replies:
        if raw_input("Confirm reply? (y/n):").lower() == "y":
            if client.confirm_replies([reply._receiptId])._confirmed == 1:
                print "Reply confirmed."
            else:
                print "Reply could not be confirmed."


def check_confirm_reports():
    """
    Example showing checking and confirming of reports. Retrieves reports first via a call to check_reports
    then iterates through the result. Requests user input and confirms each individually calling confirm_reports.
    """
    print 'Checking & confirming reports'
    client = create_client()
    reports = client.check_reports()

    for report in reports:
        if raw_input("Confirm report? (y/n):").lower() == "y":
            if client.confirm_replies([report._deliveryReportId])._confirmed == 1:
                print "Report confirmed."
            else:
                print "Report could not be confirmed."


def block_numbers():
    """ Example code showing block numbers functionality. Prints number of blocked and failed to the console. """
    print 'Blocking numbers'
    client = create_client()
    result = client.block_numbers(["+61412345678"])

    print 'Blocked: %d, failed: %d' % (result._blocked, result._failed)


def get_blocked_numbers():
    """
    Example code showing the get blocked numbers functionality. First makes a call to block a number then
    retrieves the list of all currently blocked and prints it to the console.
    """
    print 'Getting blocked numbers'
    client = create_client()
    client.block_numbers(["+61412345678"])
    # will retrieve a maximum of 10 blocked numbers
    recipients = client.get_blocked_numbers(10)

    for recipient in recipients:
        print 'Blocked number:' + recipient.value


def unblock_numbers():
    """
    Example code showing the unblock numbers functionality. First makes a call to block some numbers then
    unblocks the first one. Prints the results to the console and then retrieves and prints out the remaining
    blocked numbers.
    """
    print 'Adding some blocked numbers'
    client = create_client()
    # block some numbers
    recipients = ["+61412345678", "+61412345676", "+61412345675"]
    result = client.block_numbers(recipients)

    print 'Blocked: %d, failed: %d' % (result._blocked, result._failed)

    # unblock the first item only
    recipients = recipients[:1]
    print 'Unblocking:', recipients
    result = client.unblock_numbers(recipients)

    print 'Unblocked: %d, failed: %d' % (result._unblocked, result._failed)

    # check the remaining blocked numbers
    blocked = client.get_blocked_numbers()
    for recipient in blocked:
        print 'Remaining blocked:', recipient.value


if __name__ == '__main__':
    print 'Running SOAP Client Samples'
    check_user()
    send_messages()
    check_confirm_replies()
    check_confirm_reports()
    block_numbers()
    get_blocked_numbers()
    unblock_numbers()
