
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
