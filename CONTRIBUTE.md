# Contribute

## Install

### Directly

```bash
# download
git clone https://github.com/ansibleguy/ansible-webui

# install dependencies (venv recommended)
cd ansible-webui
python3 -m pip install --upgrade requirements.txt
bash scripts/update_version.sh

# run
python3 src/ansible-webui/
```

### Using Docker

```bash
docker image pull ansible0guy/ansible-webui:dev
cd ${PATH_TO_SRC}  # repository root directory
docker run -it --name ansible-webui-dev --publish 127.0.0.1:8000:8000 --volume /tmp/awtest:/data --volume $(pwd):/aw ansible0guy/ansible-webui:dev
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

You are very welcome to extend the unit- & [integration-Tests](https://github.com/ansibleguy/ansible-webui/tree/latest/test/integration)!

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
