"""
Test mock for MMSOAP API
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import httplib
from mock import patch, MagicMock

from django.test import override_settings
from suds.transport import Reply


class mmmock(object):
    """
    Mocks for MessageMedia
    """

    # hook this method to mock HTTP-level requests
    SEND_METHOD = 'suds.transport.http.HttpTransport.send'

    def _reply(content):
        return Reply(httplib.OK, {}, b'''
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
            <soap:Header></soap:Header>
            <soap:Body>
        ''' + content + b'''
            </soap:Body>
        </soap:Envelope>
        ''')

    success = patch(SEND_METHOD,
                    return_value=_reply(b'''
                    <sendMessagesResponse xmlns="http://xml.m4u.com.au/2009">
                        <result sent="1" scheduled="0" failed="0">
                            <accountDetails type="daily"
                                            creditLimit="5000"
                                            creditRemaining="2500"/>
                        </result>
                    </sendMessagesResponse>
                    '''))

    bad_receiver = patch(SEND_METHOD,
                         return_value=_reply(b'''
                         <sendMessagesResponse xmlns="http://xml.m4u.com.au/2009">
                            <result sent="25" scheduled="5" failed="6">
                                <accountDetails type="daily" creditLimit="5000" creditRemaining="1500"/>
                                    <errors>
                                        <error code="invalidRecipient" sequenceNumber="3">
                                            <recipients>
                                                <recipient uid="6">ABC</recipient>
                                            </recipients>
                                        </error>
                                    </errors>
                            </result>
                        </sendMessagesResponse>
                         '''))
