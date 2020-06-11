from transformers import pipeline

# Ready to Use Pipelines for inference
pipes = {
    "qa": pipeline(
        "question-answering"
    ),  # print(nlp(question="What is extractive question answering?", context=context))
    "tg": pipeline(
        "text-generation", "distilgpt2"
    ),  # print(text_generator("As far as I am concerned, I will", max_length=50))
    "ne": pipeline("ner", grouped_entities=True),  # print(nlp(sequence))
    # "sm": pipeline("summarization"),  # print(summarizer(ARTICLE, max_length=130, min_length=30))
}


class AI:
    def __init__(
        self, pipes=pipes,
    ):
        self.pipes = pipes

    def generate(self, doc, max_length=5000, min_length=0):
        """
        Generates text
        """
        return self.pipes["tg"](doc, max_length=max_length, min_length=min_length)

    def mark_entities(self, doc):
        """
        marks entities in document
        """
        return self.pipes["ne"](doc)

    def answer(self, question=None, context=None):
        """
        answers a question in the context of the document
        """
        return self.pipes["qa"](question=question, context=context)
