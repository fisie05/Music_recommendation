import streamlit as st
from get_recommendations import get_recommendations, retry_with_first_result

# Load custom CSS
with open("styles.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# App Header
st.markdown("<div class='header'><h1>🎵 Music Recommendations</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Discover songs similar to your favorites.</div>", unsafe_allow_html=True)

# Input Fields
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
song = st.text_input("🎶 Enter the Song Name:")
artist = st.text_input("🎤 Enter the Artist Name:")
limit = st.slider("📊 Number of Recommendations", 1, 50, 10)
st.markdown("</div>", unsafe_allow_html=True)

# Recommendation Button
if st.button("💡 Get Recommendations"):
    if not song or not artist:
        st.warning("⚠️ Please provide both the song and artist names.")
    else:
        with st.spinner("🔍 Fetching recommendations..."):
            recommendations = get_recommendations(song, artist, limit)
            if recommendations:
                st.success("✅ Recommendations Found!")
                st.markdown("<div class='results-section'>", unsafe_allow_html=True)
                for idx, rec in enumerate(recommendations, 1):
                    st.markdown(f"<div class='result-item'>{idx}. <b>{rec['title']}</b> by <i>{rec['artist']}</i></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ No recommendations found. Try a different song or artist.")

# Retry Section
if st.session_state.retry_queue:
    st.markdown("<div class='retry-section'>", unsafe_allow_html=True)
    first_result = st.session_state.retry_queue[0]

    if st.button(f"♻️ Retry with: {first_result['title']} by {first_result['artist']}"):
        with st.spinner("🔄 Fetching new recommendations..."):
            updated_recs, error = retry_with_first_result(st.session_state.retry_queue, limit)
            if updated_recs:
                st.success("✅ New Recommendations Found!")
                for idx, rec in enumerate(updated_recs, 1):
                    st.markdown(f"<div class='result-item'>{idx}. <b>{rec['title']}</b> by <i>{rec['artist']}</i></div>", unsafe_allow_html=True)
            elif error:
                st.warning(error)
    st.markdown("</div>", unsafe_allow_html=True)
