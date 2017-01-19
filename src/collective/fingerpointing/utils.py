# -*- coding: utf-8 -*-
from zope.globalrequest import getRequest


def get_request_information(request=None):
    if request is None:
        request = getRequest()
    try:
        user = request['AUTHENTICATED_USER']
        ip = request['REMOTE_ADDR']
        return user, ip
    except (KeyError, TypeError):
        return 'test', '127.0.0.1'  # running tests
