"""
Exceptions used in the MMSoapClient class
"""

class BaseMMSOAPException(Exception):
    """
    Base exception for all MMSOAP exceptions
    """

class InvalidRecipientException(BaseMMSOAPException):
    """
    Invalid Recipient
    """

class RecipientBlockedException(BaseMMSOAPException):
    """
    Recipient Blocked
    """

class EmptyMessageContentException(BaseMMSOAPException):
    """
    Empty message content
    """

class OtherMMSOAPException(BaseMMSOAPException):
    """
    Other error
    """
