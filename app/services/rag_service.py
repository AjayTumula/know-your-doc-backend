from transformers import pipeline

summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
    return summarizer
