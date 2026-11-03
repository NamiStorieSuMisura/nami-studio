import streamlit as st
import fal_client
import os
import time

# Configurazione della pagina
st.set_page_config(
    page_title="Nami Studio - Pro Music Video Director",
    page_icon="🎬",
    layout="centered"
)

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🎬 NAMI Studio Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Regia Automatica, Storyboard Granulare (30 Scene) & Controllo Umano</p>", unsafe_allow_html=True)

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

if "storyboard_scenes" not in st.session_state:
    st.session_state.storyboard_scenes = []

# ---------------------------------------------------------
# STEP 1: SELEZIONE STILE & CAST CON FACE CONSISTENCY
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
    "Cartone Animato 3D (Stile Pixar/Disney - Ideale per Bambini & Regali)": "Cute 3D animated movie style, Pixar and Disney aesthetic, vibrant colors, soft lighting",
    "Cinematic Realistico (Stile Film / Fotorealistico)": "Cinematic music video frame, highly detailed photorealistic, 8k resolution, professional lighting",
    "Anime Giapponese 2D": "Japanese anime style, vibrant colors, detailed line-art, Studio Ghibli aesthetic"
}

current_style_prompt = style_prompts[visual_style]

with st.form("client_cast_form", clear_on_submit=True):
    c_name = st.text_input("Nome del Personaggio (es. Luca, Chiara)")
    c_desc = st.text_area("Descrizione fisica dettagliata (es. Uomo di 37 anni, capelli castani corti, barba leggera)")
    c_file = st.file_uploader("Carica foto del volto (FONDAMENTALE per la coerenza facciale)", type=["png", "jpg", "jpeg"])
    
    add_btn = st.form_submit_button("➕ Aggiungi Personaggio al Cast")
    if add_btn:
        if c_name:
            uploaded_url = None
            if c_file is not None:
                try:
                    uploaded_url = fal_client.upload(c_file.getvalue(), content_type=c_file.type)
                except Exception as e:
                    st.warning(f"Impossibile caricare la foto su Fal.ai: {e}")
            
            st.session_state.cast_members.append({
                "name": c_name,
                "desc": c_desc,
                "photo_url": uploaded_url
            })
            st.success(f"Personaggio '{c_name}' aggiunto al cast!")
        else:
            st.warning("Inserisci almeno il nome del personaggio.")

# Mostra il cast attivo
if st.session_state.cast_members:
    st.markdown("#### 🌟 Cast Attivo:")
    for idx, member in enumerate(st.session_state.cast_members):
        col1, col2 = st.columns([4, 1])
        with col1:
            has_photo_text = "📸 [Face-Swap / Identity lock attivo]" if member['photo_url'] else "📝 [Solo descrizione]"
            st.info(f"**{idx+1}. {member['name']}** {has_photo_text}\n\n- *Dettagli:* {member['desc']}")
        with col2:
            if st.button("❌ Rimuovi", key=f"del_{idx}"):
                st.session_state.cast_members.pop(idx)
                st.rerun()

# ---------------------------------------------------------
# STEP 2: AUDIO SUNO & TESTO CANZONE (30 SCENE GRANULARI)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🎵 2. Audio Suno & Storyboard Granulare (Fino a 30 Scene)")

client_audio = st.file_uploader("Carica il brano audio Suno del cliente (MP3)", type=["mp3", "wav"])
client_lyrics = st.text_area(
    "Incolla qui il testo completo della canzone",
    height=200,
    placeholder="[Intro]\nChi l'avrebbe detto quella sera?...\n\n[Verse 1]\nEra Halloween, a casa di mia sorella..."
)

