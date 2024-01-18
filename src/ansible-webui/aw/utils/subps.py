import subprocess

from aw.settings import BASE_DIR
from aw.utils.debug import log


def process(cmd: list, timeout_sec: int = None, shell: bool = False) -> dict:
    log(msg=f"Executing command: '{' '.join(cmd)}'", level=6)

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

    return {
        'stdout': stdout,
        'stderr': stderr,
        'rc': rc,
    }
