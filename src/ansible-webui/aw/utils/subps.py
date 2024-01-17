import subprocess

from aw.settings import BASE_DIR


def process(cmd: list, timeout_sec: int = None, shell: bool = False) -> dict:
    try:
        with subprocess.Popen(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR,
        ) as p:
            b_stdout, b_stderr = p.communicate(timeout=timeout_sec)
            stdout, stderr, rc = b_stdout.decode('utf-8').strip(), b_stderr.decode('utf-8').strip(), p.returncode

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, subprocess.CalledProcessError,
            OSError, IOError) as error:
        stdout, stderr, rc = None, str(error), 1

    return dict(
        stdout=stdout,
        stderr=stderr,
        rc=rc,
    )
