
import gradio as gr
from gradio_frinput import FrInput


example = FrInput().example_value()

demo = gr.Interface(
    lambda x:x,
    FrInput(),  # interactive version of your component
    FrInput(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
