
FROM oraclelinux:8-slim

RUN microdnf install -y libaio unzip python3 python3-pip gcc gcc-c++ make rust cargo && microdnf clean all

RUN microdnf install -y libnsl

WORKDIR /opt/oracle
COPY docker/instantclient-basic-linux.x64-19.28.0.0.0dbru.zip .
RUN unzip instantclient-basic-linux.x64-19.28.0.0.0dbru.zip &&     rm instantclient-basic-linux.x64-19.28.0.0.0dbru.zip &&     echo "/opt/oracle/instantclient_19_28" > /etc/ld.so.conf.d/oracle-instantclient.conf &&     ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_28
ENV PATH=$LD_LIBRARY_PATH:$PATH

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
