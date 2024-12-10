import requests

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()



API_KEY = os.getenv("LASTFM_API_KEY")

if not API_KEY:
    raise ValueError("API-Schlüssel nicht gefunden. Bitte Umgebungsvariable setzen.")

def generate_artist_queries(artist_name):
    """Generates variations of the artist name by splitting on symbols like &, ,, ;."""
    if not artist_name:
        return []
    queries = [artist_name.strip()]  # Include the whole name
    for symbol in ['&', ',', ';']:
        if symbol in artist_name:
            before_symbol = artist_name.split(symbol)[0].strip()
            queries.append(before_symbol)
    return list(set(queries))  # Remove duplicates

def get_similar_tracks(song_name, artist_name=None, limit=50):
    """Fetch similar tracks for a given song and artist."""
    url = "http://ws.audioscrobbler.com/2.0/"
    recommendations = []
    artist_queries = generate_artist_queries(artist_name)

    for query in artist_queries:
        params = {
            'method': 'track.getsimilar',
            'track': song_name,
            'artist': query,
            'api_key': API_KEY,
            'format': 'json',
        }
        response = requests.get(url, params=params)
        try:
            data = response.json()
        except Exception:
            continue
        
        if 'similartracks' in data and data['similartracks'].get('track'):
            similar_tracks = data['similartracks']['track']
            recommendations.extend([
                {'title': track['name'], 'artist': track['artist']['name']}
                for track in similar_tracks
            ])
            if len(recommendations) >= limit:
                return recommendations[:limit]  # Truncate to limit
    return recommendations[:limit]  # Return up to the limit

def search_alternative_tracks(song_name, artist_name=None):
    """Search for alternative tracks."""
    url = "http://ws.audioscrobbler.com/2.0/"
    artist_queries = generate_artist_queries(artist_name)
    alternatives = []

    for query in artist_queries:
        params = {
            'method': 'track.search',
            'track': f"{song_name} {query}",
            'api_key': API_KEY,
            'format': 'json',
            'limit': 5
        }
        response = requests.get(url, params=params)
        try:
            data = response.json()
        except Exception:
            continue
        
        if 'results' in data and 'trackmatches' in data['results']:
            track_matches = data['results']['trackmatches']['track']
            if isinstance(track_matches, dict):  # Handle single result
                track_matches = [track_matches]
            alternatives.extend([
                {'title': track['name'], 'artist': track['artist']} for track in track_matches
            ])
    return alternatives

def contains_remix_keywords(title):
    """Check if the title contains remix-related keywords."""
    remix_keywords = ["remix", "version", "extended", "radio edit", "club mix", "reprise"]
    return any(keyword in title.lower() for keyword in remix_keywords)

def prioritize_remixes(tracks):
    """Prioritize tracks that contain remix-related keywords."""
    remix_keywords = ["remix", "version", "extended", "radio edit", "club mix", "reprise"]

    def remix_priority(track):
        title = track['title'].lower()
        if any(keyword in title for keyword in remix_keywords):
            return 0  # Higher priority for remixes
        return 1  # Lower priority for others

    return sorted(tracks, key=remix_priority)

def filter_duplicates(tracks):
    """Filters out duplicate tracks based on title and artist."""
    seen = set()
    unique_tracks = []
    for track in tracks:
        identifier = (track['title'].strip().lower(), track['artist'].strip().lower())
        if identifier not in seen:
            seen.add(identifier)
            unique_tracks.append(track)
    return unique_tracks

def search_recursive_alternatives(alternatives, limit=20):
    """Recursively searches for similar songs to alternatives until successful or exhausted."""
    for alternative in alternatives:
        recs = get_similar_tracks(alternative['title'], alternative['artist'], limit)
        if recs:
            return recs
    return []

def try_alternative_spellings(song_name, artist_name, alternative_spellings):
    """Try alternative spellings of the song name."""
    for alternative in alternative_spellings:
        recs = search_alternative_tracks(alternative, artist_name)
        if recs:
            recs = filter_duplicates(recs)  # Ensure no duplicates
            recs = prioritize_remixes(recs)
            if recs:
                return recs
    return []

def retry_with_first_result(recs, limit=20):
    """
    Retry logic using the first result in the recommendations list.
    """
    if not recs:
        return [], "No recommendations to retry."

    first_result = recs.pop(0)  # Remove the first result from the queue
    similar_recs = get_similar_tracks(first_result['title'], first_result['artist'], limit)
    if similar_recs:
        return similar_recs, None
    else:
        return recs, "No results found for the first recommendation. Queue updated."

def get_recommendations(song, artist, limit=50):
    """Main function to get song recommendations."""
    recs = get_similar_tracks(song, artist, limit)
    
    if not recs:
        alternatives = search_alternative_tracks(song, artist)
        if alternatives:
            recs = search_recursive_alternatives(alternatives, limit)
        if not recs:
            alternative_spellings = [
                f"{song.lower()}",
                f"{song.upper()}",
                f"{song} (feat. [Artist])",
                f"{song} - Remix",
                f"{song} (Extended Version)"
            ]
            alternative_recs = try_alternative_spellings(song, artist, alternative_spellings)
            if alternative_recs:
                for alt_track in alternative_recs:
                    similar_recs = get_similar_tracks(alt_track['title'], alt_track['artist'], limit)
                    if similar_recs:
                        recs.extend(similar_recs)
                        if len(recs) >= limit:
                            break  # Stop if the limit is reached
                if not recs:
                    recs = alternative_recs

    recs = filter_duplicates(recs)[:limit]  # Ensure no duplicates and apply the limit
    return recs
