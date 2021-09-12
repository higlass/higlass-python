#!/bin/bash

sphinx-autobuild -b html . _build/html --port 8061 --ignore "*.swp" 
