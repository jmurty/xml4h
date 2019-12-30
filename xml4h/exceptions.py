"""
Custom *xml4h* exceptions.
"""


class Xml4hException(Exception):
    """
    Base exception class for all non-standard exceptions raised by *xml4h*.
    """
    pass


class Xml4hImplementationBug(Xml4hException):
    """
    *xml4h* implementation has a bug, probably.
    """
    pass


class FeatureUnavailableException(Xml4hException):
    """
    User has attempted to use a feature that is available in some *xml4h*
    implementations/adapters, but is not available in the current one.
    """
    pass


class IncorrectArgumentTypeException(ValueError, Xml4hException):
    """
    Richer flavour of a ValueError that describes exactly what argument
    types are expected.
    """

    def __init__(self, arg, expected_types):
        msg = ('Argument %s is not one of the expected types: %s'
            % (arg, expected_types))
        super(IncorrectArgumentTypeException, self).__init__(msg)


class UnknownNamespaceException(ValueError, Xml4hException):
    """
    User has attempted to refer to an unknown or undeclared namespace by
    prefix or URI.
    """
    pass
