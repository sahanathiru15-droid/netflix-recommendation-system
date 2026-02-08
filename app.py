import streamlit as st
import pickle
import joblib
import requests
import urllib.parse

st.set_page_config(page_title="Netflix Recommender", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #141414;
        color: white;
    }
    h1, h2, h3, .stMarkdown p {
        color: white !important;
    }
    .stButton>button {
        background-color: #E50914;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff0f1f;
        color: white;
    }
    /* Style for the selectbox text */
    div[data-baseweb="select"] > div {
        background-color: #333 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_data():
    movies_list = pickle.load(open('movies_list.pk1', 'rb'))
    similarity = joblib.load('similarity.pk1')
    return movies_list, similarity
try:
    movies_list, similarity = load_data()
    movies = movies_list['title'].tolist()
except Exception as e:
    st.error(f"Error loading data files: {e}")
    st.stop()

def fetch_movie_details(movie_title):
    encoded_title = urllib.parse.quote(movie_title)
    url = f"http://www.omdbapi.com/?t={encoded_title}&apikey=6561a3a1"
    try:
        data = requests.get(url).json()
        if data.get('Response') == "True":
            return {
                "poster": data.get('Poster', "https://via.placeholder.com/500x750?text=No+Poster"),
                "genre": data.get('Genre', 'N/A'),
                "rating": data.get('imdbRating', 'N/A'),
                "description": data.get('Plot', 'No description available.')
            }
    except:
        return None
    return None

def recommend(movie):
    index = movies_list[movies_list['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommend_movie = []
    for i in distances[1:6]:
        m_title = movies_list.iloc[i[0]]['title']
        recommend_movie.append(m_title)
    return recommend_movie
st.title("🎬 Netflix Recommender System")
st.write("Find your next watch and click the poster to view on Netflix.")

selected_movie = st.selectbox("Select a movie you like:", movies)
if st.button("Show Recommendations"):
    recommended_titles = recommend(selected_movie)
    st.subheader(f"Because you liked '{selected_movie}':")
    st.divider()

    for movie in recommended_titles:
        details = fetch_movie_details(movie)
        if details:
            col1, col2 = st.columns([1, 3])
            with col1:
                netflix_search_url = f"https://www.netflix.com/search?q={urllib.parse.quote(movie)}"
                st.markdown(f'[![Poster]({details["poster"]})]({netflix_search_url})')
            with col2:
                st.subheader(movie)
                st.write(f"**🎭 Genre:** {details['genre']} | **⭐ IMDb Rating:** {details['rating']}")
                st.write(f"**📝 Description:** {details['description']}")
                st.markdown(f"[▶️ Watch on Netflix]({netflix_search_url})")
            st.divider()