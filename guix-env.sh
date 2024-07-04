#!/usr/bin/env bash

# precondition
# $ xhost +
# access control disabled, clients can connect from any host

PACKAGES=(python gcc-toolchain nss nss-certs pandoc curl)
PACKAGES_D=(icecat python-pandas)

guix shell --expose=$HOME/.local/ --share=$HOME/.local/state/ -CNF --preserve='^DISPLAY$' --share=$HOME/.cache --expose=/etc/machine-id ${PACKAGES[*]} -D ${PACKAGES_D[*]}
export PATH="$PATH:$HOME/.local/bin" # PDM_BIN_DIR
export PLAYWRIGHT_SKIP_BROWSER_GC=1

# for PDM dev tool
# git => git dep, git branch
# nss-certs => avoid "server certificate verification  failed. CAfile: none CRLfile: none"

# optional
# which coreutils => classic shell operation
