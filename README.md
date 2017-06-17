no-ip-refresher
=============
automatic refresh your no-ip domain name, without 30 days expiration
use [docker-selenium](https://github.com/SeleniumHQ/docker-selenium) to manipulate no-ip with selenium


Requirement
-------
[docker](https://www.docker.com/)


Installation & Configuration
-------
clone source code
```sh
git clone https://github.com/Falldog/no-ip-refresher.git
```

modify configuration in `refresher.cfg`
Example as below:
```
[Refresher]
username=your-name
password=password
host=your-host.ddns.net
```

Refresh in docker
-------
```sh
cd no-ip-refresher
docker build -t no-ip-refresher .
docker run no-ip-refresher
```


crontab
-------
schedule it in crontab
avoid expiration after 30 days
```sh
0 0 1,15 * * root docker run no-ip-refresher  # 1st & 15th day every month
```

