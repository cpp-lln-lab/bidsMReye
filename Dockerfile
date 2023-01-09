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

ENV MPLCONFIGDIR=/tmp/.config/matplotlib

RUN bidsmreye_model && \
    bidsmreye_model --model_name 1_guided_fixations && \
    bidsmreye_model --model_name 2_pursuit && \
    bidsmreye_model --model_name 3_openclosed && \
    bidsmreye_model --model_name 3_pursuit && \
    bidsmreye_model --model_name 4_pursuit && \
    bidsmreye_model --model_name 5_free_viewing && \
    bidsmreye_model --model_name 1to5

ENTRYPOINT [ "//home/neuro/bidsMReye/entrypoint.sh" ]
COPY ["./docker/entrypoint.sh", \
      "//home/neuro/bidsMReye/entrypoint.sh"]
RUN chmod +x /home/neuro/bidsMReye/entrypoint.sh

RUN chmod -R 777 /home/neuro/bidsMReye
