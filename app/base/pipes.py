from transformers import pipeline

# Ready to Use Pipelines for inference
pipes = {
    "qa": pipeline(
        "question-answering"
    ),  # print(nlp(question="What is extractive question answering?", context=context))
    "fm": pipeline(
        "fill-mask"
    ),  # print(nlp(f"HuggingFace is creating a {nlp.tokenizer.mask_token} that the community uses."))
    "tg": pipeline(
        "text-generation", "distilgpt2"
    ),  # print(text_generator("As far as I am concerned, I will", max_length=50))
    "ne": pipeline("ner", grouped_entities=True),  # print(nlp(sequence))
    # "sm": pipeline("summarization"),  # print(summarizer(ARTICLE, max_length=130, min_length=30))
    "tr": pipeline(
        "translation_en_to_de"
    ),  # print(translator("Hugging Face is a technology company based in New York and Paris", max_length=40))
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

    def summarize(self, doc, max_length=50, min_length=10):
        """
        summarizes a document
        """
        return self.pipes["sm"](doc, max_length=max_length, min_length=min_length)

    def translate(self, doc, from_lang="en", to_lang="de"):
        """
        translates a document from from_lang to to_lang
        """
        return self.pipes["tr"](doc)

    def answer(self, question=None, context=None):
        """
        answers a question in the context of the document
        """
        return self.pipes["qa"](question=question, context=context)

    def fill(self, doc):
        """
        fills in masked tokens in document
        """
        return self.pipes["fm"](doc)
