# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import spacy
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import io
from pydub import AudioSegment
import warnings
from nltk.corpus import wordnet as wn  # Import WordNet for synonyms

# Suppress specific warnings from Spotipy
warnings.filterwarnings("ignore", category=UserWarning)

class ImmersiveStorytellingEngine:
    def __init__(self, spotify_client_id, spotify_client_secret, chosen_artists):
        self.nlp = spacy.load("en_core_web_sm")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=spotify_client_id, 
            client_secret=spotify_client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.chosen_artists = chosen_artists  # List of chosen artists

    def get_synonyms(self, word):
        """Retrieve synonyms for a given word using WordNet."""
        synonyms = set()
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        return synonyms

    def analyze_text(self, text):
        """Analyze the provided text to extract mood, entities, and topics."""
        doc = self.nlp(text)
        
        mood_words = [token.text for token in doc if token.pos_ in ["ADJ", "NOUN"]]
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        topics = list(set(chunk.text for chunk in doc.noun_chunks))
        
        return {
            "mood": mood_words,
            "entities": entities,
            "topics": topics
        }

    def create_music_queries(self, analysis):
        """Create multiple music search queries based on topics and synonyms."""
        queries = []
        
        # Add general mood/theme-related keywords
        mood_keywords = ["regret", "sorrow", "nostalgia", "sad", "melancholic", "bittersweet","Exploration",
"Power",
"Identity",
"Chaos",
"Conspiracy",
"Technology",
"Morality",
"Reality",
"Humanity"]
        
        # Extract key topics and create different queries
        for topic in analysis['topics']:
            queries.append(f"{topic} soundtrack")
            # Get synonyms for each topic
            for synonym in self.get_synonyms(topic):
                queries.append(f"{synonym} soundtrack")
        
        # Add mood keywords to queries
        for keyword in mood_keywords:
            queries.append(f"{keyword} soundtrack")
        
        # Add a fallback query if no specific topics found
        queries.append("soundtrack")
        
        return queries

    def find_music(self, query):
        """Search for music tracks using the Spotify API."""
        results = self.sp.search(q=query, type='track', limit=50)  # Limit set to 50

        # Filter tracks based on the chosen artists
        filtered_tracks = [
            track for track in results['tracks']['items']
            if track['preview_url'] is not None and 
            any(artist['name'] in self.chosen_artists for artist in track['artists'])  # Check if the artist is in chosen artists
        ]

        # Return the preview URL of the first matching track, if any
        if filtered_tracks:
            return filtered_tracks[0]['id']  # Return the track ID for further analysis
            
        return None

    def analyze_song_mood(self, track_id):
        """Get audio features for a song and analyze mood."""
        features = self.sp.audio_features(track_id)[0]
        
        # You can adjust these thresholds based on your mood criteria
        if features:
            valence = features['valence']  # Measure of positivity
            energy = features['energy']  # Measure of energy
            return valence, energy
        return None, None

    def get_music_from_url(self, music_url):
        """Fetch music from the provided URL and convert it to an AudioSegment."""
        if music_url:
            response = requests.get(music_url)
            if response.status_code == 200:
                music_data = io.BytesIO(response.content)
                music = AudioSegment.from_file(music_data, format="mp3")
                return music
            else:
                print(f"Error fetching music: {response.status_code}")
        return None

    def process_story(self, text):
        """Process the provided story text to analyze it and find matching music."""
        analysis = self.analyze_text(text)
        music_queries = self.create_music_queries(analysis)

        print(f"Searching for music...")  # Debugging output

        for query in music_queries:
            print(f"Trying query: {query}")
            track_id = self.find_music(query)

            if track_id:
                valence, energy = self.analyze_song_mood(track_id)

                # Simple mood matching logic
                if valence < 0.5:  # Example threshold for sadness
                    music_url = f"https://open.spotify.com/track/{track_id}"
                    print(f"Found suitable music: {music_url}")
                    break  # Exit the loop if we find a matching song
            else:
                print(f"No music found for query: {query}")

        if not track_id:
            print("No suitable music found after all queries.")




if __name__ == "__main__":
    # Replace these with your actual Spotify API credentials
  spotify_client_id = ""
  spotify_client_secret = ""
    
  chosen_artists = ["Drake", "The Weeknd","Adele", "Coldplay", "Hans Zimmer", "Nicholas Britell", "Gustavo Santaolalla"]  # Add your desired artist names here
    
  engine = ImmersiveStorytellingEngine(spotify_client_id, spotify_client_secret, chosen_artists)
    
  story = """
  In the year 2145, humanity had colonized Mars, but the discovery of an ancient alien artifact buried beneath the surface unleashed a torrent of chaos. As scientists scrambled to unlock its secrets, a brilliant yet reclusive engineer named Mira was drawn into a conspiracy that threatened not only the Martian colony but the very fabric of reality itself. The artifact pulsed with an otherworldly energy, distorting time and space, and whispering promises of untold power to those who dared to wield it. With her past haunting her and a mysterious figure pursuing her, Mira found herself racing against time to prevent the artifact from falling into the wrong hands. As she navigated treacherous alliances and moral dilemmas, she grappled with the question of what it truly meant to be human in a world where technology blurred the lines between creation and destruction.
    """
    
  engine.process_story(story)

# if __name__ == "__main__":
#     # Replace these with your actual API credentials
#     spotify_client_id = ""
#     spotify_client_secret = ""
#     elevenlabs_api_key = ""
    
#     engine = ImmersiveStorytellingEngine(spotify_client_id, spotify_client_secret, elevenlabs_api_key)
    
#     story = """
#     As the sun set over the misty mountains, casting long shadows across the valley, 
#     John felt a surge of excitement. The epic journey was about to begin.
#     """
    
#     engine.process_story(story)

