# -*- coding: utf-8 -*-
import argparse
import re
import sys
from imagination.decorator.validator import restrict_type
from tori.application   import Application
from tori.centre        import services
from tori.cli.exception import NotConfigured, TerminationSignal, CommandNotFound

class Console(object):
    """ Main Console

        The commands must be defined first with tag "command" and then any thing
        with prefix "command:". For example,

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

        Then, the command will be referenced with anything after ":". From the
        previous example, the command "command:db" will be referred as "db".
    """
    def __init__(self, namespace=None):
        self.namespace = namespace
        self.app       = None

    @restrict_type(Application)
    def load(self, application):
        self.app = application

    def output(self, *args):
        output = ' '.join(args)
        print(output)

    def show_console_usage(self):
        if 'command' not in services._tag_to_entity_ids:
            self.output('{} has no sub commands registered.'.format(self.namespace))
            return

        self.output('USAGE: {} <command>'.format(self.namespace or sys.argv[0]))
        self.output('\nAvailable commands:')

        # This is a hack to get the list of IDs from Imagination Framework.
        command_ids = [entity_id for entity_id in services._tag_to_entity_ids['command']]
        command_desc_map = {}
        longest_cmd_length = 0

        for command_id in command_ids:
            # This is also a hack to get the entity (metadata) of the commands.
            entity = services.get_wrapper(command_id)
            for tag in entity.tags:
                if not re.search('^command:', tag):
                    continue

                alias  = re.sub('^[^:]+:', '', tag)

                if longest_cmd_length < len(alias):
                    longest_cmd_length = len(alias)

                command_doc = entity.loader.package.__doc__ or 'Unknown command'
                command_desc_map[alias] = command_doc.strip()

        format_string = '  {:<%d}{}' % (longest_cmd_length + 4)

        for id in command_desc_map:
            self.output(format_string.format(id, command_desc_map[id]))

    def handle(self):
        if not self.app:
            raise NotConfigured('Please load the configuration first.')

        if len(sys.argv) == 1:
            self.show_console_usage()
            raise TerminationSignal('List command.')

        command_id = sys.argv[1]

        command  = None
        commands = services.find_by_tag('command:{}'.format(command_id))

        if commands:
            command = commands[0]

        if not command:
            self.show_console_usage()
            raise CommandNotFound(command_id)

        # Reconfigure the parser.
        parser         = argparse.ArgumentParser(description='Console')
        subparsers     = parser.add_subparsers()
        command_parser = subparsers.add_parser(command_id, description=command.__class__.__doc__.strip())

        command.define_arguments(command_parser)
        command.execute(parser.parse_args())