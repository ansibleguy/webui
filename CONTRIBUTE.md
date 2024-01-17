# Contribute

## Testing

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

## Migrations

Migrations should not be committed to `latest`.

They will be generated & distributed cumulated for each release.
