#!/usr/bin/env python3

if __name__ == '__main__':
    # pylint: disable=E0401
    from sys import argv as sys_argv
    from sys import exit as sys_exit
    from sys import path as sys_path
    from os import path as os_path

    try:
        from main import main

    except ModuleNotFoundError:
        sys_path.append(os_path.dirname(os_path.abspath(__file__)))
        from main import main

    if len(sys_argv) > 1:
        if sys_argv[1] in ['--version', '-v']:
            from cli_init import init_cli
            from cli import _print_version
            init_cli()
            _print_version()
            sys_exit(0)

    from aw.config.main import VERSION
    print(f'AnsibleGuy-WebUI Version {VERSION}')
    main()
