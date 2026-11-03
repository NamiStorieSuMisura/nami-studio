import streamlit as st
import fal_client
import os
import time

# Configurazione della pagina
st.set_page_config(
    page_title="Nami Studio - Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 NAMI Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Generatore di Videoclip AI Multi-Cliente con Fallback Automatico</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# VERIFICA CHIAVE API
# ---------------------------------------------------------
api_key = None
try:
    if "FAL_KEY" in st.secrets:
        api_key = st.secrets["FAL_KEY"]
        os.environ["FAL_KEY"] = api_key
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("FAL_KEY")

if api_key:
    st.success("✅ Connessione Fal.ai attiva!")
else:
    st.error("⚠️ Inserisci FAL_KEY nei Secrets di Streamlit per abilitare la generazione.")

# Inizializzazione della sessione per il cast del cliente
if "cast_members" not in st.session_state:
    st.session_state.cast_members = []

# ---------------------------------------------------------
# STEP 1: GESTIONE CAST DEL CLIENTE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("👥 1. Gestione Cast del Cliente")

with st.form("client_cast_form", clear_on_submit=True):
    c_name = st.text_input("Nome del Personaggio (es. Luca, Sara, Protagonista)")
    c_desc = st.text_area("Descrizione visiva / Stile (es. Uomo con giacca in pelle, atmosfera Halloween)")
    c_file = st.file_uploader("Foto di riferimento (opzionale)", type=["png", "jpg", "jpeg"])
    
    add_btn = st.form_submit_button("➕ Aggiungi Personaggio al Cast")
    if add_btn:
        if c_name:
            st.session_state.cast_members.append({
                "name": c_name,
                "desc": c_desc,
                "has_photo": c_file is not None
            })
            st.success(f"Personaggio '{c_name}' aggiunto con successo!")
        else:
            st.warning("Inserisci almeno il nome del personaggio.")

if st.session_state.cast_members:
    st.markdown("#### 🌟 Cast Attivo per questo Cliente:")
    for idx, member in enumerate(st.session_state.cast_members):
        st.info(f"**{idx+1}. {member['name']}** — *{member['desc']}*")
    
    if st.button("🗑️ Svuota Cast e Inizia Nuovo Cliente"):
        st.session_state.cast_members = []
        st.rerun()

# ---------------------------------------------------------
# STEP 2: AUDIO SUNO & SCENEGGIATURA
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎵 2. Audio Suno & Sceneggiatura del Cliente")

client_audio = st.file_uploader("Carica il brano audio Suno del cliente (MP3)", type=["mp3", "wav"])
client_lyrics = st.text_area("Incolla qui il testo della canzone o le indicazioni delle scene", placeholder="[Intro] Chi l'avrebbe detto quella sera...")

# ---------------------------------------------------------
# FUNZIONE DI GENERAZIONE VIDEO CON FALLBACK AUTOMATICO
# ---------------------------------------------------------
def generate_video_auto_fallback(prompt, image_url=None):
    """
    Tenta di generare il video usando in primis Wan 2.1.
    Se fallisce o è in manutenzione, scala automaticamente su Minimax / Luma.
    """
    models_pipeline = [
        {"name": "Wan 2.1 (Top Quality)", "endpoint": "fal-ai/wan/v2.1/image-to-video" if image_url else "fal-ai/wan/v2.1/text-to-video"},
        {"name": "Minimax Hailuo AI (Fallback 1)", "endpoint": "fal-ai/minimax/video-01/image-to-video" if image_url else "fal-ai/minimax/video-01"},
        {"name": "Luma Dream Machine (Fallback 2)", "endpoint": "fal-ai/luma-dream-machine/image-to-video" if image_url else "fal-ai/luma-dream-machine"}
    ]
    
    for model in models_pipeline:
        try:
            st.write(f"🔄 Tentativo di generazione con **{model['name']}**...")
            args = {"prompt": prompt}
            if image_url:
                args["image_url"] = image_url

            result = fal_client.subscribe(
                model["endpoint"],
                arguments=args
            )
            st.success(f"⚡ Generazione riuscita con successo tramite **{model['name']}**!")
            return result
        except Exception as err:
            st.warning(f"⚠️ {model['name']} non disponibile o in sovraccarico. Passaggio al modello successivo...")
            time.sleep(1)
            
    raise RuntimeError("Tutti i modelli video su Fal.ai sono momentaneamente non disponibili. Riprova tra poco.")

# ---------------------------------------------------------
# STEP 3: PRE-FLIGHT CHECK & GENERAZIONE AUTOMATICA
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚀 Genera Videoclip Personalizzato"):
    # 1. PRE-FLIGHT CHECK
    errors = []
    if not api_key:
        errors.append("Manca la FAL_KEY nei secrets.")
    if not st.session_state.cast_members:
        errors.append("Il cast è vuoto. Aggiungi almeno un personaggio.")
    if not client_audio:
        errors.append("Manca il file audio Suno del cliente.")
    if not client_lyrics:
        errors.append("Il testo della canzone o le scene sono vuoti.")
        
    if errors:
        st.error("⚠️ **Pre-Flight Check Fallito!** Risolvi questi punti prima di procedere:")
        for err in errors:
            st.markdown(f"- {err}")
    else:
        st.success("✅ Pre-Flight Check Superato! Nessun credito a rischio.")
        
        # 2. GENERAZIONE FRAME DI BASE (Flux)
        with st.spinner("🎨 Creazione frame di riferimento del cast (Flux)..."):
            try:
                cast_details = ", ".join([f"{m['name']} ({m['desc']})" for m in st.session_state.cast_members])
                image_prompt = f"Cinematic music video scene featuring: {cast_details}. High visual quality, matching context: {client_lyrics[:150]}"
                
                img_res = fal_client.subscribe(
                    "fal-ai/flux/dev",
                    arguments={
                        "prompt": image_prompt,
                        "image_size": "landscape_16_9",
                        "num_inference_steps": 28
                    }
                )
                image_url = img_res["images"][0]["url"]
                st.image(image_url, caption="Frame Guida Generato", use_column_width=True)
            except Exception as e:
                st.error(f"Errore nella generazione dell'immagine di base: {e}")
                st.stop()
                
        # 3. ANIMAZIONE AUTOMATICA SMART FALLBACK
        with st.spinner("🎬 Animazione video intelligente in corso..."):
            try:
                video_prompt = f"Cinematic camera movement, music video style: {client_lyrics[:100]}"
                video_res = generate_video_auto_fallback(video_prompt, image_url=image_url)
                
                st.balloons()
                if "video" in video_res:
                    st.video(video_res["video"]["url"])
                elif "images" in video_res:
                    st.image(video_res["images"][0]["url"])
                else:
                    st.json(video_res)
            except Exception as e:
                st.error(f"Impossibile completare il video: {e}")
