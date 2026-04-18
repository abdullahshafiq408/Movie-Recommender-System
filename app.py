import pickle
import streamlit as st
import requests
import html as html_lib

# ─────────────────────────────────────────────
#  PAGE CONFIG  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  INLINE SVG FALLBACK — never fails, no network
# ─────────────────────────────────────────────
FALLBACK_POSTER = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='300' height='450' viewBox='0 0 300 450'%3E"
    "%3Crect width='300' height='450' fill='%230e1218'/%3E"
    "%3Ctext x='150' y='200' font-family='sans-serif' font-size='48' "
    "fill='%23f0c04033' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E"
    "%3Ctext x='150' y='260' font-family='sans-serif' font-size='13' "
    "fill='%23ffffff33' text-anchor='middle'%3ENo+Poster%3C/text%3E"
    "%3C/svg%3E"
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main > div { background: #080b10 !important; }

[data-testid="stHeader"]     { background: transparent !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: calc(100% - 48px) !important; margin: 0 auto !important; border-radius: 16px !important; }
footer                       { visibility: hidden; }

body, p, span, div, label { color: #e8e4dc; font-family: 'DM Sans', sans-serif; }

/* ══════════════════════════════════════════
   SELECTBOX  — Main Input Field
══════════════════════════════════════════ */
[data-testid="stSelectbox"] label { display: none !important; }

/* Pointer cursor for the whole selectbox area */
[data-testid="stSelectbox"] *, [data-testid="stSelectbox"] input {
    cursor: pointer !important;
}

[data-testid="stSelectbox"] > div:first-child > div:first-child {
    background: #111620 !important;
    border: 1px solid rgba(240,192,64,0.25) !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    transition: border-color .2s, box-shadow .2s !important;
}

/* Yellow focus ring */
[data-testid="stSelectbox"] > div:first-child > div:first-child:hover,
[data-testid="stSelectbox"] > div:first-child > div:first-child:focus-within,
[data-testid="stSelectbox"] > div:first-child > div:first-child[data-focus="true"] {
    border-color: rgba(240,192,64,0.8) !important;
    box-shadow: 0 0 0 1px rgba(240,192,64,0.8) !important;
}

/* Base text color inside the input */
[data-testid="stSelectbox"] * {
    color: #f0f0ec !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #f0f0ec !important;
}
[data-testid="stSelectbox"] svg { color: rgba(240,192,64,0.6) !important; }

/* ══════════════════════════════════════════
   DROPDOWN MENU — Portal Targeting
   Forces the dropdown to be dark with bright text
══════════════════════════════════════════ */
div[data-baseweb="popover"] > div {
    background-color: #111620 !important;
    border: 1px solid rgba(240,192,64,0.3) !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 30px rgba(0,0,0,0.7) !important;
}

div[data-baseweb="popover"] ul[role="listbox"] {
    background-color: transparent !important;
}

div[data-baseweb="popover"] ul[role="listbox"] li {
    color: #e8e4dc !important; /* Bright, readable text */
    font-size: 14px !important;
    padding: 12px 16px !important;
    background-color: transparent !important;
}

div[data-baseweb="popover"] ul[role="listbox"] li:hover, 
div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"],
div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"]:hover {
    background-color: rgba(240,192,64,0.15) !important;
    color: #f0c040 !important;
}

/* ══════════════════════════════════════════
   COLUMNS — flex-end so buttons align exactly
══════════════════════════════════════════ */
div[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-end !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f0c040 0%, #d9a81a 100%) !important;
    color: #080b10 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 10px !important;
    height: 48px !important;
    cursor: pointer !important;
    transition: all .2s ease !important;
    box-shadow: 0 4px 20px rgba(240,192,64,0.28) !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(240,192,64,0.4) !important;
    filter: brightness(1.07) !important;
}

/* ══════════════════════════════════════════
   HERO
══════════════════════════════════════════ */
.hero {
    position: relative; width: 100%;
    padding: 52px 60px 44px; overflow: hidden;
    background: #080b10;
    border-bottom: 1px solid rgba(255,215,50,0.07);
}
.hero::after {
    content: ''; position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 65% 90% at 85% 50%, rgba(240,160,30,.055) 0%, transparent 60%),
        radial-gradient(ellipse 50% 70% at 5%  20%, rgba(200,60,50,.035)  0%, transparent 55%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 10px; font-weight: 600; letter-spacing: 3.5px;
    text-transform: uppercase; color: #f0c040; margin-bottom: 10px;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(54px, 6.5vw, 92px);
    line-height: .9; letter-spacing: 1px; color: #f0f0ec; margin-bottom: 18px;
}
.hero-title span { color: #f0c040; }
.hero-subtitle {
    font-size: 15px; font-weight: 300; line-height: 1.65;
    color: rgba(232,228,220,0.5); max-width: 500px;
}

/* film-strip bar */
.filmstrip {
    width: 100%; height: 14px; overflow: hidden;
    background: repeating-linear-gradient(
        90deg,
        rgba(240,192,64,0.11) 0px, rgba(240,192,64,0.11) 14px,
        transparent 14px, transparent 26px
    );
}

/* ── Stats strip ── */
.stats-strip {
    display: flex;
    background: #090c12;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.stat-item {
    flex: 1; padding: 18px 0; text-align: center;
    border-right: 1px solid rgba(255,255,255,0.04);
}
.stat-item:last-child { border-right: none; }
.stat-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 24px; color: #f0c040; line-height: 1;
}
.stat-label {
    font-size: 9px; letter-spacing: 2px; text-transform: uppercase;
    color: rgba(232,228,220,0.28); margin-top: 5px;
}

/* ── Search section ── */
.search-section { padding: 32px 60px 8px; }
.search-label {
    font-size: 10px; font-weight: 600; letter-spacing: 3px;
    text-transform: uppercase; color: rgba(232,228,220,0.35); margin-bottom: 12px;
}

/* ── Recent chips ── */
.recent-wrap {
    display: flex; align-items: center; gap: 8px;
    flex-wrap: wrap; padding: 12px 60px 4px;
}
.recent-label {
    font-size: 9px; letter-spacing: 2.5px; text-transform: uppercase;
    color: rgba(232,228,220,0.22);
}
.recent-chip {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    color: rgba(232,228,220,0.48) !important;
    font-size: 11px; padding: 3px 10px; border-radius: 20px;
}

/* ── Divider ── */
.section-divider {
    height: 1px; margin: 0 60px;
    background: linear-gradient(90deg, transparent, rgba(240,192,64,0.13), transparent);
}

/* ── Results section ── */
.results-section { padding: 32px 60px 64px; }
.results-header {
    display: flex; align-items: baseline;
    justify-content: space-between; margin-bottom: 24px;
}
.results-left { display: flex; align-items: baseline; gap: 14px; }
.results-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 30px; letter-spacing: 1px; color: #f0f0ec;
}
.results-for { font-size: 13px; color: rgba(232,228,220,0.38); }
.results-for em { font-style: normal; color: #f0c040; font-weight: 600; }
.results-count {
    font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
    color: rgba(232,228,220,0.22);
}

/* ── Movie Card ── */
.movie-card {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; overflow: hidden;
    transition: transform .28s ease, border-color .28s ease, box-shadow .28s ease;
    cursor: pointer;
    margin-bottom: 24px;
}
.movie-card:hover {
    transform: translateY(-7px);
    border-color: rgba(240,192,64,0.32);
    box-shadow: 0 22px 55px rgba(0,0,0,0.55), 0 0 0 1px rgba(240,192,64,0.1);
}
.poster-wrap {
    position: relative; width: 100%; padding-top: 150%; overflow: hidden;
    background: #0d1117;
}
.poster-wrap img {
    position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; transition: transform .45s ease;
}
.movie-card:hover .poster-wrap img { transform: scale(1.05); }
.rank-badge {
    position: absolute; top: 10px; left: 10px;
    width: 28px; height: 28px;
    background: rgba(8,11,16,0.82); border: 1px solid rgba(240,192,64,0.45);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-family: 'Bebas Neue', sans-serif; font-size: 14px; color: #f0c040;
    backdrop-filter: blur(8px);
}
.poster-overlay {
    position: absolute; bottom: 0; left: 0; right: 0; height: 50%;
    background: linear-gradient(to top, rgba(8,11,16,.95) 0%, transparent 100%);
}
.card-body { padding: 12px 14px 16px; }
.card-title {
    font-size: 13px; font-weight: 600; color: #f0f0ec !important;
    line-height: 1.35; margin-bottom: 8px;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}
.card-meta { display: flex; gap: 6px; flex-wrap: wrap; }
.meta-pill {
    font-size: 9px; font-weight: 600; letter-spacing: .8px; text-transform: uppercase;
    color: rgba(232,228,220,0.32) !important;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);
    padding: 3px 7px; border-radius: 4px;
}
.rating-pill {
    font-size: 9px; font-weight: 700; color: #f0c040 !important;
    background: rgba(240,192,64,0.1); border: 1px solid rgba(240,192,64,0.2);
    padding: 3px 7px; border-radius: 4px;
}
.score-pill {
    font-size: 9px; font-weight: 700; color: #6ec97a !important;
    background: rgba(110,201,122,0.1); border: 1px solid rgba(110,201,122,0.2);
    padding: 3px 7px; border-radius: 4px;
}

