"""
Remote Procedure Call Module
============================

:Author: Juti Noppornpitak
:Status: Stable/Testing
:Last Update: |today|
"""

import json
import time

from tori.data.serializer   import ArraySerializer
from tori.socket.websocket import WebSocket

class UncallableException(RuntimeError): pass

class Remote(object):
    """ RPC Request

    :param method:  the name of the method
    :type  method:  str
    :param id:      the request ID (default with unix timestamp)
    :param data:    method parameters
    :type  data:    dict
    :param service: the ID of the registered component/service (optional)
    :type  service: str
    """
    def __init__(self, method, id=None, data=None, service=None):
        self.id      = id or time.time()
        self.data    = data or None
        self.method  = method
        self.service = service or None

    def call(self):
        """ Execute the request

        :return: the result of the execution
        """
        remote_call = self.service.__getattribute__(self.method)

        if not callable(remote_call):
            raise UncallableException('The request method is not callable.')

        return remote_call(**self.data) if self.data else remote_call

class Response(object):
    """ RPC Response

    :param result: the result from RPC
    :param id: the response ID
    """
    def __init__(self, result, id):
        self.id     = id
        self.result = result

class ErrorResponse(object):
    def __init__(self, reason, description, feedback):
        self.reason      = reason
        self.description = description
        self.feedback    = feedback

class Interface(WebSocket):
    """ Remote Interface

    Extends from :class:`tori.socket.websocket.WebSocket`
    """

    def on_message(self, message):
        """
        :type message: str or unicode

        The parameter ``message`` is supposed to be in JSON format:

        .. code-block:: javascript

            {
                ["id":      unique_id,]
                ["service": service_name,]
                ["data":    parameter_object,]
                "method":  method_name
            }

        When the service is not specified, the interface will act as a service.

        """

        data     = json.loads(message)
        remote   = Remote(**data)
        response = None

        if remote.service:
            remote.service = self.component(remote.service)
        else:
            remote.service = self

        try:
            response = Response(remote.call(), remote.id)
        except AttributeError as e:
            response = ErrorResponse('The method does not exist.', str(e), data)

        simplified_response = ArraySerializer.instance().encode(response)
        simplified_response.update({
            'service': data['service'],
            'method':  data['method']
        })

        self.write_message(
            json.dumps(simplified_response)
        )
