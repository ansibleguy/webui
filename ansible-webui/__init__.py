#!/usr/bin/env python3


if __name__ == '__main__':
    from multiprocessing import cpu_count
    from platform import uname

    from gunicorn.app.wsgiapp import WSGIApplication

    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')


    class StandaloneApplication(WSGIApplication):
        def __init__(self, app_uri, options=None):
            self.options = options or {}
            self.app_uri = app_uri
            super().__init__()

        def load_config(self):
            config = {
                key: value
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            }
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

    # https://docs.gunicorn.org/en/stable/settings.html
    options = {
        'bind': '127.0.0.1:8000',
        'workers': (cpu_count() * 2) + 1,
        'reload': False,
        'loglevel': 'warning',
    }
    StandaloneApplication("aw.main:app", options).run()
