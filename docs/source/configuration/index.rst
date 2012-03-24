Configuration
=============

:Author: Juti Noppornpitak

The configuration in Tori framework is written on XML. The only reason is because it is validable and flexible. It is largely 
influenced by the extensive uses of JavaBeans in Spring Framework (Java) and the lazy loading in Doctrine (PHP).

Here is the complete layout of the configution file. See the XML comment for more information.

.. code-block:: xml

    <application>
        <include src="..."/>
        <server>
            <debug>true</debug>
            <port>8000</port>
            <!--
                Custom error delegate/handler as a controller.
            
                <error>app.controller.ErrorDelegate</error>
            -->
        </server>
        <routes>
            <!-- ... -->
        </routes>
        <service><!-- ... --></service>
    </application>

Sections
--------
.. toctree::
   :maxdepth: 1
   :glob:
   
   *

=========== ================================================================= =========
Directive   Description                                                       Required
=========== ================================================================= =========
include     To include the settings from other files or modules.              0 to many
server      The settings for the built-in server.                             0 or 1
routes      The routing settings for the application. See :doc:`routing`.     0 or 1
service     The path to service configuration. See :doc:`service`.            0 to many
=========== ================================================================= =========

.. warning::
    The DTD is not available at the moment. Please follow the example and common sense.
