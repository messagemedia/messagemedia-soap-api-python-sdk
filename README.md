messagemedia-python
===================

Sample Python code demonstrating how to interact with the MessageMedia SOAP API.

The `mmsoap` package requires `suds` (0.4) for SOAP interactions. `suds` v0.4.1 and later may not function
correctly with this code. To install `suds`, run

    pip install suds

How to send messages:

    import mmsoap

    client = mmsoap.MMSoapClient("your-userId", "your-password")
    client.send_messages(["+61412345689"], "Hello from MMSoap.py!")

It's that simple! For a more in-depth example, look at `sample.py`.