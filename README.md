# HTTP Monitoring tool

[![Build Status](https://travis-ci.com/bsavelev/httpmon.svg?branch=master)](https://travis-ci.com/bsavelev/httpmon)
[![Coverage Status](https://coveralls.io/repos/github/bsavelev/httpmon/badge.svg?branch=master)](https://coveralls.io/github/bsavelev/httpmon?branch=master)

## About
Distribution HTTP monitoring tool with Apache Kafka data pipeline and Postgres as storage.

## Usage
### Producer

```python ./httpmon-cli.py --kafka-server localhost:9093 --kafka-topic test -v producer -u https://www.google.com --period 2 --timeout 10 --body '.*<html.*>'```

Will check:
* Url `https://www.google.com`
* Every `2` second
* With timeout `10` seconds
* Check response body with `.*<html.*>` 
* Push check result to Apache Kafka at `localhost:9093`

### Consumer
```python ./httpmon-cli.py --kafka-server localhost:9093 --kafka-topic test consumer --uri postgresql://postgres:secret@localhost/httpmon```

Will read stream from Apache Kafka and write date into Postgres DB specified with `--uri` option.

#### Database preparation

Create database and prepare it with initialization SQL:
```psql postgresql://postgres:secret@localhost/httpmon < sql/init.sql```
