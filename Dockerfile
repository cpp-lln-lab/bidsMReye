FROM python:3.10.9-bullseye

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/neuro/bidsMReye/models
WORKDIR /home/neuro/bidsMReye

COPY [".", "/home/neuro/bidsMReye"]
RUN pip install --upgrade pip && \
    pip3 install -e .

RUN bidsmreye_model

ENTRYPOINT [ "//home/neuro/bidsMReye/entrypoint.sh" ]
COPY ["./docker/entrypoint.sh", \
      "//home/neuro/bidsMReye/entrypoint.sh"]
RUN chmod +x /home/neuro/bidsMReye/entrypoint.sh
