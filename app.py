import streamlit as st
import fal_client
import os
import time

# Configurazione della pagina
st.set_page_config(
    page_title="Nami Studio - Full Music Video Generator",
    page_icon="🎬",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 NAMI Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Generatore Automatico di Videoclip Musicali (Multi-Scena & Flessibilità Cast)</p>", unsafe_allow_html=True)

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

if "cast_members" not in st.session_state:
    st.session_state.cast_members = []

# ---------------------------------------------------------
# STEP 1: SELEZIONE STILE & GESTIONE CAST FLESSIBILE
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎨 1. Selezione Stile Visivo & Cast")

visual_style = st.selectbox(
    "Scegli lo Stile del Videoclip:",
    [
        "Cartone Animato 3D (Stile Pixar/Disney - Ideale per Bambini & Regali)",
        "Cinematic Realistico (Stile Film / Fotorealistico)",
        "Anime Giapponese 2D"
    ]
)

style_prompts = {
    "Cartone Animato 3D (Stile Pixar/Disney - Ideale per Bambini & Regali)": "Cute 3D animated movie style, Pixar and Disney aesthetic, vibrant colors, charming character design, soft lighting, heartwarming feel",
    "Cinematic Realistico (Stile Film / Fotorealistico)": "Cinematic music video frame, highly detailed photorealistic, professional lighting, 8k resolution, film grain",
    "Anime Giapponese 2D": "Japanese anime style, vibrant colors, detailed line-art, Studio Ghibli aesthetic, emotional anime scenes"
}

current_style_prompt = style_prompts[visual_style]

with st.form("client_cast_form", clear_on_submit=True):
    c_name = st.text_input("Nome del Personaggio (es. Luca, Chiara)")
    c_desc = st.text_area("Descrizione fisica (es. Bambina di 2 anni, capelli ricciolini biondi, occhi grandi)")
    c_file = st.file_uploader("Carica foto reale (Opzionale: se caricata, l'AI la trasformerà nello stile scelto)", type=["png", "jpg", "jpeg"])
    
    add_btn = st.form_submit_button("➕ Aggiungi Personaggio al Cast")
    if add_btn:
        if c_name:
            uploaded_url = None
            if c_file is not None:
                # Carica la foto su fal.ai per usarla come riferimento
                try:
                    uploaded_url = fal_client.upload(c_file)
                except Exception as e:
                    st.warning(f"Impossibile caricare la foto su Fal.ai: {e}")
            
            st.session_state.cast_members.append({
                "name": c_name,
                "desc": c_desc,
                "photo_url": uploaded_url
            })
            st.success(f"Personaggio '{c_name}' aggiunto con successo!")
        else:
            st.warning("Inserisci almeno il nome del personaggio.")

# Mostra il cast attivo
if st.session_state.cast_members:
    st.markdown("#### 🌟 Cast Attivo per questo Cliente:")
    for idx, member in enumerate(st.session_state.cast_members):
        col1, col2 = st.columns([4, 1])
        with col1:
            has_photo_text = "📸 [Con foto di riferimento]" if member['photo_url'] else "📝 [Solo descrizione testuale]"
            st.info(f"**{idx+1}. {member['name']}** {has_photo_text}\n\n- *Aspetto:* {member['desc']}")
        with col2:
            if st.button("❌ Rimuovi", key=f"del_{idx}"):
                st.session_state.cast_members.pop(idx)
                st.rerun()
                
    if st.button("🗑️ Svuota Intero Cast"):
        st.session_state.cast_members = []
        st.rerun()

# ---------------------------------------------------------
# STEP 2: AUDIO SUNO & SCENEGGIATURA COMPLETA
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎵 2. Audio Suno & Testo Canzone (Storyboard Automatico)")

client_audio = st.file_uploader("Carica il brano audio Suno del cliente (MP3)", type=["mp3", "wav"])
client_lyrics = st.text_area(
    "Incolla qui il testo completo della canzone o le indicazioni per le scene",
    height=200,
    placeholder="[Strofa 1] La piccola Chiara gioca in giardino...\n[Ritornello] Vola alto il palloncino nel cielo blu..."
)

# ---------------------------------------------------------
# FUNZIONE DI FALLBACK VIDEO
# ---------------------------------------------------------
def generate_video_auto_fallback(prompt, image_url=None):
    models_pipeline = [
        {"name": "Wan 2.1 (Top Quality)", "endpoint": "fal-ai/wan-i2v" if image_url else "fal-ai/wan-t2v"},
        {"name": "Minimax Hailuo AI (Fallback 1)", "endpoint": "fal-ai/minimax/video-01/image-to-video" if image_url else "fal-ai/minimax/video-01"},
        {"name": "Luma Dream Machine (Fallback 2)", "endpoint": "fal-ai/luma-dream-machine/image-to-video" if image_url else "fal-ai/luma-dream-machine"}
    ]
    
    for model in models_pipeline:
        try:
            st.write(f"🔄 Generazione clip con **{model['name']}**...")
            args = {"prompt": prompt}
            if image_url:
                args["image_url"] = image_url

            result = fal_client.subscribe(model["endpoint"], arguments=args)
            return result
        except Exception as err:
            err_str = str(err)
            if "Exhausted balance" in err_str or "locked" in err_str:
                raise RuntimeError("EXHAUSTED_BALANCE")
            st.warning(f"⚠️ {model['name']} non disponibile. Provo il successivo...")
            time.sleep(1)
            
    raise RuntimeError("Errore su tutti i modelli video.")

# ---------------------------------------------------------
# STEP 3: GENERAZIONE INTERO VIDEOCLIP
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚀 Genera Videoclip Musicale Completo"):
    errors = []
    if not api_key:
        errors.append("Manca la FAL_KEY nei secrets.")
    if not st.session_state.cast_members:
        errors.append("Il cast è vuoto. Aggiungi almeno un personaggio.")
    if not client_audio:
        errors.append("Manca il file audio Suno del cliente.")
    if not client_lyrics.strip():
        errors.append("Manca il testo della canzone.")
        
    if errors:
        st.error("⚠️ **Pre-Flight Check Fallito!** Risolvi questi punti prima di procedere:")
        for err in errors:
            st.markdown(f"- {err}")
    else:
        st.success("✅ Pre-Flight Check Superato! Avvio generazione videoclip...")
        
        raw_lines = [line.strip() for line in client_lyrics.split("\n") if line.strip() and not line.startswith("[")]
        scenes = raw_lines if raw_lines else ["Music video atmosphere", "Character performing", "Climax emotional scene"]
        
        st.info(f"🎬 **Storyboard Generato:** {len(scenes)} scene identificate.")
        
        # Gestione del personaggio principale e della foto di riferimento (se presente)
        primary_member = st.session_state.cast_members[0]
        ref_image_url = primary_member.get("photo_url")
        
        cast_desc = f"Character: {primary_member['name']}, Description: {primary_member['desc']}"
        
        generated_clips = []
        
        for idx, scene_text in enumerate(scenes):
            st.markdown(f"### 📽️ Scena {idx+1}/{len(scenes)}: *\"{scene_text[:50]}...\"*")
            
            with st.spinner(f"🎨 [1/2] Generazione frame (Stile: {visual_style})..."):
                try:
                    image_prompt = f"{current_style_prompt}. Scene action: {scene_text}. Main character: {cast_desc}."
                    
                    flux_args = {
                        "prompt": image_prompt,
                        "image_size": "landscape_16_9",
                        "num_inference_steps": 28
                    }
                    
                    # Se il cliente ha caricato una foto, usiamola come guida visiva (Image-to-Image / conditioning)
                    if ref_image_url:
                        flux_args["image_url"] = ref_image_url
                        flux_args["strength"] = 0.45  # Mantiene i tratti della foto adattandoli allo stile scelto
                    
                    img_res = fal_client.subscribe("fal-ai/flux/dev", arguments=flux_args)
                    image_url = img_res["images"][0]["url"]
                    st.image(image_url, caption=f"Frame Guida Scena {idx+1}", use_column_width=True)
                except Exception as e:
                    if "Exhausted balance" in str(e) or "locked" in str(e):
                        st.error("💳 **Crediti esauriti durante la produzione!** Ricarica per continuare.")
                        st.stop()
                    st.error(f"Errore frame scena {idx+1}: {e}")
                    continue

            with st.spinner(f"🎬 [2/2] Animazione scena {idx+1}..."):
                try:
                    video_prompt = f"Dynamic animation, {current_style_prompt}, matching action: {scene_text}"
                    video_res = generate_video_auto_fallback(video_prompt, image_url=image_url)
                    
                    if "video" in video_res:
                        clip_url = video_res["video"]["url"]
                        generated_clips.append(clip_url)
                        st.video(clip_url)
                    else:
                        st.warning("Impossibile recuperare il file video per questa scena.")
                except Exception as e:
                    if str(e) == "EXHAUSTED_BALANCE":
                        st.error("💳 **Crediti esauriti durante la produzione!** Ricarica per continuare.")
                        st.stop()
                    st.error(f"Errore animazione scena {idx+1}: {e}")

        if generated_clips:
            st.balloons()
            st.success(f"🎉 **Videoclip Completato!** Generate {len(generated_clips)} scene.")
            st.markdown("### 📥 Scarica le clip generate:")
            for i, clip in enumerate(generated_clips):
                st.markdown(f"- [Scarica Clip Scena {i+1}]({clip})")
