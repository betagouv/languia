"""
The gradio LANGU:IA server with multiple tabs.
It supports chatting with two models side-by-side.
"""

import argparse

from fastchat.serve.themes.dsfr import DSFR

import gradio as gr

from fastchat.serve.languia.block_arena import (
    build_arena,
    load_demo_arena,
    set_global_vars_anony,
)

from fastchat.serve.languia.components import header_html

from fastchat.serve.languia.block_conversation import (
    set_global_vars,
    # build_about,
    get_model_list,
    get_ip,
)
from fastchat.serve.monitor.monitor import build_leaderboard_tab
from fastchat.utils import (
    build_logger,
    get_window_url_params_js,
    get_window_url_params_with_tos_js,
)

import os

import sentry_sdk

logger = build_logger("gradio_web_server_multi", "gradio_web_server_multi.log")

if os.getenv("SENTRY_DSN"):
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate = 1.0
    logger.info("Sentry loaded with traces_sample_rate=" + str(traces_sample_rate))
    if os.getenv("SENTRY_ENV"):
        sentry_env = os.getenv("SENTRY_ENV")
    else:
        sentry_env = "development"
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            environment=sentry_env,
            traces_sample_rate=traces_sample_rate,
        )


def load_demo(url_params, request: gr.Request):
    global models, all_models

    ip = get_ip(request)
    logger.info(f"load_demo. ip: {ip}. params: {url_params}")

    # selected = 0
    # if "arena" in url_params:
    #     selected = 0
    # elif "leaderboard" in url_params:
    #     selected = 4
    # elif "about" in url_params:
    #     selected = 5

    if args.model_list_mode == "reload":
        models, all_models = get_model_list(
            args.controller_url,
            args.register_api_endpoint_file,
            vision_arena=False,
        )

    arena_updates = load_demo_arena(all_models, url_params)

    # return (gr.Tabs(selected=selected),) + arena_updates
    return (gr.Blocks(),) + arena_updates


parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0")
parser.add_argument("--port", type=int)
parser.add_argument(
    "--controller-url",
    type=str,
    default="http://localhost:21001",
    help="The address of the controller",
)
parser.add_argument(
    "--concurrency-count",
    type=int,
    default=10,
    help="The concurrency count of the gradio queue",
)
parser.add_argument(
    "--model-list-mode",
    type=str,
    default="once",
    choices=["once", "reload"],
    help="Whether to load the model list once or reload the model list every time.",
)
parser.add_argument(
    "--moderate",
    action="store_true",
    help="Enable content moderation to block unsafe inputs",
)
parser.add_argument(
    "--show-terms-of-use",
    action="store_true",
    help="Shows term of use before loading the demo",
)
# parser.add_argument(
#     "--random-questions", type=str, help="Load random questions from a JSON file"
# )
parser.add_argument(
    "--register-api-endpoint-file",
    type=str,
    help="Register API-based model endpoints from a JSON file",
    default="register-api-endpoint-file.json",
)
# parser.add_argument(
#     "--gradio-auth-path",
#     type=str,
#     help='Set the gradio authentication file path. The file should contain one or more user:password pairs in this format: "u1:p1,u2:p2,u3:p3"',
#     default=None,
# )
parser.add_argument(
    "--elo-results-file", type=str, help="Load leaderboard results and plots"
)
parser.add_argument(
    "--leaderboard-table-file", type=str, help="Load leaderboard results and plots"
)
parser.add_argument(
    "--gradio-root-path",
    type=str,
    help="Sets the gradio root path, eg /abc/def. Useful when running behind a reverse-proxy or at a custom URL path prefix",
)
parser.add_argument(
    "--debug",
    default=False,
    help="Debug mode if set to true",
)
args = parser.parse_args()

env_debug = os.getenv("LANGUIA_DEBUG")

if env_debug:
    if env_debug.lower() == "true":
        args.debug = True

logger.info(f"args: {args}")

# Set global variables
set_global_vars(args.controller_url, args.moderate, False)
set_global_vars_anony(args.moderate)
models, all_models = get_model_list(
    args.controller_url,
    args.register_api_endpoint_file,
    vision_arena=False,
)

# TODO: make it a modal
if args.show_terms_of_use:
    load_js = get_window_url_params_with_tos_js
else:
    load_js = get_window_url_params_js

# TODO: async load?
head_js = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script type="module" src="file=assets/js/dsfr.module.js"></script>
<script type="text/javascript" nomodule src="file=assets/js/dsfr.nomodule.js"></script>
"""

custom_css = """
#free-mode {
    display: block
    height: 30em
}
#free-mode.selected {
    border-bottom: 5px navy solid;
}
"""

with open("./assets/dsfr.css", encoding="utf-8") as css_file:
    css_dsfr = css_file.read()
# css = css_dsfr
css = css_dsfr + custom_css

with gr.Blocks(
    title="LANGU:IA, l'arène francophone de classement de modèles de langage par préférences humaines",
    theme=DSFR(),
    css=css,
    head=head_js,
) as demo:
    # TODO: skiplinks

    gr.HTML(header_html, elem_id="header_html")

    # Tab was needed for "selected" to work
    # with gr.Tab"Leaderboard", id=6):
    with gr.Blocks() as pages:
        with gr.Blocks():
            two_models_arena = build_arena(models)

        if args.elo_results_file:
            with gr.Group("Leaderboard"):
                build_leaderboard_tab(
                    args.elo_results_file, args.leaderboard_table_file, show_plot=True
                )

        # with gr.Tab("ℹ️  About Us", id=7):
        #     about = build_about()

    url_params = gr.JSON(visible=False)

    if args.model_list_mode not in ["once", "reload"]:
        raise ValueError(f"Unknown model list mode: {args.model_list_mode}")

    demo.load(
        load_demo,
        [url_params],
        js=load_js,
    )

if __name__ == "__main__":
    # Set authorization credentials
    auth = None
    # if args.gradio_auth_path is not None:
    #     auth = parse_gradio_auth_creds(args.gradio_auth_path)

    demo = demo.queue(
        default_concurrency_limit=args.concurrency_count,
        status_update_rate=10,
        # FIXME: what does it do?
        api_open=False,
    )

    # Better use gr.set_static_paths(paths=["test/test_files/"])?
    # use gradio_root_path?
    # Note: access via e.g. DOMAIN/file=assets/fonts/Marianne-Bold.woff
    demo.launch(
        allowed_paths=[
            "/app/assets/fonts",
            "/app/assets/icons",
            "/app/assets/js",
        ],
        server_name=args.host,
        server_port=args.port,
        share=False,
        max_threads=200,
        auth=auth,
        root_path=args.gradio_root_path,
        # TODO: choose if show api
        show_api=args.debug,
        debug=args.debug,
        show_error=args.debug,
    )
