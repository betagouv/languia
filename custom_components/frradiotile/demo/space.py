
import gradio as gr
from app import demo as app
import os

_docs = {'FrRadioTile': {'description': 'Creates a set of (string or numeric type) radio buttons of which only one can be selected.\n', 'members': {'__init__': {'choices': {'type': 'list[str | int | float | tuple[str, str | int | float]]\n    | None', 'default': 'None', 'description': 'A list of string or numeric options to select from. An option can also be a tuple of the form (name, value), where name is the displayed name of the radio button and value is the value to be passed to the function, or returned by the function.'}, 'value': {'type': 'str | int | float | Callable | None', 'default': 'None', 'description': 'The option selected by default. If None, no option is selected by default. If callable, the function will be called whenever the app loads to set the initial value of the component.'}, 'type': {'type': 'str', 'default': '"value"', 'description': 'Type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'info': {'type': 'str | None', 'default': 'None', 'description': 'Additional component description.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' number of seconds while the client connection is open. Has no effect otherwise. The event can be accessed (e.g. to cancel it) via this component's .load_event attribute."}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative width compared to adjacent Components in a Row. For example, if Component A has scale=2, and Component B has scale=1, A will be twice as wide as B. Should be an integer.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, choices in this radio group will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | None', 'default': 'None', 'description': 'if assigned, will be used to assume identity across a re-render. Components that have the same key across a re-render will have their value preserved.'}}, 'postprocess': {'value': {'type': 'str | int | float | None', 'description': 'Expects a `str | int | float` corresponding to the value of the radio button to be selected'}}, 'preprocess': {'return': {'type': 'str | int | float | None', 'description': 'Passes the value of the selected radio button as a `str | int | float`, or its index as an `int` into the function, depending on `type`.'}, 'value': None}}, 'events': {'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the FrRadioTile. Uses event data gradio.SelectData to carry `value` referring to the label of the FrRadioTile, and `selected` to refer to state of the FrRadioTile. See EventData documentation on how to use this event data'}, 'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the FrRadioTile changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the FrRadioTile.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'FrRadioTile': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_frradiotile`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_frradiotile
```

## Usage

```python

import gradio as gr
from gradio_frradiotile import FrRadioTile


example = FrRadioTile().example_value()

demo = gr.Interface(
    lambda x:x,
    FrRadioTile(),  # interactive version of your component
    FrRadioTile(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `FrRadioTile`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["FrRadioTile"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["FrRadioTile"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the value of the selected radio button as a `str | int | float`, or its index as an `int` into the function, depending on `type`.
- **As output:** Should return, expects a `str | int | float` corresponding to the value of the radio button to be selected.

 ```python
def predict(
    value: str | int | float | None
) -> str | int | float | None:
    return value
```
""", elem_classes=["md-custom", "FrRadioTile-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          FrRadioTile: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
