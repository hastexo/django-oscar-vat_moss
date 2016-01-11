# vat_moss wants all input strings in Unicode. Define a helper
# function here to make this work in both Python 2 and 3.
import sys
HAVE_UNICODE_FUNCTION = (sys.version_info < (3, 0))


def u(s):
    if s is None:
        return None
    elif HAVE_UNICODE_FUNCTION:
        return unicode(s)
    else:
        return str(s)
