#!/usr/bin/env bash
DEFAULT_CHANNELS=/tmp/default_channels.scm
echo "%default-channels" > $DEFAULT_CHANNELS
# TODO non guix derivation fail with time-machine
# guix time-machine --commit=472706ae2f9160833951a4e4bcc4c206e03097b0 -C $DEFAULT_CHANNELS -- install -p .t ${PACKAGES}[*]
guix time-machine --commit=472706ae2f9160833951a4e4bcc4c206e03097b0 -C $DEFAULT_CHANNELS -- shell --expose=$HOME/.local/ -F --preserve='^DISPLAY$' --share=$HOME/.cache -N --expose=/etc/machine-id --container python python-pandas gcc:lib nss nss-certs -D icecat
export PATH="$PATH:$HOME/.local/bin"
export PLAYWRIGHT_SKIP_BROWSER_GC=1


# dev_1@dev_1 /mnt/recoverData/linuxProgram/workspace/finrl_usage$ /run/current-system/profile/bin/guix package --list-generations -p /home/dev_1/opt/python-dev_3_7
# Generation 13	Aug 25 2022 14:21:45	(current)
#  + python-ta-lib	0.4.21	out	/gnu/store/xmmv5rj9k1sfx6mhb14cjgghlpajkhw9-python-ta-lib-0.4.21

# $ /run/current-system/profile/bin/guix package --list-installed -p /home/dev_1/opt/python-dev_3_7
# glibc         	2.29  	out	/gnu/store/jdfs3xvlnj272475yja6bjrprfsgnkdd-glibc-2.29
# zlib          	1.2.11	out	/gnu/store/qx7p7hiq90mi7r78hcr9cyskccy2j4bg-zlib-1.2.11
# expat         	2.2.7 	out	/gnu/store/vy4aqrx45y5ip56ri71df9x9q5p0ap1m-expat-2.2.9
# python-wrapper	3.7.4 	out	/gnu/store/1dzzq1ka3ifnqrlka984i5ysby8ghs3y-python-wrapper-3.7.4
# python        	3.7.4 	out	/gnu/store/d7jmr2sd8lmlsghnnal13rn1i4c22xff-python-3.7.4
# which         	2.21  	out	/gnu/store/4izp5ih15pdr3q2hax2c6fmjqsw4vcrv-which-2.21
# coreutils     	8.31  	out	/gnu/store/zibwkb5xavnv6z3gzknfqjsxb9b0izh0-coreutils-8.31
# libgccjit     	9.3.0 	out	/gnu/store/q4xaxc64v73rrkfw0ha4v4z0gr3c833w-libgccjit-9.3.0
# opencv        	3.4.3 	out	/gnu/store/q07irwqcaw50ipq62gj014zylxhf35wx-opencv-3.4.3
# mesa          	19.3.4	out	/gnu/store/65zkg5hcxpl9ncb0j5g6mvjszf2mi0wl-mesa-19.3.4
# glib          	2.60.6	out	/gnu/store/rp0hd7k1j3idvcbfh683cskqcz6rkx0a-glib-2.60.6
# python-ta-lib 	0.4.21	out	/gnu/store/xmmv5rj9k1sfx6mhb14cjgghlpajkhw9-python-ta-lib-0.4.21

# python dev env
DEFAULT_CHANNELS=/tmp/default_channels.scm
echo "%default-channels" > $DEFAULT_CHANNELS

PACKAGES="libgccjit  python@3.7 glibc --ad-hoc python@3.7 which coreutils libgccjit git nss-certs zlib expat mesa glib cmake gcc-toolchain"
# runtime
# python@3.7 => interpreter used by pyproject
# libgccjit => ImportError: libstdc++.so.6: cannot open shared object file: No such file or directory. more info: fb83b9aa-23fe-4433-93fc-613b899c8e8f
# mesa => cv2 => raylib
# glib => libgthread-2.0.so.0 => cv2 => ray

# cmake, gcc-toolchain => compile wheel

# zlib => expected by pandas. more info: a29ff164-dfe1-43f2-afe1-16fbbcd53fce
# expat => no sure if needed. more info: 155457e7-551a-497a-b275-c573df0d9228
# ces package maybe is déjà in {which, coreutils}

# {which, coreutils} => has some dep package essentiel for pandas sans trigger segment fault. dont {zlib,expat}. more info : c4a23500-e63a-45fb-955b-aa725d217963

guix time-machine \
    --url=https://git.savannah.gnu.org/git/guix.git --commit=c81457a5883ea43950eb2ecdcbb58a5b144bcd11 \
    -C $DEFAULT_CHANNELS -- environment --pure $PACKAGES

# install in profile to avoid rebuild after guix gc
guix time-machine \
    --url=https://git.savannah.gnu.org/git/guix.git --commit=c81457a5883ea43950eb2ecdcbb58a5b144bcd11 \
    -C $DEFAULT_CHANNELS -- install $PACKAGES -p ~/opt/python-dev_3_7


# for PDM dev tool
# git => git dep, git branch
# nss-certs => avoid "server certificate verification  failed. CAfile: none CRLfile: none"

# optional
# which coreutils => classic shell operation
export PYTHONPATH=/home/dev_1/.local/share/pdm/venv/lib/python3.8/site-packages/pdm/pep582:/home/dev_1/opt/python-dev_3_7/lib/python3.7/site-packages
PDM_BIN_DIR=/home/dev_1/.local/bin
export PATH="$PATH:$PDM_BIN_DIR"
# pdm run ./wrapper jupyter notebook
