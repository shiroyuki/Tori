Predefined Configuration
########################

.. versionadded:: 3.0

Based on the feedback, despite of maximizing the customization, the XML
configuration schema is pretty hard to work with or remember, especially
for something important like session management and databases (MongoDB).

In version 3.0, it provides the predefined configuration (in JSON format).
Here is the sample of all available configuration.

.. code-block:: javascript

    {
        "session": {
            "class": "tori.session.InMemorySessionAdapter"
            "params": {}
        }
        "db": {
            "managers": {}
        }
    }

Database Configuration ("db")
=============================

This section currently can only tell the entity manager factory from
Passerine ORM (https://github.com/shiroyuki/passerine) to automatically
prepare for the connection to

For example, we have :file:`config.json`.

.. code-block:: javascript

    {
        "db": {
            "managers": {
                "directory": "mongodb://localhost/directory"
            }
        }
    }

Add this line to the XML configuration file.

.. code-block:: xml

    <use src="config.json"/>

And you can call the service by either::

    from tori.centre import services

    services.get('db.directory') # to get the entity manager

Session Configuration
=====================

The following are usable session adapters.

tori.session.InMemorySessionAdapter
-----------------------------------

This is the default option. This uses the process memory as a storage. **No parameters.**

tori.session.FileSessionAdapter
-------------------------------

This adapter uses a single JSON file to store session data. It writes to the file on every save.

Parameters:

:param str location: The location of the file. If the given location is a
                     relative path, the base path will be based from where the
                     main script is.

tori.session.RedisSessionAdapter
--------------------------------

This adapter uses a single JSON file to store session data. It writes to the file on every save.

:param str prefix:  The key prefix for all session entries. By default, the
                    prefix is set to **tori/session**.
:param redis_client: The redis connection client from **redis** (python package).
                     By default, it is set to a connection client bounded to
                     **localhost** without credential.
:param bool use_localhost_as_fallback: The flag to use **localhost** as a
                    fallback connection. It is set to use this feature by default.

Your own adapter?
-----------------

Just extends your adapter from :class:`tori.session.BaseSessionAdapter`