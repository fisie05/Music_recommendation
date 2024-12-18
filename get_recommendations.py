import requests
from dotenv import load_dotenv
import os
import sqlite3
import recommendation_logic as rec_l


def get_recommendations(song, artist, limit=5):
    """Main function to get song recommendations."""
    recs = rec_l.get_similar_tracks(song, artist, limit)
    
    if not recs:
        alternatives = rec_l.search_alternative_tracks(song, artist)
        if alternatives:
            recs = rec_l.search_recursive_alternatives(alternatives, limit)
        if not recs:
            alternative_spellings = [
                f"{song.lower()}",
                f"{song.upper()}",
                f"{song} (feat. [Artist])",
                f"{song} - Remix",
                f"{song} (Extended Version)"
            ]
            alternative_recs = rec_l.try_alternative_spellings(song, artist, alternative_spellings)
            if alternative_recs:
                for alt_track in alternative_recs:
                    similar_recs = rec_l.get_similar_tracks(alt_track['title'], alt_track['artist'], limit)
                    if similar_recs:
                        recs.extend(similar_recs)
                        if len(recs) >= limit:
                            break
                if not recs:
                    recs = alternative_recs

    recs = rec_l.filter_duplicates(recs)[:limit]  # Ensure no duplicates and apply the limit
    return recs

def add_user(username):
    """Add a new user or retrieve existing user ID."""
    if not username.strip():
        raise ValueError("Username cannot be empty.")  # Rule: No empty names
    
    conn = sqlite3.connect("recommendations.db")
    cursor = conn.cursor()
    
    # Ensure the username is unique
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        return existing_user[0]  # Return the existing user's ID
    
    # Add the new user
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    conn.close()
    return user_id

def save_recommendation(user_id, recommendations):
    """Save recommendations for a user."""
    if not recommendations:
        print("No recommendations to save.")  # Debugging
        return
    
    print(f"Saving recommendations for user_id: {user_id}")
    print(f"Recommendations: {recommendations}")
    
    conn = sqlite3.connect("recommendations.db")
    cursor = conn.cursor()
    for rec in recommendations:
        cursor.execute("""
            INSERT INTO recommendations (user_id, title, artist)
            VALUES (?, ?, ?)
        """, (user_id, rec['title'], rec['artist']))
    conn.commit()
    conn.close()
    print("Recommendations saved successfully!")

def load_recommendations(user_id):
    """Load recommendations for a user."""
    print(f"Loading recommendations for user_id: {user_id}")  # Debugging
    conn = sqlite3.connect("recommendations.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, artist FROM recommendations WHERE user_id = ?
    """, (user_id,))
    results = cursor.fetchall()
    conn.close()
    print(f"Loaded recommendations: {results}")  # Debugging
    return [{'title': row[0], 'artist': row[1]} for row in results]
