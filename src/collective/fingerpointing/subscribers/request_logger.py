# -*- coding: utf-8 -*-
from collective.fingerpointing.config import AUDIT_MESSAGE
from collective.fingerpointing.interfaces import IFingerPointingSettings
from collective.fingerpointing.logger import log_info
from collective.fingerpointing.utils import get_request_information
from plone import api
from plone.api.exc import InvalidParameterError
from zope.component import adapter
from zope.component import ComponentLookupError
from ZPublisher.interfaces import IPubEnd


LOGGED_CONTENT_TYPES = (
    'text/html',
    'application/json'
)
IGNORED_VIEW_NAMES = (
    'z3cform_validate_field',
)


@adapter(IPubEnd)
def request_logger(event):
    """Log content type life cycle events like object creation,
    modification and removal.
    """
    # subscriber is registered even if package has not yet been installed
    # ignore any error caused by missing registry records
    try:
        record = IFingerPointingSettings.__identifier__ + '.audit_requests'
        audit_request = api.portal.get_registry_record(record)
    except (ComponentLookupError, InvalidParameterError):
        return

    if audit_request:
        req = event.request
        user, ip = get_request_information(req)

        # depending on if legit user object or anon object, this is diff
        user_id = user
        try:
            user_id = user.name
        except AttributeError:
            try:
                user_id = user.getId()
            except AttributeError:
                pass

        if user_id in ('test', 'Anonymous User'):
            return

        ct = req.response.headers.get('content-type', '').split(';')[0]
        if ct not in LOGGED_CONTENT_TYPES:
            return

        try:
            if req.PUBLISHED.__name__ in IGNORED_VIEW_NAMES:
                return
        except (AttributeError, KeyError):
            pass

        url = req.ACTUAL_URL
        if req.environ.get('QUERY_STRING'):
            url += '?' + req.environ.get('QUERY_STRING')

        extras = 'url={0} method={1}'.format(url, req.REQUEST_METHOD)
        log_info(AUDIT_MESSAGE.format(user, ip, 'request', extras))
