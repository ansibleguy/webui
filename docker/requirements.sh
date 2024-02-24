#!/bin/sh

echo 'INSTALLING/UPGRADING DEFAULT ANSIBLE DEPENDENCIES..'
pip install --upgrade jmespath netaddr passlib pywinrm requests cryptography --root-user-action=ignore --no-warn-script-location >/dev/null

if [ -f '/play/requirements.txt' ]
then
  echo 'INSTALLING/UPGRADING PYTHON MODULES..'
  pip install --upgrade -r '/play/requirements.txt' --root-user-action=ignore --no-warn-script-location >/dev/null
fi

if [ -f '/play/requirements.yml' ]
then
  echo 'INSTALLING/UPGRADING ANSIBLE-COLLECTIONS..'
  ansible-galaxy collection install --upgrade -r /play/requirements.yml >/dev/null
  echo 'INSTALLING ANSIBLE-ROLES..'
  ansible-galaxy role install --force -r /play/requirements.yml  >/dev/null
fi

if [ -f '/play/requirements_collections.yml' ]
then
  echo 'INSTALLING/UPGRADING ANSIBLE-COLLECTIONS..'
  ansible-galaxy collection install --upgrade -r /play/requirements_collections.yml >/dev/null
fi

if [ -f '/play/collections/requirements.yml' ]
then
  echo 'INSTALLING/UPGRADING ANSIBLE-COLLECTIONS..'
  ansible-galaxy collection install --upgrade -r /play/collections/requirements.yml >/dev/null
fi

if [ -f '/play/requirements_roles.yml' ]
then
  echo 'INSTALLING ANSIBLE-ROLES..'
  ansible-galaxy role install --force -r /play/requirements_roles.yml >/dev/null
fi

if [ -f '/play/roles/requirements.yml' ]
then
  echo 'INSTALLING ANSIBLE-ROLES..'
  ansible-galaxy role install --force -r /play/roles/requirements.yml >/dev/null
fi
