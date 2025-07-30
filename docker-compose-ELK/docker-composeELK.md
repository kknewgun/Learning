# docker-compose run ELK

## 1. 新增 elasticsearch 持久層資料夾
```
mkdir -p -m 777 /data/elasticsearch && mkdir -p -m 777 /data/elasticsearch2 && cp -r logstash /data/logstash
```

# logstash.conf
```
file {
    path => "/usr/share/logstash/Log/*"
    type => "file"
    start_position => "beginning"
   }
 }

filter {
    grok {
           match => ["message", "%{TIMESTAMP_ISO8601:[@metadata][timestamp]} %{NUMBER:threadid} %{LOGLEVEL:loglevel} %{NOTSPACE:logger} %{GREEDYDATA:message}"]
           overwrite => [ "message" ]
        }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logstash-test"  
   }
  stdout { codec => rubydebug}
}
```

# docker-compose.yaml

```
version: '3.2'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.7.0
    container_name: elasticsearch
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /data/elasticsearch:/usr/share/elasticsearch/data
    ports:
      - 9200:9200
    networks:
      - esnet
  elasticsearch2:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.7.0
    container_name: elasticsearch2
    environment:
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - "discovery.zen.ping.unicast.hosts=elasticsearch"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - /data/elasticsearch2:/usr/share/elasticsearch/data
    networks:
      - esnet
    restart: always
  kibana:
    image: docker.elastic.co/kibana/kibana:6.7.0
    container_name: kibana
    ports:
    - "5601:5601"
    restart: always
    networks:
      - esnet
  logstash:
    image: docker.elastic.co/logstash/logstash:6.7.0
    container_name: logstash
    volumes:
    - /tmp/Log/:/usr/share/logstash/Log
    - /data/logstash/pipeline:/usr/share/logstash/pipeline/
    restart: always
    networks:
      - esnet
networks:
  esnet:
```

# docker-compose
docker-compose up -d
docker-compose  down
