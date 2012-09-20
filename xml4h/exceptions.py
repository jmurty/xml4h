"""
Custom exceptions for xml4h.
"""


class XmlForHumansException(Exception):
    pass


class FeatureUnavailableException(XmlForHumansException):
    pass


class IncorrectArgumentTypeException(XmlForHumansException):

    def __init__(self, arg, expected_types):
        msg = (u'Argument %s is not one of the expected types: %s'
            % (arg, expected_types))
        super(IncorrectArgumentTypeException, self).__init__(msg)
