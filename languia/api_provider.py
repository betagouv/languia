import os
import logging


from gradio import ChatMessage
import time

# def to_openai_api_messages(self):
#     """Convert the conversation to OpenAI chat completion format."""
#     if self.system_message == "":
#         ret = []
#     else:
#         ret = [{"role": "system", "content": self.system_message}]

#     for i, (_, msg) in enumerate(self.messages[self.offset :]):
#         if i % 2 == 0:
#             ret.append({"role": "user", "content": msg})
#         else:
#             if msg is not None:
#                 ret.append({"role": "assistant", "content": msg})
#     return ret


def get_api_provider_stream_iter(
    conv,
    model_name,
    model_api_dict,
    temperature,
    top_p,
    max_new_tokens,
    state,
):
    if model_api_dict["api_type"] == "openai":
        prompt = conv.to_openai_api_messages()
        stream_iter = openai_api_stream_iter(
            model_name=model_api_dict["model_name"],
            messages=prompt,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            api_base=model_api_dict["api_base"],
            api_key=model_api_dict["api_key"],
        )
    elif model_api_dict["api_type"] == "vertex":
        prompt = conv.to_openai_api_messages()
        stream_iter = vertex_api_stream_iter(
            model_name=model_api_dict["model_name"],
            messages=prompt,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            api_base=model_api_dict["api_base"],
        )
    else:
        raise NotImplementedError()

    return stream_iter


def openai_api_stream_iter(
    model_name,
    messages,
    temperature,
    top_p,
    max_new_tokens,
    api_base=None,
    api_key=None,
):
    import openai

    api_key = api_key or os.environ["OPENAI_API_KEY"]

    client = openai.OpenAI(
        base_url=api_base or "https://api.openai.com/v1",
        api_key=api_key,
        timeout=180,
    )

    # Make requests for logging
    # text_messages = messages

    # gen_params = {
    #     "model": model_name,
    #     "prompt": text_messages,
    #     "temperature": temperature,
    #     "top_p": top_p,
    #     "max_new_tokens": max_new_tokens,
    # }
    # logging.info(f"==== request ====\n{gen_params}")

    res = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_new_tokens,
        stream=True,
    )
    text = ""
    for chunk in res:
        if len(chunk.choices) > 0:
            text += chunk.choices[0].delta.content or ""
            data = {
                "text": text,
                "error_code": 0,
            }
            yield data


def vertex_api_stream_iter(
    api_base, model_name, messages, temperature, top_p, max_new_tokens
):
    # import vertexai
    # from vertexai import generative_models
    # from vertexai.generative_models import (
    #     GenerationConfig,
    #     GenerativeModel,
    #     Image,
    # )
    # GOOGLE_APPLICATION_CREDENTIALS
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        logging.warn("No Google creds detected!")

    import google.auth
    import google.auth.transport.requests
    import openai

    # Programmatically get an access token
    # creds, project = google.auth.default()
    creds, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    # Note: the credential lives for 1 hour by default (https://cloud.google.com/docs/authentication/token-types#at-lifetime); after expiration, it must be refreshed.

    # Pass the Vertex endpoint and authentication to the OpenAI SDK
    PROJECT = project
    client = openai.OpenAI(base_url=api_base, api_key=creds.token)

    # print(client.models.list())
    # project_id = os.environ.get("GCP_PROJECT_ID", None)
    # location = os.environ.get("GCP_LOCATION", None)
    # vertexai.init(project=project_id, location=location)

    # gen_params = {
    #     "model": model_name,
    #     "prompt": messages,
    #     "temperature": temperature,
    #     "top_p": top_p,
    #     "max_new_tokens": max_new_tokens,
    # }
    # logging.info(f"==== request ====\n{gen_params}")

    # safety_settings = [
    #     generative_models.SafetySetting(
    #         category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
    #         threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    #     ),
    #     generative_models.SafetySetting(
    #         category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    #         threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    #     ),
    #     generative_models.SafetySetting(
    #         category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    #         threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    #     ),
    #     generative_models.SafetySetting(
    #         category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    #         threshold=generative_models.HarmBlockThreshold.BLOCK_NONE,
    #     ),
    # ]

    res = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_new_tokens,
        stream=True,
    )
    text = ""
    for chunk in res:
        if len(chunk.choices) > 0:
            text += chunk.choices[0].delta.content or ""
            data = {
                # Processing \n for Llama3.1-405B
                "text": text.replace("\n", "<br />"),
                "error_code": 0,
            }
            yield data

    # generator = GenerativeModel(model_name).generate_content(
    #     messages,
    #     stream=True,
    #     generation_config=GenerationConfig(
    #         top_p=top_p, max_output_tokens=max_new_tokens, temperature=temperature
    #     ),
    #     safety_settings=safety_settings,
    # )

    # ret = ""
    # for chunk in generator:
    #     # NOTE(chris): This may be a vertex api error, below is HOTFIX: https://github.com/googleapis/python-aiplatform/issues/3129
    #     ret += chunk.candidates[0].content.parts[0]._raw_part.text
    #     # ret += chunk.text
    #     data = {
    #         "text": ret,
    #         "error_code": 0,
    #     }
    #     yield data
