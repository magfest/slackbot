#!/bin/bash
supervisorctl stop leinad
git pull
supervisorctl start leinad
