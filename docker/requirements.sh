#!/bin/sh

echo 'INSTALLING/UPGRADING DEFAULT ANSIBLE DEPENDENCIES..'
pip install --upgrade jmespath netaddr passlib pywinrm requests cryptography >/dev/null

if [ -f '/data/requirements.txt' ]
then
  echo 'INSTALLING/UPGRADING PYTHON MODULES..'
  pip install --upgrade -r '/data/requirements.txt' >/dev/null
fi

if [ -f '/data/requirements_collections.yml' ]
then
  echo 'INSTALLING/UPGRADING ANSIBLE-COLLECTIONS..'
  ansible-galaxy collection install --upgrade -r /data/requirements_collections.yml >/dev/null
fi

if [ -f '/data/requirements_roles.yml' ]
then
  echo 'INSTALLING ANSIBLE-ROLES..'
  ansible-galaxy role install -r /data/requirements_roles.yml >/dev/null
fi
