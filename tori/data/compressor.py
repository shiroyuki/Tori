from re import search, sub, split

from tori.data.base import ResourceServiceMiddleware

class CSSCompressor(ResourceServiceMiddleware):
    def __init__(self):
        ResourceServiceMiddleware.__init__(self, 'text/css')

    def execute(self, data):
        content = sub('\n+', ' ', data.content)

        # Get rid of comment blocks
        raw_blocks = split('\*\/', content)
        blocks     = [sub('\/\*.*$', '', block) for block in raw_blocks]
        content    = (''.join(blocks)).strip()

        # Get rid of unnecessary whitespaces per line.
        lines     = []
        raw_lines = split('\n', content)

        for line in raw_lines:
            line = line.strip()

            lines.append(line)

        content = ' '.join(lines)

        # Get rid of unnecessary whitespaces as a whole.
        content = sub('\s*>\s*', ' > ', content)
        content = sub('\s*\+\s*', ' + ', content)
        content = sub('\s*~\s*', ' ~ ', content)
        content = sub('\s*:\s*', ':', content)
        content = sub('\s*;\s*', ';', content)
        content = sub('\s*\{\s*', '{', content)
        content = sub('\s*\}\s*', '}', content)
        content = sub('\s*,\s*', ',', content)
        content = sub(' +', ' ', content)

        data.content = content

        return data