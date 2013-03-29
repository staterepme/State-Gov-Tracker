#!/bin/bash

set -x

vagrant up

CONFIG=`vagrant ssh-config`

PORT=`perl -n -e'/Port (\d+)/ && print $1' <<< "$CONFIG"`
ID_FILE=`perl -n -e'/IdentityFile (.*)/ && print $1' <<< "$CONFIG"`

TMP_FILE="/tmp/ansible_hosts.$$"
THEHOST="127.0.0.1:$PORT"

cat <<EOF > $TMP_FILE
[database]
$THEHOST

[appserver]
$THEHOST

[proxy]
$THEHOST

EOF

ansible-playbook -e "dev=1" -i "$TMP_FILE" --private-key "$ID_FILE" playbooks/all.yml

rm "$TMP_FILE"
