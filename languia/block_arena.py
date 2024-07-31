"""
Chatbot Arena (battle) tab.
Users chat with two anonymous models.
"""

# import json
# import time

import gradio as gr
import numpy as np

from fastchat.constants import (
    MODERATION_MSG,
    CONVERSATION_LIMIT_MSG,
    SLOW_MODEL_MSG,
    CONVERSATION_TURN_LIMIT,
)

# from fastchat.model.model_adapter import get_conversation_template

from languia.block_conversation import (
    # TODO: to import/replace State and bot_response?
    ConversationState,
    bot_response,
)

from fastchat.utils import moderation_filter

import logging as logger

from languia.utils import (
    get_ip,
    get_battle_pair,
    build_reveal_html,
    start_screen_html,
    header_html,
    stepper_html,
    vote_last_response,
    get_model_extra_info,
    count_output_tokens,
    get_llm_impact,
    running_eq,
)

from custom_components.frbutton.backend.gradio_frbutton import FrButton
from custom_components.frinput.backend.gradio_frinput import FrInput


from languia import config

from languia.config import (
    BLIND_MODE_INPUT_CHAR_LEN_LIMIT,
    SAMPLING_WEIGHTS,
    BATTLE_TARGETS,
    SAMPLING_BOOST_MODELS,
    OUTAGE_MODELS,
)

# // Enable navigation prompt
# window.onbeforeunload = function() {
#     return true;
# };
# // Remove navigation prompt
# window.onbeforeunload = null;


def add_text(
    # state0: ConversationState,
    # state1: ConversationState,
    state0: gr.State,
    state1: gr.State,
    # model_selector0: gr.Markdown,
    # model_selector1: gr.Markdown,
    text: gr.Text,
    request: gr.Request,
):
    ip = get_ip(request)
    logger.info(f"add_text (anony). ip: {ip}. len: {len(text)}")
    conversations_state = [state0, state1]
    # model_selectors = [model_selector0, model_selector1]

    # TODO: refacto and put init apart
    # Init conversations_state if necessary
    if conversations_state[0] is None:
        assert conversations_state[1] is None

        model_left, model_right = get_battle_pair(
            config.models,
            BATTLE_TARGETS,
            OUTAGE_MODELS,
            SAMPLING_WEIGHTS,
            SAMPLING_BOOST_MODELS,
        )
        conversations_state = [
            # NOTE: replacement of gr.State() to ConversationState happens here
            ConversationState(model_name=model_left),
            ConversationState(model_name=model_right),
        ]

    model_list = [conversations_state[i].model_name for i in range(config.num_sides)]
    # turn on moderation in battle mode
    all_conv_text_left = conversations_state[0].conv.get_prompt()
    all_conv_text_right = conversations_state[1].conv.get_prompt()
    all_conv_text = (
        all_conv_text_left[-1000:] + all_conv_text_right[-1000:] + "\nuser: " + text
    )
    # flagged = moderation_filter(all_conv_text, model_list, do_moderation=False)
    # if flagged:
    #     logger.info(f"violate moderation (anony). ip: {ip}. text: {text}")
    #     # overwrite the original text
    #     text = MODERATION_MSG

    conv = conversations_state[0].conv
    if (len(conv.messages) - conv.offset) // 2 >= CONVERSATION_TURN_LIMIT:
        logger.info(f"conversation turn limit. ip: {get_ip(request)}. text: {text}")
        for i in range(config.num_sides):
            conversations_state[i].skip_next = True
            # FIXME: fix return value
        return (
            # 2 conversations_state
            conversations_state
            # 2 chatbots
            + [x.to_gradio_chatbot() for x in conversations_state]
            # text
            # + [CONVERSATION_LIMIT_MSG]
            # + [gr.update(visible=True)]
        )

    text = text[:BLIND_MODE_INPUT_CHAR_LEN_LIMIT]  # Hard cut-off
    # TODO: what do?

    for i in range(config.num_sides):
        conversations_state[i].conv.append_message(
            conversations_state[i].conv.roles[0], text
        )
        conversations_state[i].conv.append_message(
            conversations_state[i].conv.roles[1], None
        )
        conversations_state[i].skip_next = False

    # TODO: refacto, load/init components and .then() add text
    return (
        # 2 conversations_state
        conversations_state
        # 2 chatbots
        + [x.to_gradio_chatbot() for x in conversations_state]
    )


