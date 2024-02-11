from aw.config.hardcoded import LOGOUT_PATH

NAVIGATION = {
    'left': {
        # 'Dashboard': '/ui/',
        'Jobs': {
            'Manage': '/ui/jobs/manage',
            'Logs': '/ui/jobs/log',
            'Credentials': '/ui/jobs/credentials',
        },
        'Settings': {
            'API Keys': '/ui/settings/api_keys',
            'Permissions': '/ui/settings/permissions',
            # 'Ansible': '/ui/settings/ansible',
        },
        'System': {
            'Admin': '/ui/admin/',
            'API Docs': '/ui/api_docs',
            # 'Config': '/ui/settings/system',
            'Environment': '/ui/system/environment',
        },
    },
    'right': {
        'GH': {
            'element': '<i class="fab fa-github-square fa-2x aw-nav-right-icon" title="GitHub"></i>',
            'url': 'https://github.com/ansibleguy/ansible-webui',
            'login': False,
        },
        'DON': {
            'element': '<i class="fas fa-coins fa-2x aw-nav-right-icon" title="Sponsor"></i>',
            'url': 'https://github.com/sponsors/ansibleguy',
            'login': False,
        },
        'BUG': {
            'element': '<i class="fas fa-bug fa-2x aw-nav-right-icon" title="Report bug"></i>',
            'url': 'https://github.com/ansibleguy/ansible-webui/issues',
            'login': False,
        },
        'DOC': {
            'element': '<i class="fas fa-book fa-2x aw-nav-right-icon" title="Documentation"></i>',
            'url': 'https://ansible-webui.readthedocs.io/',
            'login': False,
        },
        'LO': {
            'element': '<i class="fas fa-sign-out-alt fa-2x aw-nav-right-icon aw-nav-right-icon-logout" '
                       'title="Logout"></i>',
            'url': LOGOUT_PATH,
            'login': True,
        },
    }
}
