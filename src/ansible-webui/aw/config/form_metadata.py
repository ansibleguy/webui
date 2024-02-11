from aw.config.main import config

FORM_LABEL = {
    'jobs': {
        'manage': {
            'environment_vars': 'Environmental Variables',
            'mode_diff': 'Diff Mode',
            'mode_check': 'Check Mode (Try Run)',
            'cmd_args': 'Commandline Arguments',
            'user_credentials': 'User Credentials',
            'enabled': 'Schedule Enabled',
            'tags_skip': 'Skip Tags',
            'credentials_needed': 'Needs Credentials',
            'credentials_default': 'Default Job Credentials',
        },
        'credentials': {
            'connect_user': 'Connect User',
            'connect_pass': 'Connect Password',
            'become_user': 'Become User',
            'become_pass': 'Become Password',
            'vault_file': 'Vault Password File',
            'vault_pass': 'Vault Password',
            'vault_id': 'Vault ID',
            'ssh_key': 'SSH Private Key',
        },
    },
    'settings': {
        'permissions': {},
    },
}

FORM_HELP = {
    'jobs': {
        'manage': {
            'playbook_file': f"Playbook to execute. Search path: '{config['path_play']}'",
            'inventory_file': 'One or multiple inventory files/directories to include for the execution. '
                              'Comma-separated list. For details see: '
                              '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/'
                              'intro_inventory.html">'
                              'Ansible Docs - Inventory</a>',
            'limit': 'Ansible inventory hosts or groups to limit the execution to.'
                     'For details see: '
                     '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html">'
                     'Ansible Docs - Limit</a>',
            'schedule': 'Schedule for running the job automatically. For format see: '
                        '<a href="https://crontab.guru/">crontab.guru</a>',
            'environment_vars': 'Environmental variables to be passed to the Ansible execution. '
                                'Comma-separated list of key-value pairs. (VAR1=TEST1,VAR2=0)',
            'cmd_args': "Additional commandline arguments to pass to 'ansible-playbook'. "
                        "Can be used to pass extra-vars",
            'tags': 'For details see: '
                    '<a href="https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html">'
                    'Ansible Docs - Tags</a>',
            'mode_check': 'For details see: '
                          '<a href="https://docs.ansible.com/ansible/2.8/user_guide/playbooks_checkmode.html">'
                          'Ansible Docs - Check Mode</a>',
            'credentials_needed': 'If the job requires credentials to be specified '
                                  '(either as default or at execution-time; '
                                  'fallback are the user-credentials of the executing user)',
            'credentials_default': 'Specify job-level default credentials to use'
        },
        'credentials': {
            'vault_file': 'Path to the file containing your vault-password',
            'vault_id': 'For details see: '
                        '<a href="https://docs.ansible.com/ansible/latest/vault_guide/'
                        'vault_managing_passwords.html">'
                        'Ansible Docs - Managing Passwords</a>',
            'ssh_key': 'Provide an unencrypted SSH private key',
        },
    },
    'settings': {
        'permissions': {},
    },
}
