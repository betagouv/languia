import gradio as gr


def stepper_html(title, step, total_steps):
    return f"""
    <div class="fr-stepper">
    <h2 class="fr-stepper__title">
        {title}
        <span class="fr-stepper__state">Étape {step} sur {total_steps}</span>
    </h2>
    <div class="fr-stepper__steps" data-fr-current-step="1" data-fr-steps="{total_steps}"></div>

</div>"""



# Step 0
# accept_tos_btn.click(accept_tos, inputs=[], outputs=[start_screen, mode_screen])
# TODO: fix js output
# accept_tos_btn.click(
#     accept_tos, inputs=[], outputs=[start_screen, mode_screen], js=accept_tos_js
# )


header_html = """
    <header role="banner" class="">
  <div class="fr-header__body">
    <div class="">
      <div class="fr-header__body-row">
        <div class="fr-header__brand fr-enlarge-link">
          <div class="fr-header__brand-top">
            <div class="fr-header__logo">
              <p class="fr-logo">
                République
                <br>Française
              </p>
            </div>
          </div>
          <div class="fr-header__service">
            <a href="/" title="Accueil - LANGU:IA">
              <p class="fr-header__service-title">LANGU:IA</p>
            </a>
            <p class="fr-header__service-tagline">L'arène francophone de classement de modèles de langage par préférences humaines</p>
          </div>
        </div>

        <div class="fr-header__tools">
          <div class="fr-badge fr-badge--info">
           Version Demo
          </div>
        </div>
      </div>
    </div>
  </div>

</header>
"""
