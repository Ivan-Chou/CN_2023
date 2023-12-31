#!/bin/bash
nginx -c /phase2/nginx_files/nginx.conf
service nginx start
python3 server.py
service nginx stop