def bot_response_multi(
    state0,
    state1,
    temperature,
    top_p,
    max_new_tokens,
    request: gr.Request,
):
    logger.info(f"bot_response_multi (anony). ip: {get_ip(request)}")

    if state0 is None or state0.skip_next:
        # This generate call is skipped due to invalid inputs
        yield (
            state0,
            state1,
            state0.to_gradio_chatbot(),
            state1.to_gradio_chatbot(),
        )
        return

    conversations_state = [state0, state1]
    gen = []
    for i in range(config.num_sides):
        gen.append(
            bot_response(
                conversations_state[i],
                temperature,
                top_p,
                max_new_tokens,
                request,
                apply_rate_limit=False,
                use_recommended_config=True,
            )
        )

    is_stream_batch = []
    for i in range(config.num_sides):
        is_stream_batch.append(
            conversations_state[i].model_name
            in [
                "gemini-pro",
                "gemini-pro-dev-api",
                "gemini-1.0-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemma-1.1-2b-it",
                "gemma-1.1-7b-it",
            ]
        )
    chatbots = [None] * config.num_sides
    iters = 0
    while True:
        stop = True
        iters += 1
        for i in range(config.num_sides):
            try:
                # yield gemini fewer times as its chunk size is larger
                # otherwise, gemini will stream too fast
                if not is_stream_batch[i] or (iters % 30 == 1 or iters < 3):
                    ret = next(gen[i])
                    conversations_state[i], chatbots[i] = ret[0], ret[1]
                stop = False
            except StopIteration:
                pass
        yield conversations_state + chatbots
        if stop:
            break


# def check_for_tos_cookie(request: gr.Request):
#     if request:
#         cookies_kv = request.headers["cookie"].split(";")
#         for cookie_kv in cookies_kv:
#             cookie_key, cookie_value = cookie_kv.split("=")
#             if cookie_key == "languia_tos_accepted":
#                 if cookie_value == "1":
#                     tos_accepted = True
#                     return tos_accepted

#     return tos_accepted


def clear_history(
    state0,
    state1,
    chatbot0,
    chatbot1,
    # model_selector0,
    # model_selector1,
    textbox,
    request: gr.Request,
):
    logger.info(f"clear_history (anony). ip: {get_ip(request)}")
    #     + chatbots
    # + [textbox]
    # + [chat_area]
    # + [vote_area]
    # + [supervote_area]
    # + [mode_screen],
    return [
        None,
        None,
        None,
        None,
        "",
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
    ]


from themes.dsfr import DSFR

