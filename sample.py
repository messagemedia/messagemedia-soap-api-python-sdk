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

# Create client, specifying cache_location (e.g. /tmp/mmsoap for Linux or C:/temp/mmsoap for Windows)
client = mmsoap.MMSoapClient("your-userId", "your-password", cache_location=os.path.join(tempfile.gettempdir(), 'mmsoap'))

# Check the user
print "Check User"
details = client.check_user()
print "Credit limit: %d / Credit remaining: %d" % (details._creditLimit, details._creditRemaining)

# Send messages
print "Send Messages"
result = client.send_messages(["+61412345678"], "Hello from messagemedia-python!")
print "Sent %d messages, scheduled %d messages, %d messages failed" % (result._sent, result._scheduled, result._failed)

# Check for replies
print "Replies"
replies = client.check_replies()

for reply in replies:
    print reply.content
    if raw_input("Confirm reply? (y/N): ").lower() == "y":
        if client.confirm_replies([reply._receiptId])._confirmed == 1:
            print "Reply confirmed."
        else:
            print "Reply could not be confirmed."
