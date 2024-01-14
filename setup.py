import setuptools

with open('README.md', 'r', encoding='utf-8') as info:
    long_description = info.read()

setuptools.setup(
    name='ansible-webui',
    version='0.0.1',
    author='AnsibleGuy',
    author_email='contact@ansibleguy.net',
    description='Basic WebUI for using Ansible',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ansibleguy/ansible-webui',
    project_urls={
        'Repository': 'https://github.com/ansibleguy/ansible-webui',
        'Bug Tracker': 'https://github.com/ansibleguy/ansible-webui/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5'
)