with gr.Blocks(
    title="LANGU:IA – L'arène francophone de comparaison de modèles conversationnels",
    theme=DSFR(),
    css=config.css,
    head=config.arena_head_js,
    analytics_enabled=False,
    # Doesn't work with uvicorn
    # delete_cache=(1, 1) if config.debug else None,
    # Dirty hack for accepting ToS
    js="""function() {
// start_arena_btn code: check for ToS+Waiver

    const acceptWaiverCheckbox = document.getElementById('accept_waiver');

    const acceptTosCheckbox = document.getElementById('accept_tos');

    const startArenaBtn = document.getElementById('start_arena_btn');

    function checkAndEnableButton() {
        const shouldEnable = acceptWaiverCheckbox.checked && acceptTosCheckbox.checked;

        startArenaBtn.disabled = !shouldEnable;
    }

    acceptWaiverCheckbox.addEventListener('change', function() {
        checkAndEnableButton();
    });

    acceptTosCheckbox.addEventListener('change', function() {
        checkAndEnableButton();
    });

    // Initial check
    checkAndEnableButton();
// scroll to guided area if selected    

  const scrollButton = document.getElementById('guided-mode');
  const targetElement = document.getElementById('guided-area');

  // only works on second click :(
  scrollButton.addEventListener('click', () => {
    targetElement.scrollIntoView({ 
      behavior: 'smooth'
    });
  });

// // scroll to last prompt
//   var left = document.querySelector('#chatbot-0 .user'); 
//   var last_left = left.items(left.length-1);
//   var right = document.querySelector('#chatbot-1 .user'); 
//   var last_right = right.items(right.length-1);
//   const sendButton = document.getElementById('send-btn');
// 
//   // FIXME: only when our prompt is added to chat
//   sendButton.addEventListener('click', () => {
//     last_left.scrollIntoView({ 
//       behavior: 'smooth'
//     });
//     last_right.scrollIntoView({ 
//       behavior: 'smooth'
//     });
//   });

}

""",
) as demo:
    conversations_state = [gr.State() for _ in range(config.num_sides)]
    # model_selectors = [None] * num_sides
    # TODO: allow_flagging?
    chatbots = [None] * config.num_sides

    # TODO: check cookies on load!
    # tos_cookie = check_for_tos_cookie(request)
    # if not tos_cookie:
    header = gr.HTML(start_screen_html, elem_id="header_html")

    with gr.Column(elem_classes="fr-container") as start_screen:

        # TODO: DSFRize
        # accept_waiver_checkbox = gr.Checkbox(
        #     label="J'ai compris que mes données transmises à l'arène seront mises à disposition à des fins de recherche",
        #     show_label=True,
        #     elem_classes="",
        # )
        # # FIXME: custom component for checkboxes
        # accept_tos_checkbox = gr.Checkbox(
        #     label="J'accepte les conditions générales d'utilisation :",
        #     show_label=True,
        #     elem_id="accept_tos_checkbox",
        # )
        # gr.HTML(elem_id="accept_tos_label", value="""<a href="/cgu" target="_blank">Conditions générales d'utilisation</a>.""")

        start_arena_btn = gr.Button(
            value="C'est parti",
            scale=0,
            # TODO: à centrer
            elem_id="start_arena_btn",
            elem_classes="fr-btn fr-mx-auto",
            interactive=False,
        )

    with gr.Row(elem_id="stepper-row", elem_classes="raised fr-pb-2w") as stepper_row:
        stepper_block = gr.HTML(
            stepper_html("Choix du mode de conversation", 1, 4),
            elem_id="stepper_html",
            elem_classes="fr-container",
            visible=False,
        )

    with gr.Column(
        visible=False, elem_id="mode-screen", elem_classes="fr-container"
    ) as mode_screen:
        gr.HTML(
            """
        <div class="fr-notice fr-notice--info"> 
            <div class="fr-container">
                    <div class="fr-notice__body mission" >
                        <p class="fr-notice__title mission">Discutez d’un sujet qui vous intéresse puis évaluez les réponses des modèles.</p>
                    </div>
            </div>
        </div>"""
        )
        gr.HTML(
            """<div class="text-center fr-mt-4w fr-mb-2w fr-grid-row fr-grid-row--center"><h4 class="fr-mb-1v fr-col-12">Comment voulez-vous commencer la conversation ?</h4>
            <p class="fr-col-12"><em>(Sélectionnez un des deux modes)</em></p></div>"""
        )
        with gr.Row(
            elem_classes="fr-grid-row fr-grid-row--gutters fr-grid-row--center fr-col-12"
        ):
            mode_selection_classes = "fr-col-12 fr-col-md-4 fr-p-4w"
            free_mode_btn = FrButton(
                custom_html="""<h4>Mode libre</h4><p class="fr-text--lg">Ecrivez directement aux modèles, discutez du sujet que vous voulez</p>""",
                elem_id="free-mode",
                elem_classes="fr-ml-auto " + mode_selection_classes,
                icon="assets/extra-artwork/conclusion.svg",
            )
            guided_mode_btn = FrButton(
                elem_classes="fr-mr-auto " + mode_selection_classes,
                elem_id="guided-mode",
                custom_html="""<h4>Mode inspiré</h4><p class="fr-text--lg">Vous n'avez pas d'idée ? Découvrez une série de thèmes inspirants</p>""",
                icon="assets/extra-artwork/innovation.svg",
            )

        with gr.Column(
            elem_id="guided-area",
            # elem_classes="fr-grid-row" messes with visible=False...
            # elem_classes="fr-grid-row fr-grid-row--center",
            visible=False,
        ) as guided_area:
            gr.Markdown(
                elem_classes="text-center fr-mt-4w fr-mb-2w",
                value="##### Sélectionnez un thème que vous aimeriez explorer :",
            )
            # fr-col-12 fr-col-sm-8 fr-col-md-6 fr-col-lg-4 fr-col-xl-2
            with gr.Row(elem_classes="radio-tiles"):
                maniere = FrButton(
                    value="maniere",
                    custom_html="""<span class="fr-badge fr-badge--purple-glycine">Style</span><p>Ecrire à la manière d'un romancier ou d'une romancière</p>""",
                )
                registre = FrButton(
                    value="registre",
                    custom_html="""<span class="fr-badge fr-badge--purple-glycine">Style</span><p>Transposer en registre familier, courant, soutenu…</p>""",
                )
                creativite_btn = FrButton(
                    value="creativite",
                    custom_html="""<span class="fr-badge fr-badge--green-tilleul-verveine">Créativité</span><p>Jeux de mots, humour et expressions</p>""",
                )
            with gr.Row(elem_classes="radio-tiles"):
                pedagogie = FrButton(
                    value="pedagogie",
                    custom_html="""<span class="fr-badge fr-badge--blue-cumulus">Pédagogie</span><p>Expliquer simplement un concept</p>""",
                )
                regional = FrButton(
                    value="regional",
                    custom_html="""<span class="fr-badge fr-badge--yellow-moutarde">Diversité</span><p>Parler en Occitan, Alsacien, Basque, Picard…</p>""",
                )
                variete = FrButton(
                    value="variete",
                    custom_html="""<span class="fr-badge fr-badge--yellow-moutarde">Diversité</span><p>Est-ce différent en Québécois, Belge, Suisse, Antillais…</p>""",
                )
            # guided_prompt = gr.Radio(
            #     choices=["Chtimi ?", "Québécois ?"], elem_classes="", visible=False
            # )

    # with gr.Column(elem_id="send-area", elem_classes="fr-grid-row", visible=False) as send_area:
    with gr.Column(elem_id="send-area", visible=False) as send_area:
        with gr.Row(elem_classes="fr-grid-row"):
            # textbox = gr.Textbox(
            textbox = FrInput(
                show_label=False,
                lines=1,
                placeholder="Ecrivez votre premier message à l'arène ici",
                max_lines=7,
                # TODO: raise fr-col-md to 10 ?
                elem_classes="fr-col-12 fr-col-md-9",
                container=False,
                # not working
                # autofocus=True
            )
            send_btn = gr.Button(
                interactive=False,
                value="Envoyer",
                elem_classes="fr-btn fr-col-6 fr-col-md-1",
            )
            # FIXME: visible=false not working?
            # retry_btn = gr.Button(
            #     icon="assets/dsfr/icons/system/refresh-line.svg",
            #     value="",
            #     elem_classes="icon-blue fr-btn fr-btn--secondary",
            #     # elem_classes="fr-icon-refresh-line",
            #     visible=False,
            #     # render=False,
            #     scale=1,
            # )
        with gr.Row(elem_classes="fr-grid-row fr-grid-row--center"):
            # FIXME: visible=false not working?
            # TODO: griser le bouton "Terminer et donner mon avis" tant que les LLM n'ont pas fini d'écrire
            conclude_btn = gr.Button(
                value="Terminer et donner mon avis",
                elem_classes="fr-btn fr-col-12 fr-col-md-4",
                visible=False,
                interactive=False,
            )

    with gr.Group(elem_id="chat-area", visible=False) as chat_area:
        with gr.Row():
            for i in range(config.num_sides):
                label = "Modèle A" if i == 0 else "Modèle B"
                # with gr.Column():
                    # {likeable}
                    # placeholder
                    #         placeholder
                    # a placeholder message to display in the chatbot when it is empty. Centered vertically and horizontally in the Chatbot. Supports Markdown and HTML.
                chatbots[i] = gr.Chatbot(
                        # type="tuples",
                        # TODO:
                        type="messages",
                        elem_id=f"chatbot-{i}",
                        # min_width=
                        # height=
                        # Doesn't show because it always has at least our message
                        # Note: supports HTML, use it!
                        placeholder="<em>Veuillez écrire au modèle</em>",
                        # No difference
                        # bubble_full_width=False,
                        layout="panel",  # or "bubble"
                        likeable=False,
                        label=label,
                        # UserWarning: show_label has no effect when container is False.
                        show_label=False,
                        container=False,
                        elem_classes="chatbot",
                        # Should we show it?
                        show_copy_button=False,
                    )

    with gr.Column(visible=False, elem_classes="fr-container") as vote_area:
        gr.Markdown(value="## Quel modèle avez-vous préféré ?")
        with gr.Row():
            which_model_radio = gr.Radio(
                elem_classes="radio-tiles bolder",
                show_label=False,
                choices=[
                    ("Modèle A", "leftvote"),
                    ("Modèle B", "rightvote"),
                    ("Aucun des deux", "bothbad"),
                ],
            )
            # leftvote_btn = gr.Button(value="👈  A est mieux")
            # rightvote_btn = gr.Button(value="👉  B est mieux")
            # # tie_btn = gr.Button(value="🤝  Les deux se valent")
            # bothbad_btn = gr.Button(value="👎  Aucun des deux")

        # with gr.Column(visible=False, elem_classes="fr-container") as supervote_area:
        with gr.Column(visible=False) as supervote_area:

            # TODO: render=false?
            # TODO: move to another file?
            with gr.Column() as positive_supervote:
                gr.Markdown(
                    value="### Pourquoi ce choix de modèle ?\nSélectionnez autant de préférences que vous souhaitez"
                )
                # TODO: checkboxes tuple
                ressenti_checkbox = gr.CheckboxGroup(
                    [
                        "Impressionné·e",
                        "Complet",
                        "Facile à comprendre",
                        "Taille des réponses adaptées",
                    ],
                    label="ressenti",
                    show_label=False,
                    info="Ressenti général",
                )
                pertinence_checkbox = gr.CheckboxGroup(
                    [
                        "Consignes respectées",
                        "Cohérent par rapport au contexte",
                        "Le modèle ne s'est pas trompé",
                    ],
                    label="pertinence",
                    show_label=False,
                    info="Pertinence des réponses",
                )
                comprehension_checkbox = gr.CheckboxGroup(
                    [
                        "Syntaxe adaptée",
                        "Richesse du vocabulaire",
                        "Utilisation correcte des expressions",
                    ],
                    label="comprehension",
                    show_label=False,
                    info="Compréhension et expression",
                )
                originalite_checkbox = gr.CheckboxGroup(
                    ["Créatif", "Expressif", "Drôle"],
                    label="originalite",
                    info="Créativité et originalité",
                    show_label=False,
                )

            # TODO: render=false?
            # TODO: move to another file
            with gr.Column() as negative_supervote:
                gr.Markdown(
                    value="### Pourquoi êtes-vous insatisfait·e des deux modèles ?\nSélectionnez autant de préférences que vous souhaitez"
                )
                ressenti_checkbox = gr.CheckboxGroup(
                    [
                        "Trop court",
                        "Trop long",
                        "Pas utile",
                        "Nocif ou offensant",
                    ],
                    label="ressenti",
                    info="Ressenti général",
                    show_label=False,
                )
                pertinence_checkbox = gr.CheckboxGroup(
                    [
                        "Incohérentes par rapport au contexte",
                        "Factuellement incorrectes",
                        "Imprécises",
                    ],
                    label="pertinence",
                    info="Pertinence des réponses",
                    show_label=False,
                )
                comprehension_checkbox = gr.CheckboxGroup(
                    [
                        "Faible qualité de syntaxe",
                        "Pauvreté du vocabulaire",
                        "Mauvaise utilisation des expressions",
                    ],
                    label="comprehension",
                    info="Compréhension et expression",
                    show_label=False,
                )
                originalite_checkbox = gr.CheckboxGroup(
                    ["Réponses banales", "Réponses superficielles"],
                    label="originalite",
                    info="Créativité et originalité",
                    show_label=False,
                )

            supervote_checkboxes = [
                ressenti_checkbox,
                pertinence_checkbox,
                comprehension_checkbox,
                originalite_checkbox,
            ]

            comments_text = FrInput(
                # elem_classes="fr-input",
                label="Détails supplémentaires",
                show_label=True,
                # TODO:
                # info=,
                # autofocus=True,
                placeholder="Ajoutez plus de précisions ici",
            )

    with gr.Column(
        elem_classes="arena-footer fr-container--fluid", visible=False
    ) as buttons_footer:
        with gr.Row(elem_classes="fr-grid-row fr-container fr-mt-4w"):
            return_btn = gr.Button(
                elem_classes="fr-btn fr-btn--secondary fr-col-12 fr-col-md-1",
                value="Retour",
            )
            final_send_btn = gr.Button(
                elem_classes="fr-btn fr-col-12 fr-col-md-3 fr-col-offset-md-2",
                value="Envoyer mes préférences",
                interactive=False,
            )

    results_area = gr.HTML(visible=False, elem_classes="fr-container")

    with gr.Row(visible=False) as feedback_row:
        # dsfr: This should just be a normal link...
        # feedback_btns =
        gr.HTML(
            value="""
            <div class="fr-grid-row fr-grid-row--center fr-grid-row--gutters">
            <a class="fr-btn" href="https://adtk8x51mbw.eu.typeform.com/to/kiPl3JAL" >Donner mon avis sur l'arène</a>
            <a class="fr-btn fr-btn--secondary" href="../modeles">Liste des modèles</a>
            </div>
        """
        )

    # TODO: get rid
    temperature = gr.Slider(
        visible=False,
        # minimum=0.0,
        # maximum=1.0,
        value=0.7,
        # step=0.1,
        interactive=False,
        label="Temperature",
    )
    top_p = gr.Slider(
        visible=False,
        minimum=0.0,
        maximum=1.0,
        value=1.0,
        step=0.1,
        interactive=False,
        label="Top P",
    )
    max_output_tokens = gr.Slider(
        visible=False,
        minimum=16,
        maximum=2048,
        value=1024,
        step=64,
        interactive=False,
        label="Max output tokens",
    )

    # Register listeners
    def register_listeners():
        # Step 0

        # @gr.on(
        #     triggers=[accept_tos_checkbox.change, accept_waiver_checkbox.change],
        #     inputs=[accept_tos_checkbox, accept_waiver_checkbox],
        #     outputs=start_arena_btn,
        #     api_name=False,
        # )
        # def accept_tos_to_enter_arena(accept_tos_checkbox, accept_waiver_checkbox):
        #     # Enable if both checked
        #     return gr.update(
        #         interactive=(accept_tos_checkbox and accept_waiver_checkbox)
        #     )

        @start_arena_btn.click(
            inputs=[],
            outputs=[header, start_screen, stepper_block, mode_screen],
            api_name=False,
        )
        def enter_arena(request: gr.Request):
            # tos_accepted = accept_tos_checkbox
            # if tos_accepted:
            return (
                gr.HTML(header_html),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True),
            )
            # else:
            #     return (gr.skip(), gr.skip(), gr.skip())

        # Step 1

        @free_mode_btn.click(
            inputs=[],
            # js?
            outputs=[
                free_mode_btn,
                guided_mode_btn,
                send_area,
                guided_area,
                mode_screen,
            ],
            api_name=False,
        )
        def free_mode():
            return [
                gr.update(
                    elem_classes="fr-ml-auto " + mode_selection_classes + " selected"
                ),
                gr.update(elem_classes="fr-mr-auto " + mode_selection_classes),
                gr.update(visible=True),
                gr.update(visible=False),
                gr.update(elem_classes="fr-container send-area-enabled"),
            ]

        @guided_mode_btn.click(
            inputs=[],
            outputs=[
                free_mode_btn,
                guided_mode_btn,
                # send_area,
                guided_area,
                mode_screen,
            ],
            api_name=False,
            # TODO: scroll_to_output?
        )
        def guided_mode():
            # print(guided_mode_btn.elem_classes)
            if "selected" in guided_mode_btn.elem_classes:
                return [gr.skip() * 4]
            else:
                return [
                    gr.update(elem_classes="fr-ml-auto " + mode_selection_classes),
                    gr.update(
                        elem_classes="fr-mr-auto "
                        + mode_selection_classes
                        + " selected"
                    ),
                    # send_area
                    # gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(elem_classes="fr-container send-area-enabled"),
                ]

        # Step 1.1

        def set_guided_prompt(event: gr.EventData):
            chosen_guide = event.target.value
            if chosen_guide in [
                "variete",
                "regional",
                "pedagogie",
                "creativite",
                "registre",
                "maniere",
            ]:
                preprompts = config.preprompts_table[chosen_guide]
            else:
                logger.error("Type of guided prompt not listed")
            preprompt = preprompts[np.random.randint(len(preprompts))]
            return [gr.update(visible=True), gr.update(value=preprompt)]

        gr.on(
            triggers=[
                maniere.click,
                registre.click,
                regional.click,
                variete.click,
                pedagogie.click,
                creativite_btn.click,
            ],
            fn=set_guided_prompt,
            inputs=[],
            outputs=[send_area, textbox],
            api_name=False,
        )

        # Step 2

        @textbox.change(inputs=textbox, outputs=send_btn, api_name=False)
        def change_send_btn_state(textbox):
            if textbox == "":
                return gr.update(interactive=False)
            else:
                return gr.update(interactive=True)

        def enable_component():
            return gr.update(interactive=True)

        def goto_chatbot():
            # FIXME: tant que les 2 modèles n'ont pas répondu, le bouton "envoyer" est aussi inaccessible
            return (
                [
                    gr.update(
                        value="",
                        placeholder="Continuer à discuter avec les deux modèles",
                    )
                ]
                # stepper_block
                + [gr.update(value=stepper_html("Discussion avec les modèles", 2, 4))]
                # mode_screen
                + [gr.update(visible=False)]
                # chat_area
                + [gr.update(visible=True)]
                # send_btn
                + [gr.update(interactive=False)]
                # retry_btn
                # + [gr.update(visible=True)]
                # conclude_btn
                + [gr.update(visible=True, interactive=True)]
            )

        def send_msg(textbox, chatbot0, chatbot1):
            print(chatbot0)
            print(chatbot1)
            # history = [["user", textbox]]

            msg = gr.ChatMessage(role="user", content=textbox)
            # chatbots[0].append(msg)
            # chatbots[1].append(msg)
            chatbot0.append(msg)
            chatbot1.append(msg)

            
            return (chatbot0, chatbot1)
            # return chatbot1

        def bots_responses(chatbot0, chatbot1):

            msg = gr.ChatMessage(role="assistant", content="Yo")
            # chatbots[0].append(msg)
            # chatbots[1].append(msg)
            chatbot0.append(msg)
            chatbot1.append(msg)
            return (chatbot0, chatbot1)

        # gr.on(
        #     triggers=[textbox.submit, send_btn.click],
        #     fn=add_text,
        #     api_name=False,
        #     inputs=conversations_state + [textbox],
        #     # inputs=conversations_state + model_selectors + [textbox],
        #     outputs=conversations_state + chatbots,
        # ).then(
        gr.on(
            triggers=[textbox.submit, send_btn.click],
            fn=send_msg,
            api_name=False,
            inputs=[textbox] + chatbots,
            # inputs=conversations_state + model_selectors + [textbox],
            outputs=[chatbots[0], chatbots[1]],
        ).then(
            fn=goto_chatbot,
            inputs=[],
            outputs=(
                [textbox]
                + [stepper_block]
                + [mode_screen]
                + [chat_area]
                + [send_btn]
                # + [retry_btn]
                + [conclude_btn]
            ),
            # ).then(
            #     fn=bot_response_multi,
            #     inputs=conversations_state + [temperature, top_p, max_output_tokens],
            #     outputs=conversations_state + chatbots,
            #     api_name=False,
        ).then(
            fn=bots_responses,
            inputs=chatbots,
            outputs=[chatbots[0], chatbots[1]],
            api_name=False,
        ).then(
            fn=enable_component,
            inputs=[],
            outputs=[conclude_btn],
            api_name=False,
        )

        @conclude_btn.click(
            inputs=[],
            outputs=[stepper_block, chat_area, send_area, vote_area, buttons_footer],
            api_name=False,
            # TODO: scroll_to_output?
        )
        def show_vote_area():
            # return {
            #     conclude_area: gr.update(visible=False),
            #     chat_area: gr.update(visible=False),
            #     send_area: gr.update(visible=False),
            #     vote_area: gr.update(visible=True),
            # }
            # [conclude_area, chat_area, send_area, vote_area]
            return [
                gr.update(value=stepper_html("Évaluation des modèles", 3, 4)),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True),
            ]

        @which_model_radio.change(
            inputs=[which_model_radio],
            outputs=[
                supervote_area,
                positive_supervote,
                negative_supervote,
                final_send_btn,
            ],
            api_name=False,
        )
        def build_supervote_area(vote_radio):
            if vote_radio == "bothbad":
                return (
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(interactive=True),
                )
            else:
                return (
                    gr.update(visible=True),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(interactive=True),
                )

        # Step 3

        @return_btn.click(
            inputs=[],
            outputs=[stepper_block] + [vote_area]
            # + [supervote_area]
            + [chat_area] + [send_area] + [buttons_footer],
        )
        def return_to_chat():
            return (
                [gr.update(value=stepper_html("Discussion avec les modèles", 2, 4))]
                # vote_area
                + [gr.update(visible=False)]
                # supervote_area
                # + [gr.update(visible=False)]
                # chat_area
                + [gr.update(visible=True)]
                # send_area
                + [gr.update(visible=True)]
                # buttons_footer
                + [gr.update(visible=False)]
            )

        @final_send_btn.click(
            inputs=(
                [conversations_state[0]]
                + [conversations_state[1]]
                + [which_model_radio]
                + (supervote_checkboxes)
                + [comments_text]
            ),
            outputs=[
                stepper_block,
                vote_area,
                supervote_area,
                feedback_row,
                results_area,
                buttons_footer,
            ],
            api_name=False,
        )
        def vote_preferences(
            state0,
            state1,
            which_model_radio,
            ressenti_checkbox,
            pertinence_checkbox,
            comprehension_checkbox,
            originalite_checkbox,
            comments_text,
            request: gr.Request,
        ):
            # conversations_state = [state0, state1]

            details = {
                "chosen_model": which_model_radio,
                "ressenti": ressenti_checkbox,
                "pertinence": pertinence_checkbox,
                "comprehension": comprehension_checkbox,
                "originalite": originalite_checkbox,
                "comments": comments_text,
            }
            if which_model_radio in ["bothbad", "leftvote", "rightvote"]:
                logger.info("Voting " + which_model_radio)

                vote_last_response(
                    [state0, state1],
                    which_model_radio,
                    details,
                    request,
                )
            else:
                logger.error(
                    'Model selection was neither "bothbad", "leftvote" or "rightvote", got: '
                    + str(which_model_radio)
                )
            # model_a =  config.models_extra_info[state0.model_name.lower()]
            # model_b =  config.models_extra_info[state1.model_name.lower()]
            model_a = get_model_extra_info(state0.model_name, config.models_extra_info)
            model_b = get_model_extra_info(state1.model_name, config.models_extra_info)

            # TODO: Improve fake token counter: 4 letters by token: https://genai.stackexchange.com/questions/34/how-long-is-a-token
            model_a_tokens = count_output_tokens(
                state0.conv.roles, state0.conv.messages
            )
            model_b_tokens = count_output_tokens(
                state1.conv.roles, state1.conv.messages
            )
            # TODO:
            # request_latency_a = state0.conv.finish_tstamp - state0.conv.start_tstamp
            # request_latency_b = state1.conv.finish_tstamp - state1.conv.start_tstamp
            model_a_impact = get_llm_impact(
                model_a, state0.model_name, model_a_tokens, None
            )
            model_b_impact = get_llm_impact(
                model_b, state1.model_name, model_b_tokens, None
            )

            model_a_running_eq = running_eq(model_a_impact)
            model_b_running_eq = running_eq(model_b_impact)

            reveal_html = build_reveal_html(
                model_a=model_a,
                model_b=model_b,
                which_model_radio=which_model_radio,
                model_a_impact=model_a_impact,
                model_b_impact=model_b_impact,
                model_a_running_eq=model_a_running_eq,
                model_b_running_eq=model_b_running_eq,
            )
            return [
                gr.update(value=stepper_html("Révélation des modèles", 4, 4)),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True, value=reveal_html),
                gr.update(visible=False),
            ]

        # On reset go to mode selection mode_screen
        # gr.on(
        #     triggers=[retry_btn.click],
        #     api_name=False,
        #     # triggers=[clear_btn.click, retry_btn.click],
        #     fn=clear_history,
        #     inputs=conversations_state + chatbots + [textbox],
        #     # inputs=conversations_state + chatbots + model_selectors + [textbox],
        #     # List of objects to clear
        #     outputs=conversations_state + chatbots
        #     # + model_selectors
        #     + [textbox] + [chat_area] + [vote_area] + [supervote_area] + [mode_screen],
        # )

    register_listeners()
