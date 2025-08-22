# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import spacy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import warnings
from nltk.corpus import wordnet as wn
import PyPDF2
import re
from collections import namedtuple
import nltk
nltk.download('wordnet')

# Suppress specific warnings from Spotipy
warnings.filterwarnings("ignore", category=UserWarning)

# Create a named tuple for song recommendations
SongRecommendation = namedtuple('SongRecommendation', ['title', 'artist', 'spotify_url', 'mood_score'])

class BookMusicRecommender:
    def __init__(self, spotify_client_id, spotify_client_secret, chosen_artists):
        """Initialize the recommender with Spotify credentials and NLP models."""
        self.nlp = spacy.load("en_core_web_sm")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=spotify_client_id, 
            client_secret=spotify_client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.chosen_artists = chosen_artists
        
    def extract_paragraphs_from_pdf(self, pdf_path):
        """Extract paragraphs from a PDF file."""
        paragraphs = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    
                    # Split text into paragraphs (adjust the regex pattern as needed)
                    page_paragraphs = re.split(r'\n\s*\n', text)
                    
                    # Filter out empty paragraphs and clean up whitespace
                    page_paragraphs = [p.strip() for p in page_paragraphs if p.strip()]
                    paragraphs.extend(page_paragraphs)
                    
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return []
            
        return paragraphs

    def get_synonyms(self, word):
        """Get synonyms for a word using WordNet."""
        synonyms = set()
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return synonyms

    def analyze_text(self, text):
        """Analyze text to extract mood, entities, and topics."""
        doc = self.nlp(text)
        
        # Extract relevant linguistic features
        mood_words = [token.text for token in doc if token.pos_ in ["ADJ", "VERB", "ADV"]]
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        topics = list(set(chunk.text for chunk in doc.noun_chunks))
        
        # Perform sentiment analysis using spaCy's built-in features
        sentiment = sum(token.sentiment for token in doc if hasattr(token, 'sentiment') and token.sentiment != 0)
        
        return {
            "mood_words": mood_words,
            "entities": entities,
            "topics": topics,
            "sentiment": sentiment
        }

    def create_music_queries(self, analysis):
        """Create search queries based on text analysis."""
        queries = []
        
        # Add topic-based queries
        for topic in analysis['topics']:
            queries.append(f"{topic}")
            # Add queries with synonyms
            for synonym in self.get_synonyms(topic):
                queries.append(f"{synonym}")
        
        # Add mood-based queries
        for mood in analysis['mood_words']:
            queries.append(f"{mood}")
        
        # Add entity-based queries
        for entity, label in analysis['entities']:
            if label in ['PERSON', 'EVENT', 'ORG']:
                queries.append(f"{entity}")
        
        # Add sentiment-based queries
        sentiment = analysis['sentiment']
        if sentiment > 0:
            queries.extend(['uplifting', 'joyful', 'happy'])
        elif sentiment < 0:
            queries.extend(['melancholic', 'sad', 'dark'])
        
        return list(set(queries))  # Remove duplicates

    def find_matching_songs(self, query, limit=3):
        """Find matching songs for a query."""
        try:
            results = self.sp.search(q=query, type='track', limit=50)
            
            matching_tracks = []
            for track in results['tracks']['items']:
                if track['preview_url'] and any(artist['name'] in self.chosen_artists for artist in track['artists']):
                    # Get audio features for mood analysis
                    features = self.sp.audio_features(track['id'])[0]
                    if features:
                        mood_score = (features['valence'] + features['energy']) / 2
                        
                        recommendation = SongRecommendation(
                            title=track['name'],
                            artist=track['artists'][0]['name'],
                            spotify_url=f"https://open.spotify.com/track/{track['id']}",
                            mood_score=mood_score
                        )
                        matching_tracks.append(recommendation)
            
            # Sort by mood score and return top matches
            matching_tracks.sort(key=lambda x: x.mood_score, reverse=True)
            return matching_tracks[:limit]
        except Exception as e:
            print(f"Error finding matching songs: {str(e)}")
            return []

    def process_book(self, pdf_path, output_file="recommendations.txt"):
        """Process entire book and generate recommendations."""
        paragraphs = self.extract_paragraphs_from_pdf(pdf_path)
        
        if not paragraphs:
            print("No paragraphs found in the PDF file.")
            return
            
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, paragraph in enumerate(paragraphs, 1):
                if len(paragraph.split()) < 20:  # Skip very short paragraphs
                    continue
                    
                print(f"\nProcessing paragraph {i} of {len(paragraphs)}...")
                f.write(f"\n{'='*80}\nParagraph {i}:\n{'='*80}\n")
                f.write(f"{paragraph}\n\nRecommended Songs:\n{'-'*50}\n")
                
                # Analyze paragraph
                analysis = self.analyze_text(paragraph)
                queries = self.create_music_queries(analysis)
                
                # Track unique songs to avoid duplicates
                seen_songs = set()
                recommendations = []
                
                # Try different queries until we find enough unique songs
                for query in queries:
                    if len(recommendations) >= 3:
                        break
                        
                    matches = self.find_matching_songs(query)
                    for match in matches:
                        if match.title not in seen_songs and len(recommendations) < 3:
                            seen_songs.add(match.title)
                            recommendations.append(match)
                
                # Write recommendations
                if recommendations:
                    for j, rec in enumerate(recommendations, 1):
                        f.write(f"{j}. \"{rec.title}\" by {rec.artist}\n")
                        f.write(f"   Spotify URL: {rec.spotify_url}\n")
                        f.write(f"   Mood Score: {rec.mood_score:.2f}\n\n")
                else:
                    f.write("No matching songs found for this paragraph.\n\n")
                
                f.flush()  # Ensure writing to file immediately
# Spotify credentials - replace with your own
spotify_client_id = ""
spotify_client_secret = ""

# List of artists to choose from
chosen_artists = [
    "Hans Zimmer", "Max Richter", "Ludovico Einaudi", 
    "Johann Johannsson", "Ólafur Arnalds", "Nicholas Britell",
    "Gustavo Santaolalla", "Philip Glass", "Thomas Newman",
    "Nils Frahm", "Jon Hopkins", "Joep Beving"
]

# Initialize and run the recommender
recommender = BookMusicRecommender(spotify_client_id, spotify_client_secret, chosen_artists)
output_file = "book_recommendations.txt"
recommender.process_book(filename, output_file)

# Download the recommendations file
files.download(output_file)