# Funzione di fallback video
def generate_video_auto_fallback(prompt, image_url=None):
    models_pipeline = [
        {"name": "Wan 2.1 (Top Quality)", "endpoint": "fal-ai/wan-i2v" if image_url else "fal-ai/wan-t2v"},
        {"name": "Minimax Hailuo AI (Fallback 1)", "endpoint": "fal-ai/minimax/video-01/image-to-video" if image_url else "fal-ai/minimax/video-01"},
        {"name": "Luma Dream Machine (Fallback 2)", "endpoint": "fal-ai/luma-dream-machine/image-to-video" if image_url else "fal-ai/luma-dream-machine"}
    ]
    
    for model in models_pipeline:
        try:
            args = {"prompt": prompt}
            if image_url:
                args["image_url"] = image_url
            result = fal_client.subscribe(model["endpoint"], arguments=args)
            return result
        except Exception as err:
            err_str = str(err)
            if "Exhausted balance" in err_str or "locked" in err_str:
                raise RuntimeError("EXHAUSTED_BALANCE")
            time.sleep(1)
    raise RuntimeError("Errore su tutti i modelli video.")

# ---------------------------------------------------------
# STEP 3: CREAZIONE E REVISIONE DELLE SCENE
# ---------------------------------------------------------
st.markdown("---")
if st.button("🚀 Genera Storyboard e Clip per la Revisione"):
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
        st.error("⚠️ **Pre-Flight Check Fallito!** Risolvi questi punti:")
        for err in errors:
            st.markdown(f"- {err}")
    else:
        st.success("✅ Analisi avviata! Creazione delle scene granulari (fino a 30)...")
        
        # Parsing avanzato riga per riga per raggiungere una struttura ricca (circa 25-30 scene)
        raw_blocks = client_lyrics.split("\n\n")
        extracted_scenes = []
        for b in raw_blocks:
            lines = [l.strip() for l in b.split("\n") if l.strip() and not l.startswith("[")]
            for line in lines:
                extracted_scenes.append(line)
        
        # Se ci sono troppe poche righe, suddividiamo meglio, altrimenti prendiamo fino a 30 scene chiave
        if len(extracted_scenes) > 30:
            step = len(extracted_scenes) // 30
            scenes = extracted_scenes[::step][:30]
        else:
            scenes = extracted_scenes if extracted_scenes else ["Party atmosphere", "Romantic moment", "Happy family"]

        primary_member = st.session_state.cast_members[0]
        ref_image_url = primary_member.get("photo_url")
        cast_desc = f"{primary_member['name']}, {primary_member['desc']}"
        
        st.session_state.storyboard_scenes = []
        
        progress_bar = st.progress(0)
        total_s = len(scenes)
        
        for idx, scene_text in enumerate(scenes):
            try:
                image_prompt = (
                    f"{current_style_prompt}. "
                    f"The exact same identical person: {cast_desc}. "
                    f"Consistent facial features, same face, same hair style across all scenes. "
                    f"Action/Setting: {scene_text}."
                )
                
                if ref_image_url:
                    img_res = fal_client.subscribe(
                        "fal-ai/flux-pulid",
                        arguments={
                            "prompt": image_prompt,
                            "reference_image_url": ref_image_url,
                            "id_weight": 0.95,
                            "mode": "fidelity"
                        }
                    )
                else:
                    img_res = fal_client.subscribe(
                        "fal-ai/flux/dev",
                        arguments={
                            "prompt": image_prompt,
                            "image_size": "landscape_16_9",
                            "num_inference_steps": 28
                        }
                    )
                
                image_url = img_res["images"][0]["url"]
                
                # Generazione clip video associata
                video_prompt = f"Dynamic video animation, {current_style_prompt}, featuring {cast_desc}, action: {scene_text}"
                video_res = generate_video_auto_fallback(video_prompt, image_url=image_url)
                clip_url = video_res["video"]["url"] if "video" in video_res else None
                
                st.session_state.storyboard_scenes.append({
                    "id": idx + 1,
                    "text": scene_text,
                    "prompt": image_prompt,
                    "image_url": image_url,
                    "clip_url": clip_url
                })
                
            except Exception as e:
                if "EXHAUSTED_BALANCE" in str(e) or "Exhausted balance" in str(e):
                    st.error("💳 **Crediti esauriti durante la produzione!** Ricarica per continuare.")
                    break
                st.warning(f"Errore nella scena {idx+1}: {e}")
                
            progress_bar.progress((idx + 1) / total_s)
            
        st.success("🎉 **Generazione delle scene completata!** Ora puoi revisionare, modificare o approvare il video qui sotto.")

