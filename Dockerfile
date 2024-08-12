FROM python:3.11.9-slim-bullseye@sha256:8850f5e6e8da9081a6d156252a11161aa22f04d6ed1723c57ca2d5a5d48132bc

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/neuro/bidsMReye/models
WORKDIR /home/neuro/bidsMReye

COPY [".", "/home/neuro/bidsMReye"]
RUN pip install --upgrade pip && \
    pip3 install -r requirements.txt && \
    git restore . && pip3 install .

RUN bidsmreye_model

ENTRYPOINT [ "/home/neuro/bidsMReye/entrypoint.sh" ]
COPY ["./docker/entrypoint.sh", \
      "/home/neuro/bidsMReye/entrypoint.sh"]
RUN chmod +x /home/neuro/bidsMReye/entrypoint.sh
