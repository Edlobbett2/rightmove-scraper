#!/usr/bin/env bash
# Build script to verify package installation
pip install -r requirements.txt
pip show gunicorn
which gunicorn 