#!/bin/bash

sphinx-autobuild -b html . _build/html -p 8061 --ignore "*.swp" -B
