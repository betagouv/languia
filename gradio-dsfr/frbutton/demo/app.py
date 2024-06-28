
import gradio as gr
from gradio_frbutton import FrButton


example = FrButton().example_value()

demo = gr.Interface(
    lambda x:x,
    FrButton(),  # interactive version of your component
    FrButton(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
