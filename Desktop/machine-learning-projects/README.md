# 🎬 Content-Based Movie Recommender System

An end-to-end machine learning project that recommends movies based on content similarities. It processes the TMDB 5000 dataset, extracts features using Natural Language Processing (NLP), and serves recommendations through a modern, responsive Streamlit web interface.

## 🧠 How It Works (The ML Pipeline)

The recommendation engine is built on a **Content-Based Filtering** architecture. Instead of relying on user ratings, it recommends movies based on metadata (genres, keywords, cast, and director).

1.  **Data Preprocessing:** Merged the TMDB movies and credits datasets. Extracted relevant nested JSON data (top 3 cast members, director name, genres, and keywords) using `ast.literal_eval`.
2.  **Feature Engineering:** Collapsed text spaces to treat multi-word names as single entities (e.g., "Johnny Depp" -> "JohnnyDepp") and concatenated all metadata into a single `tags` feature.
3.  **Text Processing:** Applied lowercasing and the **Porter Stemmer** algorithm via NLTK to reduce words to their root forms (e.g., "actions", "acting" -> "act").
4.  **Vectorization:** Converted the text tags into a 5000-dimensional vector space using **Bag of Words** (`CountVectorizer`), filtering out standard English stop words.
5.  **Similarity Metric:** Calculated the **Cosine Similarity** between movie vectors to find the nearest neighbors in the high-dimensional space.

## 🛠️ Tech Stack

* **Data Processing & ML:** Python, Pandas, NumPy, Scikit-learn, NLTK
* **Web Framework:** Streamlit
* **API Integration:** TMDB API (for dynamic poster fetching)
* **Serialization:** Pickle

## 🚀 Installation & Setup

Because the similarity matrix is too large to host on GitHub, you need to generate the machine learning models locally before running the app.

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/movie-recommender.git](https://github.com/yourusername/movie-recommender.git)
cd movie-recommender
