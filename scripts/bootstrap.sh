#!/bin/bash

### SUPER ANNOYING vagrant issue
apt-get install -y debconf
update-locale LC_CTYPE="en_US.UTF-8" LC_ALL="en_US.UTF-8" LANG="en_US.UTF-8"
dpkg-reconfigure locales

# Create staterep user
if [ -z "$(getent passwd staterep)" ];
then
    useradd -m -k /home/vagrant -s /bin/bash staterep
    echo "staterep ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/80-allow-staterep-sudo
    chmod 0440 /etc/sudoers.d/80-allow-staterep-sudo
fi

# vagrant mounts the share as the wrong user (vagrant)
# umount and remount as staterep.
mountpoint -q /usr/local/staterep/app/ || umount /usr/local/staterep/app
mount -t vboxsf -o uid=`id -u staterep`,gid=`id -g vagrant` share /usr/local/staterep/app
