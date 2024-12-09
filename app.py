import streamlit as st
from get_recommendations import get_recommendations, retry_with_first_result

# Initialize session state
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "retry_queue" not in st.session_state:
    st.session_state.retry_queue = []

st.title("Music Recommendation🎵")
st.write("Get recommendations for similar tracks based on your favorite songs!")

# Input fields
song = st.text_input("Enter the song name:")
artist = st.text_input("Enter the artist name:")
limit = st.slider("Number of Recommendations", 1, 20, 10)

# Recommendation button
if st.button("Get Recommendations"):
    if not song or not artist:
        st.warning("Please provide both song and artist names.")
    else:
        with st.spinner("Fetching recommendations..."):
            recommendations = get_recommendations(song, artist, limit)
            if recommendations:
                st.success("Here are your recommendations:")
                st.session_state.recommendations = recommendations
                st.session_state.retry_queue = recommendations[:]  # Copy recommendations for retry queue
                for idx, rec in enumerate(recommendations, 1):
                    st.write(f"{idx}. **{rec['title']}** by *{rec['artist']}*")
            else:
                st.error("No recommendations found. Try a different song or artist.")

# Retry feature
if st.session_state.retry_queue:
    st.subheader("Would you like to try again with the next result?")
    first_result = st.session_state.retry_queue[0]

    # Retry button
    if st.button(f"Retry with: {first_result['title']} by {first_result['artist']}"):
        with st.spinner(f"Fetching new recommendations based on: {first_result['title']}..."):
            updated_recs, error = retry_with_first_result(st.session_state.retry_queue, limit)
            if updated_recs:
                st.session_state.recommendations = updated_recs
                st.session_state.retry_queue = updated_recs[:]  # Update retry queue
                st.success("New recommendations:")
                for idx, rec in enumerate(updated_recs, 1):
                    st.write(f"{idx}. **{rec['title']}** by *{rec['artist']}*")
            else:
                st.session_state.retry_queue = updated_recs  # Update the retry queue
                if error:
                    st.warning(error)

    # Stop retry button
    if st.button("Stop retries"):
        st.session_state.retry_queue.clear()
        st.info("Retries stopped.")
