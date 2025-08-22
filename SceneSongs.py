# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0


import spacy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import warnings
from nltk.corpus import wordnet as wn
from collections import namedtuple
import nltk
nltk.download('wordnet')

# Suppress specific warnings from Spotipy
warnings.filterwarnings("ignore", category=UserWarning)

# Create a named tuple for song recommendations
SongRecommendation = namedtuple('SongRecommendation', ['title', 'artist', 'spotify_url', 'mood_score', 'match_reason'])

class SceneMusicRecommender:
    def __init__(self, spotify_client_id, spotify_client_secret, chosen_artists):
        """Initialize the recommender with Spotify credentials and NLP models."""
        self.nlp = spacy.load("en_core_web_sm")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=spotify_client_id, 
            client_secret=spotify_client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.chosen_artists = chosen_artists
        
        # Define mood mappings for different scene elements
        self.mood_mappings = {
            'locations': {
                'beach': ['peaceful', 'serene', 'waves', 'tropical'],
                'mountain': ['epic', 'majestic', 'vast', 'triumphant'],
                'city': ['urban', 'busy', 'rhythmic', 'modern'],
                'forest': ['mysterious', 'organic', 'natural', 'mystical'],
                'desert': ['minimal', 'expansive', 'empty', 'spiritual'],
                'space': ['atmospheric', 'ethereal', 'floating', 'cosmic'],
                'underwater': ['floating', 'mysterious', 'fluid', 'deep'],
                'castle': ['royal', 'epic', 'medieval', 'grand'],
                'ruins': ['ancient', 'mysterious', 'forgotten', 'ethereal']
            },
            'times': {
                'night': ['dark', 'mysterious', 'quiet', 'nocturnal'],
                'dawn': ['hopeful', 'beginning', 'light', 'awakening'],
                'dusk': ['melancholic', 'ending', 'transition', 'fading'],
                'day': ['bright', 'active', 'energetic', 'vibrant'],
                'twilight': ['magical', 'transitional', 'ethereal', 'mysterious']
            },
            'weather': {
                'rain': ['melancholic', 'peaceful', 'gentle', 'pitter-patter'],
                'storm': ['dramatic', 'intense', 'powerful', 'thunderous'],
                'snow': ['quiet', 'soft', 'delicate', 'crystalline'],
                'sunny': ['bright', 'warm', 'positive', 'radiant'],
                'foggy': ['mysterious', 'ethereal', 'muted', 'hazy'],
                'windy': ['dynamic', 'sweeping', 'flowing', 'whistling']
            },
            'emotions': {
                'happy': ['joyful', 'uplifting', 'bright', 'celebratory'],
                'sad': ['melancholic', 'emotional', 'deep', 'sorrowful'],
                'angry': ['intense', 'dramatic', 'powerful', 'aggressive'],
                'peaceful': ['calm', 'serene', 'gentle', 'tranquil'],
                'tense': ['suspense', 'dramatic', 'dark', 'anxious'],
                'nostalgic': ['emotional', 'bittersweet', 'remembrance', 'longing'],
                'afraid': ['tense', 'dark', 'scary', 'frightening'],
                'triumphant': ['victorious', 'uplifting', 'powerful', 'grand'],
                'lonely': ['melancholic', 'isolated', 'empty', 'solitary']
            },
            'actions': {
                'running': ['fast', 'chase', 'intense', 'urgent'],
                'fighting': ['action', 'dramatic', 'battle', 'aggressive'],
                'kissing': ['romantic', 'emotional', 'intimate', 'tender'],
                'crying': ['sad', 'emotional', 'deep', 'heartbreaking'],
                'laughing': ['happy', 'light', 'joyful', 'playful'],
                'waiting': ['suspense', 'tension', 'quiet', 'anticipation'],
                'searching': ['mysterious', 'quest', 'seeking', 'determined'],
                'dancing': ['rhythmic', 'joyful', 'flowing', 'energetic'],
                'sleeping': ['peaceful', 'quiet', 'dreamy', 'gentle']
            },
            'genres': {
                'romance': ['romantic', 'emotional', 'intimate', 'loving'],
                'horror': ['scary', 'tense', 'dark', 'suspenseful'],
                'action': ['intense', 'dramatic', 'powerful', 'energetic'],
                'drama': ['emotional', 'deep', 'serious', 'powerful'],
                'fantasy': ['magical', 'epic', 'mystical', 'otherworldly'],
                'scifi': ['futuristic', 'electronic', 'otherworldly', 'cosmic']
            }
        }

    def get_synonyms(self, word):
        """Get synonyms for a word using WordNet."""
        synonyms = set()
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return synonyms

    def analyze_scene(self, scene_description):
        """Analyze scene description to extract mood, location, action, and atmosphere."""
        doc = self.nlp(scene_description.lower())
        
        elements = {k: [] for k in self.mood_mappings.keys()}
        
        # Check each word against our mood mappings
        for token in doc:
            for category, mappings in self.mood_mappings.items():
                for key in mappings:
                    if key in token.text or any(syn in token.text for syn in self.get_synonyms(key)):
                        elements[category].append(key)
        
        mood_words = [token.text for token in doc if token.pos_ in ["ADJ", "VERB", "ADV"]]
        sentiment = sum(token.sentiment for token in doc if hasattr(token, 'sentiment'))
        
        return {"elements": elements, "mood_words": mood_words, "sentiment": sentiment}

    def create_music_queries(self, analysis):
        queries = []
        match_reasons = []
        
        for category, items in analysis['elements'].items():
            for item in items:
                if item in self.mood_mappings[category]:
                    queries.extend(self.mood_mappings[category][item])
                    match_reasons.append(f"Matches {category}: {item}")
        
        for mood in analysis['mood_words']:
            queries.append(mood)
            match_reasons.append(f"Matches mood: {mood}")
        
        sentiment = analysis['sentiment']
        if sentiment > 0:
            queries.extend(['uplifting', 'positive', 'bright'])
            match_reasons.append("Matches positive sentiment")
        elif sentiment < 0:
            queries.extend(['dark', 'somber', 'intense'])
            match_reasons.append("Matches negative sentiment")
        
        return list(set(queries)), match_reasons

    def find_matching_songs(self, query, match_reason, limit=3):
        """Find matching songs for a query."""
        try:
            results = self.sp.search(q=query, type='track', limit=50)
            
            matching_tracks = []
            for track in results['tracks']['items']:
                if any(artist['name'] in self.chosen_artists for artist in track['artists']):
                    features = self.sp.audio_features(track['id'])[0]
                    if features:
                        mood_score = (
                            features['valence'] * 0.3 +
                            features['energy'] * 0.3 +
                            features['instrumentalness'] * 0.2 +
                            features['acousticness'] * 0.2
                        )
                        
                        recommendation = SongRecommendation(
                            title=track['name'],
                            artist=track['artists'][0]['name'],
                            spotify_url=f"https://open.spotify.com/track/{track['id']}",
                            mood_score=mood_score,
                            match_reason=match_reason
                        )
                        matching_tracks.append(recommendation)
            
            matching_tracks.sort(key=lambda x: x.mood_score, reverse=True)
            return matching_tracks[:limit]
        except Exception as e:
            print(f"Error finding matching songs: {str(e)}")
            return []

    def recommend_for_scene(self, scene_description):
        analysis = self.analyze_scene(scene_description)
        queries, match_reasons = self.create_music_queries(analysis)
        
        seen_songs = set()
        recommendations = []
        
        for query, reason in zip(queries, match_reasons):
            tracks = self.find_matching_songs(query, reason)
            for track in tracks:
                if track.title not in seen_songs:
                    recommendations.append(track)
                    seen_songs.add(track.title)
        
        recommendations.sort(key=lambda x: x.mood_score, reverse=True)
        return recommendations


