# Contribute

Contributions are very welcome!

We're also open to allow co-maintainers.

## What to contribute?

* [Find and report issues/bugs](https://github.com/ansibleguy/webui/issues/new)
* [Start Discussions about Implementations/Optimizations](https://github.com/ansibleguy/webui/discussions/new/choose)
* Help optimizing/polishing the frontend is very welcome
  * Fix/optimize styles/css
  * Extend/fix/optimize JS

* Add Unit-Tests (*pytest*)
* Add [Integration-Tests](https://github.com/ansibleguy/webui/tree/latest/test/integration) for the Web-UI and/or API

Read into the [Troubleshooting Guide](https://webui.ansibleguy.net/en/latest/usage/troubleshooting.html) to get some insight on how the stack works.

----

## Know How

* Do not commit [database migrations](https://docs.djangoproject.com/en/5.0/topics/migrations/#module-django.db.migrations) - they will be created on release.
* As we mainly use SQLite as database we should keep the DB writes to a minimum, so we do not run into locking issues (`OperationalError: database is locked`)
* Important fixes and features should be added to the CHANGELOG.md file

----

## Install

### Directly

```bash
# download
git clone https://github.com/ansibleguy/webui

# install dependencies (venv recommended)
cd ansible-webui
python3 -m pip install --upgrade -r requirements.txt
bash scripts/update_version.sh
export AW_VERSION="$(cat VERSION)"

# run
python3 src/ansibleguy-webui/
```

### Using Docker

```bash
docker image pull ansible0guy/webui:dev
cd ${PATH_TO_SRC}  # repository root directory
docker run -it --name ansible-webui-dev --publish 127.0.0.1:8000:8000 --volume /tmp/awtest:/data --volume $(pwd):/aw ansible0guy/webui:dev
```

----

## Development

You can run the service in its development mode:

```bash
bash ${REPO}/scripts/run_dev.sh
```

Run in staging mode: (*close to production behavior*)

```bash
bash ${REPO}/scripts/run_staging.sh
```

Admin user for testing:

* User: `ansible`
* Pwd: `automateMe`

----

## Testing

Test to build the app using PIP:
```bash
bash ${REPO}/scripts/run_pip_build.sh
```

Run tests and lint:

```bash
python3 -m pip install -r ${REPO}/requirements.txt
python3 -m pip install -r ${REPO}/requirements_lint.txt
python3 -m pip install -r ${REPO}/requirements_test.txt

bash ${REPO}/scripts/lint.sh
bash ${REPO}/scripts/test.sh
```
