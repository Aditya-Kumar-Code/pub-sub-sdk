FROM python:3.8

WORKDIR /app
RUN curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash
RUN mkdir -p /root/.dapr/components
RUN mkdir -p /root/.dapr/bin/daprd
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["dapr", "run" ,"--app-id" ,"python-subscriber" ,"--app-port","50051","python3","app.py"]
