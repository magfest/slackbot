#!/bin/bash
supervisorctl stop processname
git pull
supervisorctl start processname
