#!/usr/bin/env bash
# See the Procfile for usage of this script.

export PYTHONPATH=..:$PWD
./report_event_stats.py