# Example usage:
spotify_client_id = ""
spotify_client_secret = ""

# List of film composers and ambient artists
chosen_artists = [
    "Hans Zimmer",
    "John Williams",
    "Ennio Morricone",
    "Max Richter",
    "Ludovico Einaudi",
    "Philip Glass",
    "James Horner",
    "Ramin Djawadi",
    "Gustavo Santaolalla",
    "Nils Frahm",
    "Yannick Nézet-Séguin",
    "Hildur Guðnadóttir",
    "Bear McCreary",
    "Thomas Newman",
    "Ólafur Arnalds",
    "Johann Johannsson",
    "Danny Elfman",
    "Klaus Badelt",
    "Igor Stravinsky",
    "Ludwig van Beethoven",
    "Wolfgang Amadeus Mozart",
    "Johann Sebastian Bach",
    "Frédéric Chopin",
    "Claude Debussy",
    "Richard Wagner",
    "Gustav Mahler",
    "Antonín Dvořák",
    "Sergei Rachmaninoff",
    "Camille Saint-Saëns",
    "Philip Sparke",
    "Arvo Pärt",
    "Tan Dun",
    "Michael Giacchino",
    "Alexandre Desplat",
    "Dario Marianelli",
    "John Barry",
    "Vangelis",
    "M83"
]

# Initialize the recommender
recommender = SceneMusicRecommender(spotify_client_id, spotify_client_secret, chosen_artists)

# Example scene description
scene_description = """
Ethan sat on the weathered park bench, watching as leaves danced in the crisp autumn breeze, their vibrant colors a stark contrast to the gray cloud hanging over his heart. He remembered the way Clara laughed, her eyes sparkling with a warmth that made the world around him seem brighter. They had shared fleeting moments—soft conversations that lingered in the air, the brush of hands during a casual joke, and the electric thrill of unspoken words. Yet, each time he hesitated, fearing the risk of vulnerability more than the ache of unfulfilled longing. 

When she finally left for the city, chasing her dreams, he felt a hollow void where his courage should have been. Days turned into weeks, and those stolen moments replayed in his mind like a bittersweet melody, a constant reminder of the "what ifs" that haunted him. Friends told him to reach out, to let her know how he felt, but he remained silent, trapped in his own indecision. Now, as he watched couples stroll hand-in-hand, laughter ringing through the air, he realized that he had let the opportunity slip away, buried under the weight of his fears. The regret settled in like an unwelcome guest, and with it came the painful understanding that sometimes, the hardest battles are fought within ourselves."""

# Get recommendations
recommendations = recommender.recommend_for_scene(scene_description)
print(recommendations)
