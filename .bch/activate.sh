#!/usr/bin/env bash

export BCH_JOTS__root=$(dirname $(dirname $BASH_SOURCE))
_link () { ln -s $1 $HOME/.local/bin/$(basename $1); }
_link $(dirname $BASH_SOURCE)/lbin/bch.jots

