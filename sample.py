import mmsoap

client = mmsoap.MMSoapClient("your-userId", "your-password")
client.send_messages(["+61412345689"], "Hello from MMSoap.py!")