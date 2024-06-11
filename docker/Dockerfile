# FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04
FROM python:3.9-slim AS build

RUN groupadd fastchat --gid 10001 && useradd --system -u 10001 --gid 10001 --home /app fastchat
USER fastchat
WORKDIR /app

# RUN python3.9 -m venv /app/venv
# ENV VIRTUAL_ENV=/app/venv
# ENV PATH="/app/venv/bin:$PATH"
# Install deps first
RUN pip3 install fschat[webui]

# For monitoring
RUN pip3 install plotly psutil

# For OpenAI-like APIs
RUN pip3 install openai

COPY --chown=fastchat:fastchat . /app

# TODO: distroless virtualenv and multistage build
# FROM gcr.io/distroless/python3-debian11

# ENV VIRTUAL_ENV=/app/venv
# ENV PATH="/app/venv/bin:$PATH"

# COPY --from=build /app /app