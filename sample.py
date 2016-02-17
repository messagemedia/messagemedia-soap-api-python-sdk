"""
Copyright 2014 MessageMedia
Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import mmsoap
import os
import tempfile
from datetime import datetime, timedelta

# user = 'your-userId'
# password = 'your-password'
user = 'MessageUPtyLt461'
password = 'liu@MM!'

# Create client, specifying cache_location (e.g. /tmp/mmsoap for Linux or C:/temp/mmsoap for Windows)
client = mmsoap.MMSoapClient(user, password,
                             cache_location=os.path.join(tempfile.gettempdir(), 'mmsoap'))


def check_user():
    """ Example showing the check_user function. Prints credit limit and credit remaining. """
    details = client.check_user()
    print "Credit limit: %d / Credit remaining: %d" % (details._creditLimit, details._creditRemaining)


def send_messages():
    """
    Example showing the send_messages function. Sends a single message to 1 recipient.
    Prints the resulting sent, scheduled and failed to the console.
    """
    result = client.send_messages(["+61412345671"], "Hello from messagemedia-python!")
    print "Sent %d messages, scheduled %d messages, %d messages failed" % (
        result._sent, result._scheduled, result._failed)


def check_confirm_replies():
    """
    Example showing checking and confirming of replies. Retrieves replies first via a call to check_replies
    then iterates through the result. Requests user input and confirms each individually calling confirm_replies.
    """
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
    reports = client.check_reports()

    for report in reports:
        if raw_input("Confirm report? (y/n):").lower() == "y":
            if client.confirm_replies([report._deliveryReportId])._confirmed == 1:
                print "Report confirmed."
            else:
                print "Report could not be confirmed."


def delete_scheduled_messages():
    """
    Example showing delete scheduled message functionality. First it creates a message with a future scheduled date
    and a message sequenceNumber. This is used as the id on a request to delete_scheduled_messages.
    Prints results to the console.
    """
    # first schedule a message
    seq = 1
    now = datetime.utcnow()
    scheduled = now + timedelta(weeks=1)
    result = client.send_messages(["+61412345671"], "Hello from messagemedia-python!", scheduled=scheduled, id=seq)
    print 'Sent: %d, scheduled: %d, failed: %d' % (result._sent, result._scheduled, result._failed)

    # now remove it
    print 'Deleting scheduled:', seq
    result = client.delete_scheduled_messages([seq])
    print 'Unscheduled: %d' % (result._unscheduled)


def block_numbers():
    """ Example code showing block numbers functionality. Prints number of blocked and failed to the console. """
    result = client.block_numbers(["+61412345678"])
    print 'Blocked: %d, failed: %d' % (result._blocked, result._failed)


def get_blocked_numbers():
    """
    Example code showing the get blocked numbers functionality. First makes a call to block a number then
    retrieves the list of all currently blocked and prints it to the console.
    """
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
    # block some numbers
    recipients = ["+61412345678", "+61412345676", "+61412345675"]
    result = client.block_numbers(recipients)
    print 'Blocked: %d, failed: %d' % (result._blocked, result._failed)

    # unblock the first item only
    recipient = recipients[0]
    print 'Unblocking:', recipient
    result = client.unblock_numbers(recipient)
    print 'Unblocked: %d, failed: %d' % (result._unblocked, result._failed)

    # check the remaining blocked numbers
    blocked = client.get_blocked_numbers()
    for recipient in blocked:
        print 'Remaining blocked:', recipient.value


if __name__ == '__main__':
    print '\nRunning SOAP Client Samples'

    print '\nChecking user'
    check_user()

    print '\nSending messages'
    send_messages()

    print '\nChecking & confirming replies'
    check_confirm_replies()

    print '\nChecking & confirming reports'
    check_confirm_reports()

    print '\nDeleting scheduled messages'
    delete_scheduled_messages()

    print '\nBlocking numbers'
    block_numbers()

    print '\nGetting blocked numbers'
    get_blocked_numbers()

    print '\nUnblocking numbers'
    unblock_numbers()
