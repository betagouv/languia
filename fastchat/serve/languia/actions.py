import gradio as gr

import time

import json

from fastchat.serve.languia.block_conversation import get_conv_log_filename, get_ip

from fastchat.serve.remote_logger import get_remote_logger

from fastchat.utils import (
    build_logger,
    # moderation_filter,
)

logger = build_logger("gradio_web_server_multi", "gradio_web_server_multi.log")


# FIXME: TO REFACTO
def vote_last_response(
    conversations_state, vote_type, _model_selectors, request: gr.Request
):
    logger.info(f"{vote_type}_vote (anony). ip: {get_ip(request)}")
    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(time.time(), 4),
            "type": vote_type,
            "models": [x.model_name for x in conversations_state],
            "conversations_state": [x.dict() for x in conversations_state],
            "ip": get_ip(request),
        }
        logger.info(json.dumps(data))
        fout.write(json.dumps(data) + "\n")

    get_remote_logger().log(data)

    names = (
        "### Model A: " + conversations_state[0].model_name,
        "### Model B: " + conversations_state[1].model_name,
    )
    yield names + ("",)

# TODO: refacto: why the loop?
def leftvote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    for x in vote_last_response(
        [state0, state1], "leftvote", [model_selector0, model_selector1], request
    ):
        yield x


def rightvote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    for x in vote_last_response(
        [state0, state1], "rightvote", [model_selector0, model_selector1], request
    ):
        yield x


def tievote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    for x in vote_last_response(
        [state0, state1], "tievote", [model_selector0, model_selector1], request
    ):
        yield x


def bothbad_vote_last_response(
    state0, state1, model_selector0, model_selector1, request: gr.Request
):
    for x in vote_last_response(
        [state0, state1], "bothbad_vote", [model_selector0, model_selector1], request
    ):
        yield x


def send_preferences(
    state0,
    state1,
    model_selector0,
    model_selector1,
    ressenti_checkbox,
    request: gr.Request,
):
    print(ressenti_checkbox)
    for x in vote_last_response(
        [state0, state1],
        f"ressenti: {str(ressenti_checkbox)}",
        [model_selector0, model_selector1],
        request,
    ):
        yield x


def accept_tos(request: gr.Request):
    global tos_accepted
    tos_accepted = True

    print("ToS accepted!")
    return (
        # accept_tos_btn:
        gr.update(visible=False),
        # mode_screen:
        gr.update(visible=True)
    )


accept_tos_js = """
function () {
  document.cookie="languia_tos_accepted=1"
}
"""
