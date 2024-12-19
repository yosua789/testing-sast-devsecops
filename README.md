# Kecilin Web Logger

This project is used to read logs from webservers such as (nginx, apache)

## installation

For installatio u can run : 


but first u must change volumes dir to location where log is set

```code
    services:
  dasboard:
    container_name: kecilin_web_logger
    build: 
      context: .
      dockerfile: DockerFile
    volumes:
      - ./src:/home/kecilin/src
      - /home/gozilla/project/web_logger/log:/home/log # here change 
    ports:
      - 50001:8000
```

after change, u can run 

```bash
sudo docker-compose up --build
```

## this project under develoment
needed : 
uniq user, req file,not found,os,browesr,reffering site


command for dev :

```bash
goaccess access.log \
--log-format='%h %^[%d:%t %^]%^"%r" %s %b "%R" "%u" %^' \
--date-format=%d/%b/%Y \
--time-format=%T \
--ignore-panel=REFERRERS --ignore-panel=STATUS --ignore-panel=GEO_LOCATION --ignore-panel=KEYPHRASES \
-o report.json
```


additional module : APScheduler