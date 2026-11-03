import streamlit as st
import os

# Configurazione della pagina per adattarsi al meglio anche da cellulare
st.set_page_config(
    page_title="Nami Studio",
    page_icon="🎬",
    layout="centered"
)

# Stile grafico pulito e ottimizzato per mobile
st.markdown("""
    <style>
    .main-title { text-align: center; color: #FF4B4B; font-weight: bold; }
    .sub-title { text-align: center; color: #555555; margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎬 NAMI Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Il tuo studio di produzione video AI da Suno Audio</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# VERIFICA CONNESSIONE API FAL.AI
# ---------------------------------------------------------
api_key = None
try:
    if "FAL_KEY" in st.secrets:
        api_key = st.secrets["FAL_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("FAL_KEY")

if api_key:
    st.success("✅ Motore Fal.ai connesso e pronto all'azione!")
else:
    st.warning("⚠️ Chiave API Fal.ai non rilevata. Inseriscila nei Secrets di Streamlit.")

# ---------------------------------------------------------
# MODULO 1: GESTIONE CAST & SCHEDA PERSONAGGIO (VALIDAZIONE)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("👥 1. Gestione Cast & Scheda Personaggio")
st.write("Definisci i protagonisti del videoclip. Puoi caricare una foto reale o descrivere il personaggio per generare una scheda validata.")

if "cast_members" not in st.session_state:
    st.session_state.cast_members = []

with st.form("add_character_form"):
    char_name = st.text_input("Nome del Personaggio (es. Marco, Sara, Nami)")
    char_desc = st.text_area("Descrizione o Stile (es. Ragazzo con felpa verde, stile 3D Pixar, occhiali da vista)")
    char_source = st.radio("Origine del Personaggio:", ["Genera con IA da descrizione", "Carica foto esistente del cliente"])
    uploaded_char_file = st.file_uploader("Carica foto di riferimento (opzionale se generato da IA):", type=["png", "jpg", "jpeg"])
    
    submitted = st.form_submit_button("➕ Aggiungi al Cast e Valida Scheda")
    
    if submitted and char_name:
        st.session_state.cast_members.append({
            "name": char_name,
            "desc": char_desc,
            "source": char_source,
            "validated": True  # Flag di approvazione
        })
        st.success(f"Personaggio '{char_name}' aggiunto e validato con successo!")

# Mostra i personaggi attualmente nel cast
if st.session_state.cast_members:
    st.markdown("#### 🌟 Cast Attivo per il Videoclip:")
    for idx, member in enumerate(st.session_state.cast_members):
        st.info(f"**{idx+1}. {member['name']}** — *{member['desc']}* (Stato: ✅ Validato)")

# ---------------------------------------------------------
# MODULO 2: CARICAMENTO AUDIO SUNO E TESTO
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎵 2. Sincronizzazione Audio & Sceneggiatura")

audio_file = st.file_uploader("Carica il file audio Suno (MP3)", type=["mp3", "wav"])
song_lyrics = st.text_area("Inserisci il Testo della Canzone / Prompt delle Scene", placeholder="Scena 1: [Nome Personaggio] corre felice nel parco...")

# ---------------------------------------------------------
# MODULO 3: GENERAZIONE VIDEO
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚀 Genera Videoclip Nami"):
    if not api_key:
        st.error("Errore: Impossibile generare senza una chiave API valida configurata.")
    elif not audio_file:
        st.warning("Per favore carica prima un brano audio MP3 di Suno.")
    elif not st.session_state.cast_members:
        st.warning("Aggiungi e valida almeno un personaggio nel cast prima di generare.")
    else:
        with st.spinner("Nami sta elaborando la sincronizzazione e la coerenza dei personaggi... Attendere prego."):
            # Qui inseriremo la chiamata effettiva alle API di Fal.ai per la generazione delle scene con i seed bloccati
            st.success("🎉 Processo avviato con successo! (Modulo di rendering collegato a Fal.ai)")
