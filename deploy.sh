#!/bin/bash
echo off

python setup.py sdist
twine upload dist/*
