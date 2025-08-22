# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from gensim import corpora
from gensim.models import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
from collections import Counter
import logging
from transformers import pipeline

# Set up logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class TextAnalyzer:
    def __init__(self, max_segment_length=1000, num_themes=5):
        self.max_segment_length = max_segment_length
        self.num_themes = num_themes
        self.vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, stop_words='english')
        self.sentiment_pipeline = pipeline("sentiment-analysis")

    def process_text(self, text):
        # Process the entire text
        doc = nlp(text)
        
        # Segment the text
        segments = self.segment_text(doc)
        
        # Analyze each segment
        analyzed_segments = [self.analyze_segment(segment) for segment in segments]
        
        return analyzed_segments

    def segment_text(self, doc):
        segments = []
        current_segment = []
        current_length = 0
        current_characters = set()
        current_location = None

        for sent in doc.sents:
            # Check for new characters or locations
            new_characters = set([ent.text for ent in sent.ents if ent.label_ == "PERSON"])
            new_location = next((ent.text for ent in sent.ents if ent.label_ == "LOC"), None)

            # If there's a significant change, start a new segment
            if (len(new_characters - current_characters) > 1 or 
                (new_location and new_location != current_location) or 
                current_length > self.max_segment_length):
                if current_segment:
                    segments.append(nlp(" ".join(current_segment)))
                current_segment = []
                current_length = 0
                current_characters = set()
                current_location = None

            current_segment.append(sent.text)
            current_length += len(sent)
            current_characters.update(new_characters)
            if new_location:
                current_location = new_location

        if current_segment:
            segments.append(nlp(" ".join(current_segment)))

        return segments

    def analyze_segment(self, doc):
        # Basic analysis
        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        
        # Named Entity Recognition
        entities = Counter((ent.text, ent.label_) for ent in doc.ents)
        
        # Part-of-speech patterns
        pos_patterns = Counter(token.pos_ for token in doc)
        
        # Dependency patterns
        dep_patterns = Counter(token.dep_ for token in doc)
        
        # Topic Modeling
        tokens_for_lda = [token.lemma_ for token in doc if token.lemma_.lower() not in STOPWORDS and token.is_alpha]
        dictionary = corpora.Dictionary([tokens_for_lda])
        corpus = [dictionary.doc2bow(tokens_for_lda)]
        lda_model = LdaModel(corpus, num_topics=self.num_themes, id2word=dictionary, passes=15)
        topics = lda_model.print_topics()
        
        # Sentiment analysis using Hugging Face Transformers
        sentiment = self.analyze_sentiment(doc.text)
        
        return {
            'text': doc.text,
            'tokens': tokens,
            'lemmas': lemmas,
            'named_entities': dict(entities),
            'pos_patterns': dict(pos_patterns),
            'dep_patterns': dict(dep_patterns),
            'topics': topics,
            'sentiment': sentiment
        }

    def analyze_sentiment(self, text):
        result = self.sentiment_pipeline(text[:512])[0]  # Limit to 512 tokens due to model constraints
        return {
            'label': result['label'],
            'score': result['score']
        }

def read_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Example usage
if __name__ == "__main__":
    file_path = "./Data/text.txt"
    text = read_text(file_path)
    
    analyzer = TextAnalyzer()
    analyzed_segments = analyzer.process_text(text)
    
    for i, segment in enumerate(analyzed_segments):
        print(f"\nSegment {i+1}:")
        print(f"Text: {segment['text'][:100]}...")  # Print first 100 characters
        print(f"Named Entities: {segment['named_entities']}")
        print(f"Top Topic: {segment['topics'][0]}")
        print(f"Sentiment: {segment['sentiment']['label']} (Score: {segment['sentiment']['score']:.4f})")
