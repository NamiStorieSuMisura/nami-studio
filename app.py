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
st.markdown("<p style='text-align: center;'>Generatore di Videoclip AI Personalizzati con Gestione Avanzata del Cast</p>", unsafe_allow_html=True)

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
    st.error("⚠️ Inserisci la FAL_KEY nei Secrets di Streamlit.")

# Inizializzazione della sessione per il cast del cliente
if "cast_members" not in st.session_state:
    st.session_state.cast_members = []

# ---------------------------------------------------------
# STEP 1: GESTIONE CAST DEL CLIENTE (Con rimozione singola)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("👥 1. Gestione Cast e Dettagli Caratteriali")
st.write("Definisci i personaggi aggiungendo dettagli fisici ed espressivi (es. *occhi furbetti, aria dolce, sorriso misterioso*).")

with st.form("client_cast_form", clear_on_submit=True):
    c_name = st.text_input("Nome del Personaggio (es. Luca, Chiara)")
    c_desc = st.text_area("Caratteristiche e Abbigliamento (es. Uomo alto, giacca in pelle)")
    c_expression = st.text_input("Espressione / Dettagli del viso (es. Sguardo dolce, occhi furbetti, aria malinconica)")
    c_file = st.file_uploader("Foto di riferimento del personaggio (opzionale)", type=["png", "jpg", "jpeg"])
    
    add_btn = st.form_submit_button("➕ Aggiungi Personaggio al Cast")
    if add_btn:
        if c_name:
            st.session_state.cast_members.append({
                "name": c_name,
                "desc": c_desc,
                "expression": c_expression,
                "has_photo": c_file is not None
            })
            st.success(f"Personaggio '{c_name}' aggiunto con successo!")
        else:
            st.warning("Inserisci almeno il nome del personaggio.")

# Mostra il cast attivo con opzione di eliminazione mirata
if st.session_state.cast_members:
    st.markdown("#### 🌟 Cast Attivo per questo Cliente:")
    
    for idx, member in enumerate(st.session_state.cast_members):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.info(f"**{idx+1}. {member['name']}**\n\n"
                    f"- *Aspetto:* {member['desc']}\n\n"
                    f"- *Espressione:* {member.get('expression', 'Nessuna indicazione')}")
        with col2:
            if st.button("❌ Rimuovi", key=f"del_{idx}"):
                st.session_state.cast_members.pop(idx)
                st.rerun()
                
    if st.button("🗑️ Svuota Intero Cast"):
        st.session_state.cast_members = []
        st.rerun()

# ---------------------------------------------------------
# STEP 2: AUDIO SUNO & SCENEGGIATURA
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎵 2. Audio Suno & Sceneggiatura del Cliente")

client_audio = st.file_uploader("Carica il brano audio Suno del cliente (MP3)", type=["mp3", "wav"])
client_lyrics = st.text_area("Incolla qui il testo della canzone o le indicazioni delle scene", placeholder="[Intro] Atmosfera suggestiva...")

# ---------------------------------------------------------
# FUNZIONE DI FALLBACK AUTOMATICO PER IL VIDEO
# ---------------------------------------------------------
def generate_video_auto_fallback(prompt, image_url=None):
    models_pipeline = [
        {
            "name": "Wan 2.1 (Top Quality)", 
            "endpoint": "fal-ai/wan-i2v" if image_url else "fal-ai/wan-t2v"
        },
        {
            "name": "Minimax Hailuo AI (Fallback 1)", 
            "endpoint": "fal-ai/minimax/video-01/image-to-video" if image_url else "fal-ai/minimax/video-01"
        },
        {
            "name": "Luma Dream Machine (Fallback 2)", 
            "endpoint": "fal-ai/luma-dream-machine/image-to-video" if image_url else "fal-ai/luma-dream-machine"
        }
    ]
    
    for model in models_pipeline:
        try:
            st.write(f"🔄 Tentativo con **{model['name']}**...")
            args = {"prompt": prompt}
            if image_url:
                args["image_url"] = image_url

            result = fal_client.subscribe(model["endpoint"], arguments=args)
            st.success(f"⚡ Successo con **{model['name']}**!")
            return result
        except Exception as err:
            err_str = str(err)
            if "Exhausted balance" in err_str or "locked" in err_str:
                raise RuntimeError("EXHAUSTED_BALANCE")
            st.warning(f"⚠️ {model['name']} non disponibile ({err}). Provo il successivo...")
            time.sleep(1)
            
    raise RuntimeError("Tutti i modelli video su Fal.ai hanno riscontrato un errore.")
# ---------------------------------------------------------
# STEP 3: PRE-FLIGHT CHECK & GENERAZIONE
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚀 Genera Videoclip Personalizzato"):
    errors = []
    if not api_key:
        errors.append("Manca la FAL_KEY nei secrets.")
    if not st.session_state.cast_members:
        errors.append("Il cast è vuoto. Aggiungi almeno un personaggio.")
    if not client_audio:
        errors.append("Manca il file audio Suno del cliente.")
        
    if errors:
        st.error("⚠️ **Pre-Flight Check Fallito!** Risolvi questi punti prima di procedere:")
        for err in errors:
            st.markdown(f"- {err}")
    else:
        st.success("✅ Pre-Flight Check Superato!")
        
        # Composizione dettagliata del cast con espressioni
        cast_descriptions = []
        for m in st.session_state.cast_members:
            desc_str = f"Character name: {m['name']}, Appearance: {m['desc']}, Facial expression & vibe: {m.get('expression', 'natural')}"
            cast_descriptions.append(desc_str)
        
        full_cast_prompt = " | ".join(cast_descriptions)
        
        # Generazione Immagine con Flux
        with st.spinner("🎨 Creazione frame di riferimento del cast..."):
            try:
                image_prompt = f"Cinematic music video frame featuring: {full_cast_prompt}. High professional quality, detailed lighting."
                
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
                err_str = str(e)
                if "Exhausted balance" in err_str or "locked" in err_str:
                    st.error("💳 **Crediti Fal.ai esauriti!** La produzione è stata fermata per evitare sprechi. Ricarica il saldo su fal.ai/dashboard/billing per continuare.")
                else:
                    st.error(f"Errore nella generazione dell'immagine: {e}")
                st.stop()
                
        # Animazione video intelligente
        with st.spinner("🎬 Animazione video intelligente in corso..."):
            try:
                video_prompt = f"Dynamic camera movement, cinematic music video style, matching: {client_lyrics[:100]}"
                video_res = generate_video_auto_fallback(video_prompt, image_url=image_url)
                
                st.balloons()
                if "video" in video_res:
                    st.video(video_res["video"]["url"])
                elif "images" in video_res:
                    st.image(video_res["images"][0]["url"])
                else:
                    st.json(video_res)
            except Exception as e:
                if str(e) == "EXHAUSTED_BALANCE":
                    st.error("💳 **Crediti Fal.ai esauriti!** La produzione è stata fermata per evitare sprechi. Ricarica il saldo su fal.ai/dashboard/billing per continuare.")
                else:
                    st.error(f"Impossibile completare il video: {e}")
