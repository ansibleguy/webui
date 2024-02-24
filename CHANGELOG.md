# Changelog

## Version 0

### 0.0.10 / 0.0.11

**Features:**

* Git Repository support - `Jobs - Repositories` UI
* Form-Validation enhancements
  * Checking if provided file/directory exists
  * Enhanced job-file file-browsing
* Privilege System - Manager Groups
* Password-Change UI
* Docker
  * Support to [run as unprivileged user](https://webui.ansibleguy.net/en/latest/usage/docker.html#unprivileged)
  * [Image with AWS-CLI support](https://webui.ansibleguy.net/en/latest/usage/docker.html#aws-cli-support)
* Enhanced handling of [SQLite Write-Locks](https://github.com/ansibleguy/webui/issues/6)


### 0.0.9

**Features:**

* `System - Config` UI
* Support for SSH `known_hosts` file

**Fixes:**

* Dark-Mode fixes
* Multiple fixes for SSH connections

----

### 0.0.8

* Credentials
  * Global/Shared credentials
  * User-specific credentials
  * Credential permissions
* Basic Integration Tests
* Support for dockerized deployments
* Support to run behind Proxy (Nginx tested)
* Dynamic pulling of UI data using JS

----

### 0.0.7

* Job Permissions
* Job Output UI
* Refactored UI to use Ajax for dynamic Updates
* System - Environment UI

----

### 0.0.6

* Job Logs
  * Realtime following of Output
* Ability to stop running jobs
* Fixes for secret handling

----

### 0.0.5

* [Ansible-Runner](https://ansible.readthedocs.io/projects/runner/en/latest/python_interface/) integration
  * Ability to execute simple playbooks successfully
* Scheduled jobs working
* Manual job execution using UI and API working
* Job-Management UI with basic result stats
* Job-Secrets are saved encrypted

----

### 0.0.4

* Very basic job management
* Scheduler to run jobs by cron-based expressions
* Queue to process manually triggered jobs
