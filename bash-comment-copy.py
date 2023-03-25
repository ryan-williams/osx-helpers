#!/usr/bin/env python
import shlex

import click
from utz import process


@click.command()
@click.option('-f', '--fence', count=True, help='Pass 0-3x to configure output style: 0x: print output lines, prepended by "# "; 1x: print a "```bash" fence block including the <command> and commented output lines; 2x: print a bash-fenced command followed by plain-fenced output lines; 3x: print a <details/> block, with command <summary/> and collapsed output lines in a plain fence.')
@click.argument('command', nargs=-1)
def main(fence, command):
    lines = process.lines(*command)
    cmd_str = shlex.join(command)

    def print_commented_lines():
        for line in lines:
            print(f'# {line}')

    def print_fenced_lines():
        print('```')
        for line in lines:
            print(line)
        print('```')

    if not fence:
        print_commented_lines()
    elif fence == 1:
        print('```bash')
        print(cmd_str)
        print_commented_lines()
        print('```')
    elif fence == 2:
        print('```bash')
        print(cmd_str)
        print('```')
        print_fenced_lines()
    elif fence == 3:
        print(f'<details><summary><code>{cmd_str}</code></summary>')
        print()
        print_fenced_lines()
        print('</details>')
    else:
        raise ValueError(f"Pass -f/--fence at most 3x")


if __name__ == '__main__':
    main()
