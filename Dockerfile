FROM python:3.11.15-slim@sha256:9358444059ed78e2975ada2c189f1c1a3144a5dab6f35bff8c981afb38946634

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git curl ca-certificates && \
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
