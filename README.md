messagemedia-python
===================

Sample Python code demonstrating how to interact with the MessageMedia SOAP API.

The `mmsoap` package requires `suds` for SOAP interactions.

How to send messages:

    import mmsoap

    client = mmsoap.MMSoapClient("your-userId", "your-password")
    client.send_messages(["+61412345689"], "Hello from MMSoap.py!")

It's that simple! For a more in-depth example, look at `sample.py`.