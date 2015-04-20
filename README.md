# MessageMedia Python SDK
This library provides a simple interface for sending and receiving messages using the [MessageMedia SOAP API](http://www.messagemedia.com.au/wp-content/uploads/2013/05/MessageMedia_Messaging_Web_Service.pdf?eacfbb).

If you have any issue using this sample code, or would like to report a defect, you could [create a new Issue](https://github.com/messagemedia/messagemedia-python/issues/new) in Github or [Contact us](http://www.messagemedia.com.au/contact-us).

## Installation
Install the `mmsoap` package via pip from Github:

    pip install -e git://github.com/messagemedia/messagemedia-python.git#egg=mmsoap-dev

The `mmsoap` package requires `suds` (0.4) for SOAP interactions. `suds` v0.4.1 and later may not function
correctly with this code.

## Usage
    import mmsoap

    client = mmsoap.MMSoapClient("your-userId", "your-password")
    client.send_messages(["+61412345689"], "Hello from MMSoap.py!")

For a more in-depth example, look at `sample.py`.

## Contributing
We welcome contributions from our users. Contributing is easy:

  1.  Fork this repo
  2.  Create your feature branch (`git checkout -b my-new-feature`)
  3.  Commit your changes (`git commit -am 'Add some feature'`)
  4.  Push to the branch (`git push origin my-new-feature`)
  5.  Create a Pull Request
