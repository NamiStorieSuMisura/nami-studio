import streamlit as st

# Configurazione della pagina per adattarsi al meglio ai dispositivi mobili
st.set_page_config(
    page_title="NAMI Studio | Video Generator",
    page_icon="🎬",
    layout="centered"
)

# Stile visivo personalizzato per il brand Nami
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #FF4B4B;
    }
    .sub-title {
        text-align: center;
        color: #555555;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎬 NAMI Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Il tuo motore di sviluppo video personalizzato</p>", unsafe_allow_html=True)

# Pannello di controllo laterale (comodo anche da mobile nel menu a tendina)
with st.sidebar:
    st.header("⚙️ Impostazioni Nami")
    
    stile_video = st.selectbox(
        "Stile Visivo",
        ["Cartonato 3D Pixar (Coerente)", "Cinematografico Realistico (Film)"]
    )
    
    usa_fissa = st.checkbox("Blocca identità personaggi", value=True)
    modalita_agente = st.checkbox("Attiva Agente Correttore", value=True)

# Area di caricamento principale (ottimizzata per tap da cellulare)
st.markdown("### 1. Carica il brano Suno (MP3)")
audio_file = st.file_uploader("Scegli il file audio", type=["mp3", "wav"])

st.markdown("### 2. Inserisci il Testo della Canzone")
testo_canzone = st.text_area("Incolla qui il testo diviso per strofe...", height=120)

# Pulsante di generazione grande e centrale
if st.button("🚀 Genera Videoclip Nami", use_container_width=True):
    if audio_file is not None and testo_canzone:
        with st.status("🛠️ Nami sta creando il video...", expanded=True) as status:
            st.write("🎵 Sincronizzazione audio con Whisper...")
            st.write(f"🎨 Rendering fotogrammi in stile: {stile_video}...")
            st.write("🎞️ Assemblaggio e montaggio finale...")
            status.update(label="✅ Video completato con successo!", state="complete")
        
        st.success("Il tuo videoclip è pronto! (Qui apparirà l'anteprima video)")
        # st.video("output_nami.mp4")
    else:
        st.warning("⚠️ Carica l'MP3 e inserisci il testo per procedere.")

# Sezione Agente di Correzione integrata
if modalita_agente:
    st.markdown("---")
    st.subheader("💬 Parla con l'Agente Nami")
    st.write("Noti un errore? Scrivi qui sotto cosa correggere (es. *'Modifica la scena iniziale e rendi il vestito blu'*).")
    
    correzione = st.text_input("Istruzione per Nami:")
    if st.button("Invia correzione all'Agente", use_container_width=True):
        if correzione:
            st.info(f"🤖 Nami sta elaborando la correzione: '{correzione}'...")
            st.success("Scena corretta e rigenerata al volo!")
        else:
            st.error("Scrivi un'istruzione valida.")