# ---------------------------------------------------------
# STEP 4: PANNELLO DI REVISIONE E MODIFICA UMANA
# ---------------------------------------------------------
if st.session_state.storyboard_scenes:
    st.markdown("---")
    st.subheader("🔍 Pannello di Revisione Umana & Modifiche")
    st.markdown("Controlla le scene generate. Se una scena non ti convince, puoi modificare il testo del prompt e rigenerarla singolarmente prima di creare il video finale.")

    for s_idx, scene in enumerate(st.session_state.storyboard_scenes):
        with st.expander(f"🎬 Scena {scene['id']}: \"{scene['text'][:40]}...\""):
            c1, c2 = st.columns(2)
            with c1:
                st.image(scene['image_url'], caption=f"Frame Scena {scene['id']}", use_column_width=True)
            with c2:
                if scene['clip_url']:
                    st.video(scene['clip_url'])
                else:
                    st.warning("Clip video non disponibile.")
            
            # Area di modifica personalitazzata per singola scena
            new_prompt_edit = st.text_area(f"Modifica Prompt Scena {scene['id']}", value=scene['prompt'], key=f"edit_p_{s_idx}")
            
            if st.button(f"🔄 Rigenera Solo Scena {scene['id']}", key=f"re_gen_{s_idx}"):
                with st.spinner(f"Rigenerazione Scena {scene['id']} in corso..."):
                    try:
                        primary_member = st.session_state.cast_members[0]
                        ref_image_url = primary_member.get("photo_url")
                        
                        if ref_image_url:
                            img_res = fal_client.subscribe(
                                "fal-ai/flux-pulid",
                                arguments={
                                    "prompt": new_prompt_edit,
                                    "reference_image_url": ref_image_url,
                                    "id_weight": 0.95,
                                    "mode": "fidelity"
                                }
                            )
                        else:
                            img_res = fal_client.subscribe(
                                "fal-ai/flux/dev",
                                arguments={
                                    "prompt": new_prompt_edit,
                                    "image_size": "landscape_16_9",
                                    "num_inference_steps": 28
                                }
                            )
                        
                        new_img_url = img_res["images"][0]["url"]
                        vid_res = generate_video_auto_fallback(new_prompt_edit, image_url=new_img_url)
                        new_clip_url = vid_res["video"]["url"] if "video" in vid_res else None
                        
                        # Aggiorna lo stato locale
                        st.session_state.storyboard_scenes[s_idx]['prompt'] = new_prompt_edit
                        st.session_state.storyboard_scenes[s_idx]['image_url'] = new_img_url
                        st.session_state.storyboard_scenes[s_idx]['clip_url'] = new_clip_url
                        
                        st.success(f"Scena {scene['id']} rigenerata con successo!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Errore durante la rigenerazione: {ex}")

    # ---------------------------------------------------------
    # STEP 5: APPROVAZIONE FINALE E DOWNLOAD
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("✨ Approvazione & Esportazione Finale")
    
    if st.button("✅ Approvo il Video: Crea Videoclip Finale"):
        st.balloons()
        st.success("🎉 **Videoclip Approvato e Pronto!** Ecco i link di tutte le clip validate pronte per il montaggio finale:")
        
        for scene in st.session_state.storyboard_scenes:
            if scene['clip_url']:
                st.markdown(f"- **Scena {scene['id']}**: [Scarica Clip MP4]({scene['clip_url']})")
