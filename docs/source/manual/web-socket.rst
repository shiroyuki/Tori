Web Socket
**********

The implementation of Web Socket in Tori Framework incorporates Tornado's Web Socket Handler with Tori's cookie-based
Session Controller, which is pretty much like working with :doc:`controller`.

Here is an example.

Suppose I want to create a message-relay module

.. code-block:: python

    from council.common.handler import WSRPCInterface
    # where WSRPCInterface inherits from tori.socket.rpc.Interface

    class MathAPI(WSRPCInterface):
        def add(self, a, b):
            return a + b

Then, the client just has to send the message in JSON format.

.. code-block:: json

    {
        "id":     12345
        "method": "add"
        "data": {
            "a": 1,
            "b": 2
        }
    }

Then, the server will reply with.

.. code-block:: json

    {
        "id":     12345
        "result": 3
    }

See More
========

* :doc:`../api/socket` (Reference)