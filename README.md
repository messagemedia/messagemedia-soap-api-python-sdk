messagemedia-python
===================

Sample Python code demonstrating how to interact with the MessageMedia SOAP API.

In **sample.py:**

    import mmsoap

    client = mmsoap.MMSoapClient("your-userId", "your-password")
    client.send_messages(["+61412345689"], "Hello from MMSoap.py!")

It's that simple!