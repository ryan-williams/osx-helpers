#!/usr/bin/env python
import shlex
from contextlib import contextmanager
from subprocess import PIPE, Popen

import click
from utz import process


@contextmanager
def fence(typ=None, log=print):
    log(f'```{typ or ""}')
    yield
    log('```')


@contextmanager
def details(summary=None, code=None, log=print):
    if summary:
        if code:
            raise ValueError(f'Pass `summary` xor `code`')
        log(f'<details><summary>{summary}</summary>')
    else:
        log(f'<details><summary><code>{code}</code></summary>')
    log()
    yield
    log('</details>')


COPY_BINARIES = [ 'pbcopy', 'xclip', 'clip', ]


@click.command(no_args_is_help=True)
@click.option('-C', '--no-copy', is_flag=True, help=f'Disable copying output to clipboard (normally uses first available executable from {COPY_BINARIES}')
@click.option('-f', '--fence', 'fence_level', count=True, help='Pass 0-3x to configure output style: 0x: print output lines, prepended by "# "; 1x: print a "```bash" fence block including the <command> and commented output lines; 2x: print a bash-fenced command followed by plain-fenced output lines; 3x: print a <details/> block, with command <summary/> and collapsed output lines in a plain fence.')
@click.argument('command', nargs=-1)
def main(no_copy, fence_level, command):
    lines = process.lines(*command, log=None)
    cmd_str = shlex.join(command)

    out_lines = []

    def log(line=''):
        out_lines.append(line)

    def print_commented_lines():
        for line in lines:
            log(f'# {line}')

    def print_fenced_lines():
        with fence(log=log):
            for line in lines:
                log(line)

    if not fence_level:
        print_commented_lines()
    elif fence_level == 1:
        with fence('bash', log=log):
            log(cmd_str)
            print_commented_lines()
    elif fence_level == 2:
        with fence('bash', log=log):
            log(cmd_str)
        print_fenced_lines()
    elif fence_level == 3:
        with details(code=cmd_str, log=log):
            print_fenced_lines()
    else:
        raise ValueError(f"Pass -f/--fence at most 3x")

    output = '\n'.join(out_lines)
    if not no_copy:
        copy_cmd = None
        for cmd in COPY_BINARIES:
            if process.check('which', cmd, log=None):
                copy_cmd = cmd
                break
        if copy_cmd:
            p = Popen([copy_cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
            p.communicate(input=output)
    print(output)


if __name__ == '__main__':
    main()
