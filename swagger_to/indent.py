"""Re-indent the code."""
import re
import textwrap
from typing import List  # pylint: disable=unused-import

_SPACE4_RE = re.compile('^([ ]{4})+')


def reindent(text: str, level: int = 0, indention: str = ' ' * 4) -> str:
    r"""
    Strip the prefix indentation, parse indention as 4 spaces and re-indent according to ``level``.

    >>> result = reindent(text='''\
    ...     test me:
    ...         again
    ...             and again
    ...     ''', indention='|')
    >>> assert result == ('test me:\n'
    ...                   '|again\n'
    ...                   '||and again\n')

    >>> result = reindent(text='''\
    ...     test me:
    ...         again
    ...             and again
    ...     ''', level=1, indention='|')
    >>> assert result == ('|test me:\n'
    ...                   '||again\n'
    ...                   '|||and again\n')

    :param text: to be re-indented
    :param level: indention level
    :return: re-indented text
    """
    text = textwrap.dedent(text)

    lines = text.splitlines(keepends=True)
    result_lines = []  # type: List[str]
    for line in lines:
        mtch = _SPACE4_RE.match(line)
        if mtch:
            _, end = mtch.span()
            spaces = end
            assert spaces % 4 == 0, "Expected to match indention at 4 spaces, but got spaces == {}".format(spaces)

            result_lines.append(indention * int(spaces / 4 + level) + line[end:])

        else:
            result_lines.append(indention * level + line)

    return ''.join(result_lines)
