Nest
****

**Nest** is a command-line script to help you quickly setup an app container. By
default, it will be installed on under ``/usr/local/bin`` for most of the system.
Run ``nest -h`` for more information.

.. versionadded:: 2.1.2

    The option ``--dry-run`` is added to prevent the command from performing
    any write operations, including running :command:`pip`.

.. deprecated:: 2.1.2

    The prompt for UI library installation is removed in flavour to other package
    managers or any automation scripts like **puppet** and **chef**.

.. warning::

    Nest only works on Python 2.6 and 2.7. It would be fixed in the future release.