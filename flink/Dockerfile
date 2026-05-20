FROM apache/flink:1.18.1-scala_2.12-java11

# Kafka connector
RUN wget -P /opt/flink/lib \
    https://repo1.maven.org/maven2/org/apache/flink/flink-connector-kafka/3.1.0-1.18/flink-connector-kafka-3.1.0-1.18.jar && \
    wget -P /opt/flink/lib \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    python -m pip install --upgrade pip && \
    python -m pip install \
        "numpy>=1.24.0" \
        "apache-flink==1.18.1" \
        "kafka-python" \
        "google-cloud-storage" \
        "google-cloud-bigquery"