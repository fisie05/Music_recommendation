import streamlit as st
from get_recommendations import get_recommendations, retry_with_first_result, add_user, save_recommendation, load_recommendations

# Load custom CSS
with open("styles.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# App Header
st.markdown("<div class='header'><h1>🎵 Music Recommendation Hub</h1></div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Discover songs similar to your favorites.</div>", unsafe_allow_html=True)

# Login and Signup Section
st.markdown("<div class='login-section'>", unsafe_allow_html=True)
username = st.text_input("👤 Enter your username:")
if st.button("🔑 Login / Signup"):
    try:
        if username:
            user_id = add_user(username)
            st.session_state.user_id = user_id
            st.success(f"Welcome, {username}!")
        else:
            st.warning("⚠️ Username cannot be empty. Please enter a valid username.")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
st.markdown("</div>", unsafe_allow_html=True)


# Initialize Session State
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "retry_queue" not in st.session_state:
    st.session_state.retry_queue = []

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
                st.session_state.recommendations = recommendations
                st.session_state.retry_queue = recommendations[:]  # Copy recommendations to retry queue
                st.markdown("<div class='results-section'>", unsafe_allow_html=True)
                for idx, rec in enumerate(recommendations, 1):
                    st.markdown(f"<div class='result-item'>{idx}. <b>{rec['title']}</b> by <i>{rec['artist']}</i></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ No recommendations found. Try a different song or artist.")
    
        # Save Recommendations Button
    if "user_id" in st.session_state:
        if st.button("💾 Save Recommendations"):
            save_recommendation(st.session_state.user_id, st.session_state.recommendations)
            st.success("Recommendations saved successfully!")
            # Do not clear st.session_state.recommendations here
    else:
        st.warning("Please login to save recommendations.")



# Retry Feature
if st.session_state.retry_queue:
    st.markdown("<div class='retry-section'>", unsafe_allow_html=True)
    first_result = st.session_state.retry_queue[0]
    st.markdown(f"<div class='retry-item'>Retry with: <b>{first_result['title']}</b> by <i>{first_result['artist']}</i></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("♻️ Retry"):
            with st.spinner("🔄 Fetching new recommendations..."):
                updated_recs, error = retry_with_first_result(st.session_state.retry_queue, limit)
                if updated_recs:
                    st.session_state.recommendations = updated_recs
                    st.session_state.retry_queue = updated_recs[:]  # Update retry queue
                    st.success("✅ New Recommendations Found!")
                    st.markdown("<div class='results-section'>", unsafe_allow_html=True)
                    for idx, rec in enumerate(updated_recs, 1):
                        st.markdown(f"<div class='result-item'>{idx}. <b>{rec['title']}</b> by <i>{rec['artist']}</i></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                elif error:
                    st.warning(error)
    with col2:
        if st.button("❌ Stop Retries"):
            st.session_state.retry_queue.clear()
            st.info("Retries stopped.")
    st.markdown("</div>", unsafe_allow_html=True)

# Load Saved Recommendations Button
if "user_id" in st.session_state:
    if st.button("📂 Load Saved Recommendations"):
        saved_recs = load_recommendations(st.session_state.user_id)
        if saved_recs:
            st.session_state.recommendations = saved_recs  # Update session state
            st.markdown("<div class='results-section'>", unsafe_allow_html=True)
            st.markdown("<h3>Your Saved Recommendations:</h3>", unsafe_allow_html=True)
            for idx, rec in enumerate(saved_recs, 1):
                st.markdown(f"<div class='result-item'>{idx}. <b>{rec['title']}</b> by <i>{rec['artist']}</i></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("You have no saved recommendations.")
else:
    st.warning("Please login to view saved recommendations.")
