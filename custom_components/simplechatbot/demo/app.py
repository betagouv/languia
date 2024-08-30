
import gradio as gr
from gradio_simplechatbot import SimpleChatbot


example = SimpleChatbot().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        SimpleChatbot(label="Blank"),  # blank component
        SimpleChatbot(value=example, label="Populated"),  # populated component


if __name__ == "__main__":
    demo.launch()
