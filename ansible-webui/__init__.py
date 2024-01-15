#!/usr/bin/env python3

if __name__ == '__main__':
    # pylint: disable=E0401
    from sys import argv as sys_argv
    from sys import exit as sys_exit
    from main import main
    from aw.config.hardcoded import VERSION

    if len(sys_argv) > 1:
        if sys_argv[1] == 'version':
            print(VERSION)
            sys_exit(0)

    main()
