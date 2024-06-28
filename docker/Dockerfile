FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04 AS build
# FROM debian:11-slim
# FROM python:3.9-slim

RUN apt-get update -y && apt-get install -y python3.9 python3.9-distutils curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# TODO: virtualenv
RUN python3.9 get-pip.py
RUN pip3 install fschat
RUN pip3 install fschat[model_worker,webui]
RUN pip3 install openai plotly pydantic-settings sentry-sdk

# Specific to LANGU:IA: install required Gradio Custom Components
FROM python:3.9-slim as custom_components
RUN apt update && apt install -y nodejs npm
RUN pip3 install gradio
COPY ./gradio-dsfr/ /custom_components/
WORKDIR /custom_components/frbutton
RUN gradio cc install
RUN gradio cc build

FROM build
COPY --from=custom_components /custom_components/frbutton/dist/gradio_frbutton-0.0.1-py3-none-any.whl /gradio_frbutton-0.0.1-py3-none-any.whl
RUN pip3 install /gradio_frbutton-0.0.1-py3-none-any.whl

WORKDIR /app
COPY . /app

VOLUME /data

EXPOSE 80

CMD ["python3.9", "-m", "fastchat.serve.gradio_web_server_multi_languia", "--controller-url", "http://fastchat-controller:21001", "--register-api-endpoint-file", "/register-api-endpoint-file.json", "--host", "0.0.0.0", "--port", "80"]