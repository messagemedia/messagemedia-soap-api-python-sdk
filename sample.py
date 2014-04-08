import mmsoap


# Create client, specifying cache_location (e.g. /tmp/mmsoap for Linux or C:/temp/mmsoap for Windows)
client = mmsoap.MMSoapClient("your-userId", "your-password", cache_location="C:/temp/mmsoap")

# Send messages
print "Send messages"
result = client.send_messages(["+61412345689"], "Hello from MMSoap.py!")
print "Send %d messages, scheduled %d messages, %d messages failed" % (result._sent, result._scheduled, result._failed)

# Check for replies
print "Replies:"
replies = client.check_replies()

for reply in replies:
    print reply.content
    if raw_input("Confirm reply? (y/N): ").lower() == "y":
        if client.confirm_replies([reply._receiptId])._confirmed == 1:
            print "Reply confirmed."
        else:
            print "Reply could not be confirmed."