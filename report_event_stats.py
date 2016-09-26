#!/usr/bin/env python

import logging

from eventbot import report_event_stats


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    report_event_stats()
