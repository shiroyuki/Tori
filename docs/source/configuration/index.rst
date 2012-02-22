Configuration
=============

:Author: Juti Noppornpitak

The configuration in Tori framework is written on XML. The only reason is because it is validable and flexible. It is largely 
influenced by the extensive use of Beans in Spring Framework (Java) and the lazy loading in Doctrine (PHP).


=========== =================================================================
Directive   Description
=========== =================================================================
include     To include the settings from other files or modules.
server      The settings for the built-in server.
port        The port number that the built-in server listens to the requests.
route       The routing settings for the application. See :doc:`routing`.
=========== =================================================================

.. warning::
    The DTD is not available at the moment. Please follow the example and common sense.

.. warning::
    ``include`` is not yet implemented.

.. note::
    Like a prototype in **Yotsuba** project, :class:`yotsuba.kotoba.Kotoba` is still used for parsing the XML. This will be replaced
    with the selector from **Kotoba** project.

Undocumented Configuration
--------------------------

The following is an example of supported configuration which is still undocumented.

.. code-block:: xml

    <application>
        <!-- ... -->
        <services>
            <service id="db" class="tori.service.rdb.EntityService">
                <param name="url">sqlite:///:memory:</param>
                <param name="entity_type" type="class">core.model.Log</param>
            </service>
        </services>
        <!-- ... -->
    </application>

This sample shows how to set an entity service for the entity class ``core.model.Log``.

See also
--------
.. toctree::
   :maxdepth: 1
   :glob:
   
   *