# Contribute

You can run the service in its development mode:

```bash
python3 -m pip install -r ${REPO}/requirements.txt

export AW_DEV=1

python3 -m ansible-webui
# OR
cd ${REPO}/ansible-webui/
python3 __init__.py
```

Run tests and lint:

```bash
python3 -m pip install -r ${REPO}/requirements.txt
python3 -m pip install -r ${REPO}/requirements_lint.txt
python3 -m pip install -r ${REPO}/requirements_test.txt

bash ${REPO}/scripts/lint.sh
bash ${REPO}/scripts/test.sh
```