/* ── Empty state ── */
.empty-state { padding: 20px 60px 60px; }
.empty-card {
    padding: 40px 32px; text-align: center;
    background: rgba(240,192,64,0.03);
    border: 1px dashed rgba(240,192,64,0.14);
    border-radius: 16px;
}
.empty-icon { font-size: 48px; margin-bottom: 14px; opacity: .45; }
.empty-text { font-size: 15px; color: rgba(232,228,220,0.45) !important; line-height: 1.6; }
.empty-text strong { color: rgba(232,228,220,0.72) !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #f0c040 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────

@st.cache_resource
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    sim = pickle.load(open('similarity.pkl',  'rb'))
    return movies, sim

movies_df, similarity = load_data()
movie_list = sorted(movies_df['title'].values.tolist())

# ─────────────────────────────────────────────
#  TMDB HELPER
# ─────────────────────────────────────────────
TMDB_KEY = "8265bd1679663a7ea12ac168da84d2e8"

@st.cache_data(show_spinner=False, ttl=86400)
def fetch_details(movie_id: int) -> dict:
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": TMDB_KEY, "language": "en-US"},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        path = data.get("poster_path") or ""
        poster = f"https://image.tmdb.org/t/p/w500{path}" if path else FALLBACK_POSTER
        genres = [g["name"] for g in data.get("genres", [])[:2]]
        year = (data.get("release_date") or "")[:4]
        vote = round(float(data.get("vote_average") or 0), 1)
        return {"poster": poster, "genres": genres, "year": year, "vote": vote}
    except Exception:
        return {"poster": FALLBACK_POSTER, "genres": [], "year": "", "vote": 0.0}

def recommend(movie: str):
    idx = movies_df[movies_df["title"] == movie].index[0]
    distances = sorted(
        enumerate(similarity[idx]), reverse=True, key=lambda x: x[1])
    results = []
    for rank, (i, score) in enumerate(distances[1:11], start=1):
        row = movies_df.iloc[i]
        details = fetch_details(int(row["id"]))
        results.append({
            "title": row["title"],
            "score": round(score * 100),
            "rank":  rank,
            **details,
        })
    return results

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in [("results", None), ("searched_movie", None), ("history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered Discovery Engine</div>
    <div class="hero-title">CINE<span>MATCH</span></div>
    <p class="hero-subtitle">
        Intelligent recommendations driven by cosine similarity across cast,
        genres, keywords &amp; crew. Your next obsession is one click away.
    </p>
</div>
<div class="filmstrip"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  STATS STRIP
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="stats-strip">
    <div class="stat-item">
        <div class="stat-num">{len(movie_list):,}</div>
        <div class="stat-label">Movies Indexed</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">5,000</div>
        <div class="stat-label">Feature Vectors</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">Cosine</div>
        <div class="stat-label">Similarity Metric</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">BoW + NLP</div>
        <div class="stat-label">Bag of Words · Stemming</div>
    </div>
    <div class="stat-item">
        <div class="stat-num">{len(st.session_state.history)}</div>
        <div class="stat-label">Searches This Session</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SEARCH ROW
# ─────────────────────────────────────────────
st.markdown('<div class="search-section">', unsafe_allow_html=True)
st.markdown('<div class="search-label">✦ Pick a Movie to Start</div>',
            unsafe_allow_html=True)

# Adjust columns to perfectly balance the Selectbox and the single Search button
col_sel, col_btn = st.columns([5, 1.5], gap="medium", vertical_alignment="bottom")

with col_sel:
    default_movie = "Avatar"
    default_idx = movie_list.index(
        default_movie) if default_movie in movie_list else 0
    selected_movie = st.selectbox(
        "Movie", movie_list, index=default_idx, label_visibility="collapsed")

with col_btn:
    search_clicked = st.button("⚡  Find Similar", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Recent searches chips ─────────────────────
if st.session_state.history:
    chips_html = '<div class="recent-wrap"><span class="recent-label">Recent —</span>'
    for title in reversed(st.session_state.history[-5:]):
        chips_html += f'<span class="recent-chip">{html_lib.escape(title)}</span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGIC
# ─────────────────────────────────────────────
def run_recommendation(movie: str):
    with st.spinner(f"Finding movies similar to **{movie}**…"):
        st.session_state.results = recommend(movie)
        st.session_state.searched_movie = movie
        if movie not in st.session_state.history:
            st.session_state.history.append(movie)

if search_clicked:
    run_recommendation(selected_movie)

# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
if st.session_state.results:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="results-section">', unsafe_allow_html=True)

    safe_title = html_lib.escape(st.session_state.searched_movie)
    st.markdown(f"""
    <div class="results-header">
        <div class="results-left">
            <span class="results-title">TOP 10 PICKS</span>
            <span class="results-for">because you liked <em>{safe_title}</em></span>
        </div>
        <span class="results-count">10 results</span>
    </div>
    """, unsafe_allow_html=True)

    for row_start in range(0, 10, 5):
        cols = st.columns(5, gap="medium")
        chunk = st.session_state.results[row_start:row_start+5]
        
        for col, m in zip(cols, chunk):
            safe_name = html_lib.escape(m["title"])
            genre_pills = "".join(
                f'<span class="meta-pill">{html_lib.escape(g)}</span>'
                for g in (m["genres"] if m["genres"] else ["—"])
            )
            year_pill = f'<span class="meta-pill">{m["year"]}</span>' if m["year"] else ""
            rating_pill = f'<span class="rating-pill">★ {m["vote"]}</span>' if m["vote"] else ""
            score_pill = f'<span class="score-pill">↑ {m["score"]}% match</span>' if m["score"] >= 10 else ""

            with col:
                st.markdown(f"""
                <div class="movie-card">
                    <div class="poster-wrap">
                        <img
                            src="{m['poster']}"
                            alt="{safe_name}"
                            loading="lazy"
                            onerror="this.onerror=null;this.src='{FALLBACK_POSTER}';"
                        >
                        <div class="poster-overlay"></div>
                        <div class="rank-badge">{m['rank']}</div>
                    </div>
                    <div class="card-body">
                        <div class="card-title">{safe_name}</div>
                        <div class="card-meta">{year_pill}{genre_pills}{rating_pill}</div>
                        <div class="card-meta" style="margin-top:5px;">{score_pill}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-card">
            <div class="empty-icon">🎬</div>
            <div class="empty-text">
                <strong>Pick a movie, get 10 perfect matches.</strong><br>
                Search by title in the dropdown above to let the algorithm find your next obsession.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)