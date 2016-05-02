#!/bin/bash
supervisorctl stop magbot
git pull
supervisorctl start magbot
