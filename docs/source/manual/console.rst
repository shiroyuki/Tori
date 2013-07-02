Console and CLI Framework
*************************

.. versionadded:: 2.2

Setup
=====

Similar to how you set up a server (see :doc:`getting_started`), you need to add
:class:`tori.cli.console.Console` into the mix, for instance, we have a script
name :file:`nep`

.. code-block:: python

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    """
    Nameless Education Platform

    .. codeauthor:: Juti Noppornpitak <jnopporn@shiroyuki.com>
    """
    from tori.application import Application
    from tori.cli.console import Console
    from tori.cli.exception import TerminationSignal

    app     = Application('config/app.xml')
    console = Console('NEP')

    console.load(app);

    try:
        console.handle()
    except TerminationSignal as e:
        pass

where you can see the list of all registered commands by executing `nep`.

Configuration
=============

As commands are treated as reusable components (with Imagination Framework),
they must be defined first with tag "command" and then any thing with prefix
"command:". For example,

.. code-block:: xml

    <!-- From https://github.com/nepteam/nep -->
    <entity
        id="command.db"
        class="neptune.command.Database"
        tags="command command:db">
        <param name="db" type="entity">db</param>
        <interception before="me" do="execute" with="init"/>
        <interception after="me" do="execute" with="clean_up"/>
    </entity>

Then, the command will be referenced with anything after ":". From the previous
example, the command "command.db" will be referred as "db" and executed as::

    ./nep db -d # in this example, this command is to reset the databases.

Implement Commands
==================

Just write a class extending from :class:`tori.cli.command.Command`.

There are two methods that mush be overridden:

.. py:method:: define_arguments(argument_parser)

    Define the arguements. Override the method with the keyword `pass` if there
    is no argument to define.

    :param argument_parser: the argument parser
    :type  argument_parser: argparse.ArgumentParser

    For more information on how to define the arguments, see http://docs.python.org/3.3/library/argparse.html.

.. py:method:: execute(args)

    Execute the command.

    :param args: the arguments
    :type  args: argparse.Namespace