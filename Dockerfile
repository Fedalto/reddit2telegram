FROM python:3.8.5-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /bot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "-m", "reddit2telegram"]
