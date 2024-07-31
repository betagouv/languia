
import gradio as gr
from gradio_customchatbot import CustomChatbot


example = CustomChatbot().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        CustomChatbot(label="Blank"),  # blank component
        CustomChatbot(value=example, label="Populated"),  # populated component


if __name__ == "__main__":
    demo.launch()
