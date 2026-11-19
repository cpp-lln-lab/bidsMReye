FROM python:3.11.15-slim@sha256:9358444059ed78e2975ada2c189f1c1a3144a5dab6f35bff8c981afb38946634

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/neuro/bidsMReye/models
WORKDIR /home/neuro/bidsMReye

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

COPY [".", "/home/neuro/bidsMReye"]
RUN git restore . && \
    uv export --frozen --no-dev --no-emit-project --no-hashes -o /tmp/requirements.txt && \
    uv pip install --system --no-cache -r /tmp/requirements.txt && \
    uv pip install --system --no-cache --no-deps . && \
    rm /tmp/requirements.txt

RUN bidsmreye_model

ENTRYPOINT [ "/home/neuro/bidsMReye/entrypoint.sh" ]
COPY ["./docker/entrypoint.sh", \
      "/home/neuro/bidsMReye/entrypoint.sh"]
RUN chmod +x /home/neuro/bidsMReye/entrypoint.sh
