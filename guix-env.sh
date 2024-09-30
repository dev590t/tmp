#!/usr/bin/env bash

# precondition
# $ xhost +
# access control disabled, clients can connect from any host

guix shell -m manifest.scm --expose=$HOME/.local/ --share=$HOME/.local/state/ -CNF --preserve='^DISPLAY$' --share=$HOME/.cache --expose=/etc/machine-id -- env PATH="$PATH:$HOME/.local/bin" PLAYWRIGHT_SKIP_BROWSER_GC=1 bash

# for PDM dev tool
# git => git dep, git branch
# nss-certs => avoid "server certificate verification  failed. CAfile: none CRLfile: none"

# optional
# which coreutils => classic shell operation
