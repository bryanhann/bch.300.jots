#!/usr/bin/env bash

__export() { export BCH_JOTS_${1}="${2}"; }
__export _root $(dirname $(dirname ${BASH_SOURCE[0]}))
__export _bin  ${BCH_JOTS__root}/.bch.bin
unset __export

bch:000:linkall ${BCH_JOTS__bin}
