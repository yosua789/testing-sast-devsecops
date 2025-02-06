# Kecilin Web Logger

This project is used to read logs from webservers such as (nginx, apache)

## installation

For installatio u can run : 


but first u must change volumes dir to location where log is set, keep in mind that u can use multiple path to mouthing path, but u must make path in /home/log or in your log path in env 

example : /home/log/test

```code
    services:
  dasboard:
    container_name: kecilin_web_logger
    build: 
      context: .
      dockerfile: DockerFile
    volumes:
      - ./src:/home/kecilin/src
      - /home/gozilla/project/web_logger/log:/home/log/rest # change here 
    ports:
      - 50001:8000
```

after change the path to mouthing, u can run, before u run this project make sure to check .env  

```bash
sudo docker-compose up --build
```

## this project under develoment
needed : 
uniq user, req file,not found,os,browesr,reffering site




additional module : APScheduler

symlink file log

try restart service

docker compose -f /home/gozilla/project/web_logger/docker-compose-testing.yaml up -d --force-recreate  dashboard

dalam bentuk form

jwt for login

add name service
breadcrumb
title spisifik samakan jira
overall title (general info)
auth()

feb 4
pagination not in data table but manual

user managemen(admin,viewer)
1. path 
2. api


