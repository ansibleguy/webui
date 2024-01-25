from aw.config.main import config

FORM_LABEL = {
    'jobs': {
        'manage': {
            'job': {
                'environment_vars': 'Environmental Variables',
                'mode_diff': 'Diff Mode',
                'mode_check': 'Check Mode (Try Run)',
                'vault_pass': 'Vault Password',
                'vault_file': 'Vault Password File',
                'connect_user': 'Connect User',
                'connect_pass': 'Connect Password',
                'become_user': 'Become User',
                'become_pass': 'Become Password',
                'cmd_args': 'Commandline Arguments',
                'user_credentials': 'User Credentials',
                'enabled': 'Schedule Enabled',
            }
        }
    }
}

FORM_HELP = {
    'jobs': {
        'manage': {
            'job': {
                'playbook': f"Playbook to execute. Search path: '{config['path_play']}'",
                'inventory': 'One or multiple inventory files/directories to include for the execution. '
                             'Comma-separated list. For details see: '
                             '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html">'
                             'Ansible Docs - Inventory</a>',
                'limit': 'Ansible inventory hosts or groups to limit the execution to.'
                         'For details see: '
                         '<a href="https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html">'
                         'Ansible Docs - Limit</a>',
                'schedule': 'Schedule for running the job automatically. For format see: '
                            '<a href="https://crontab.guru/">crontab.guru</a>',
                'environment_vars': 'Environmental variables to be passed to the Ansible execution. '
                                    'Comma-separated list of key-value pairs. (VAR1=TEST1,VAR2=0)',
            }
        }
    }
}
