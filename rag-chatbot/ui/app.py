# ui/app.py
"""
File: app.py
Gradio interface for the RAG chatbot.
"""

import gradio as gr
from src.chatbot import chatbot_response

def chat_interface(query):
    return chatbot_response(query)

iface = gr.Interface(fn=chat_interface,
                     inputs="text",
                     outputs="text",
                     title="RAG Chatbot",
                     description="Ask a question and get context-informed answers!")
                     
if __name__ == "__main__":
    iface.launch()
