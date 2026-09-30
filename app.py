"""
=============================================================================
PROPRIETARY & CONFIDENTIAL CONTENT GENERATOR ENGINE
-----------------------------------------------------------------------------
Author / Creator Signature: Dony Telim
Project: Factory Content Studio - Commercial Grade Edition
Copyright (c) 2026 CONTENT FACTORY. All Rights Reserved.
Unauthorized distribution, resale, or reverse engineering is strictly prohibited.
=============================================================================
"""

import streamlit as st
import time
import json
import random
import os
import re
import pandas as pd
from groq import Groq

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CSS (MOBILE-FRIENDLY & CONTENT FACTORY BRANDING)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Factory Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Styling Dasar & Responsif untuk Mobile */
    .main .block-container { 
        padding-top: 1rem; 
        padding-bottom: 2rem; 
        padding-left: 1rem; 
        padding-right: 1rem; 
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        font-weight: bold; 
    }
    div[data-testid="stSidebarUserContent"] { 
        padding-top: 1rem; 
    }
    .footer-brand { 
        text-align: center; 
        font-size: 0.8rem; 
        color: #888888; 
        padding: 20px 0; 
        border-top: 1px solid #333333; 
        margin-top: 30px; 
    }
    .activation-box {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: #cccccc;
        line-height: 1.5;
    }
    .activation-box a {
        color: #4da6ff;
        text-decoration: none;
        font-weight: bold;
    }
    .activation-box a:hover {
        text-decoration: underline;
    }
    
    /* Optimasi Tampilan Mobile / Layar Kecil */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        .stButton>button {
            height: 3.2em;
            font-size: 0.95rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FILE PENYIMPANAN DATABASE & PROYEK TERISOLASI PER AKUN
# -----------------------------------------------------------------------------
CSV_FILE = "license.csv"

@st.cache_data(ttl=1)
def load_users():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, dtype=str)
            df.columns = df.columns.str.strip()
            if "email" in df.columns:
                df["email"] = df["email"].str.strip()
            if "active_session" in df.columns:
                df["active_session"] = df["active_session"].str.strip()
            return df
        except:
            return pd.DataFrame(columns=["email", "expired_date", "active_session"])
    else:
        return pd.DataFrame(columns=["email", "expired_date", "active_session"])

def update_user_activation(user_email, activation_key):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, dtype=str)
        df.columns = df.columns.str.strip()
        df["email"] = df["email"].str.strip()
        df.loc[df["email"] == user_email, "active_session"] = activation_key.strip()
        df.to_csv(CSV_FILE, index=False)

# Fungsi riwayat proyek spesifik berdasarkan email pengguna (Isolasi Data)
def get_user_history_filename(email):
    safe_email = re.sub(r'[^a-zA-Z0-9]', '_', email)
    return f".recent_projects_{safe_email}.json"

def load_recent_projects(email):
    if not email:
        return {}
    filename = get_user_history_filename(email)
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_project_to_history(email, title, show_bible, scenes):
    if not email:
        return
    filename = get_user_history_filename(email)
    projects = load_recent_projects(email)
    projects[title] = {
        "show_bible": show_bible,
        "scenes": scenes,
        "timestamp": time.strftime("%Y-%m-%d %H:%M")
    }
    with open(filename, "w") as f:
        json.dump(projects, f, indent=2)

# -----------------------------------------------------------------------------
# 3. PRESET LISTS (STANDARD & EXTENDED)
# -----------------------------------------------------------------------------
VIDEO_TYPES = [
    "Auto AI / Smart Mode (Default)",
    "Music Video / Karaoke Visualizer",
    "Short Drama / Mini Series / Film Story",
    "Movie Cinematic / Trailer",
    "Iklan / Affiliate Product / Marketing",
    "Fakta Unik / Edukasi / Dokumenter",
    "Horor / Thriller / Misteri",
    "Motivasi / Podcast Visual / Quote",
    "✏️ Custom Type..."
]

VISUAL_STYLES = [
    "Auto AI / Smart Match (Default)",
    "Cinematic Photorealistic (8k, Moody Lighting, 35mm Lens)",
    "Tilt-Shift / Diorama Miniature World",
    "Claymation / Stop-Motion Animation",
    "3D Animation / Pixar & DreamWorks Style",
    "2D Anime / Japanese Animation (Makoto Shinkai Style)",
    "Papercraft / Cutout Origami Art",
    "Cyberpunk / Neon Future Aesthetic",
    "Vintage 80s / 90s VHS Retro Aesthetic",
    "Dark Fantasy / Gothic Oil Painting",
    "Vector Flat Design / Minimalist Motion",
    "Isometric 3D / Low Poly Art",
    "✏ Custom Visual Style..."
]

IMAGE_ENGINES = [
    "Auto AI / Universal (Default)",
    "Midjourney (v6 / Niji 6)",
    "FLUX.1 (Dev / Schnell / Pro)",
    "Stable Diffusion (SDXL / SD 3.5)",
    "Ideogram 2.0 (Text/Typography Focused)",
    "DALL-E 3 (OpenAI)",
    "Leonardo AI / Recraft",
    "✏️ Custom Image Engine..."
]

VIDEO_ENGINES = [
    "Auto AI / Universal (Default)",
    "Google Veo / Flow",
    "Kling AI (v1.5 / v2)",
    "Hailuo AI / Minimax",
    "Runway (Gen-3 Alpha / Gen-2)",
    "Luma Dream Machine",
    "Pika Labs (2.0)",
    "CogVideoX / Hunyuan Video",
    "✏️ Custom Video Engine..."
]

ASPECT_RATIOS = [
    "Auto AI / 16:9 Landscape (Default)",
    "9:16 Vertical (TikTok/Reels/Shorts)",
    "1:1 Square (Feed)",
    "21:9 Ultrawide Cinematic",
    "✏ Custom Ratio..."
]

DURATION_OPTIONS = [
    "AI AUTO / Flexible (Default)",
    "3 Detik per Adegan",
    "5 Detik per Adegan",
    "6 Detik per Adegan",
    "10 Detik per Adegan",
    "✏️ Custom Durasi..."
]

SCENE_COUNT_OPTIONS = [
    "AI AUTO / Flexible (Default)",
    "4 Scene",
    "5 Scene",
    "8 Scene",
    "10 Scene (Maksimal)",
    "✏ Custom (Maksimal 10)..."
]

VOICE_TYPES = [
    "AI AUTO / Adaptif (Default)",
    "Narasi / Voiceover Only",
    "Dialog Karakter Only",
    "Gabungan (Narasi + Dialog)"
]

NARRATOR_GENDER_OPTIONS = [
    "AI AUTO / Bebas (Default)",
    "Pria (Male Voice)",
    "Wanita (Female Voice)",
    "Duet / Pergantian (Male & Female Voice)"
]

LANGUAGE_OPTIONS = [
    "AI AUTO / Ikuti Input (Default)",
    "Bahasa Indonesia",
    "Bahasa Inggris (English)",
    "✏️ Custom Bahasa..."
]

CAMERA_SHOT_OPTIONS = [
    "AI AUTO / Smart Framing (Default)",
    "Extreme Wide Shot / Landscape Overview",
    "Wide Shot / Full Body Action",
    "Medium Shot / Waist Up Character Focus",
    "Close-Up / Facial Emotion Focus",
    "Extreme Close-Up / Eye & Detail Focus",
    "Low Angle / Hero Dynamic Shot",
    "High Angle / Top-Down Bird's Eye View",
    "Drone Flythrough / Tracking Shot",
    "Orbiting Dynamic Camera Motion",
    "✏️️ Custom Camera Shot..."
]

LIGHTING_OPTIONS = [
    "AI AUTO / Natural Dynamic (Default)",
    "Golden Hour / Warm Sunset Glow",
    "Cinematic Moody / High-Contrast Chiaroscuro",
    "Volumetric Fog & God Rays",
    "Neon Cyberpunk Glow / Vibrant Lights",
    "Soft Studio Portrait Lighting",
    "Dramatic Dark & Shadowy (Horror/Thriller)",
    "Bright Natural Sunlight",
    "✏️ Custom Lighting..."
]

COLOR_GRADING_OPTIONS = [
    "AI AUTO / Standard Color (Default)",
    "Teal & Orange Hollywood Style",
    "Vintage Kodak / VHS Grain 90s Film",
    "Black & White / High-Contrast Film Noir",
    "Pastel Aesthetic / Soft Dreamy Tones",
    "Vibrant High-Saturated Color",
    "Desaturated Dark & Gritty",
    "✏️ Custom Color Grading..."
]

GROQ_MODELS = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]

# -----------------------------------------------------------------------------
# 4. HELPER: SAFE GROQ API CALL
# -----------------------------------------------------------------------------
def call_groq_safe(api_key, system_instruction, user_prompt, selected_model="openai/gpt-oss-120b", is_json=True, max_retries=3):
    client = Groq(api_key=api_key)
    models_to_try = [selected_model] + [m for m in GROQ_MODELS if m != selected_model]
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                kwargs = {
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_prompt}
                    ],
                    "model": model_name,
                    "temperature": 0.7
                }
                if is_json:
                    kwargs["response_format"] = {"type": "json_object"}
                
                chat_completion = client.chat.completions.create(**kwargs)
                res_text = chat_completion.choices[0].message.content
                
                if is_json:
                    return json.loads(res_text)
                return res_text
            except Exception as e:
                err_str = str(e)
                if "404" in err_str or "model_not_found" in err_str or "decommissioned" in err_str:
                    break 
                if attempt < max_retries - 1:
                    time.sleep((2 ** attempt) + random.uniform(0.5, 1.5))
    
    st.error("❌ Proses gagal diproses. Pastikan data aktivasi Anda valid.")
    return None

# -----------------------------------------------------------------------------
# 5. SESSION STATE INITIALIZATION & QUERY PARAMS (ANTI-LOGOUT SAAT REFRESH)
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "step" not in st.session_state:
    st.session_state.step = "input_email"
if "show_bible" not in st.session_state:
    st.session_state.show_bible = None
if "scenes" not in st.session_state:
    st.session_state.scenes = []

# Sinkronisasi parameter URL untuk pemulihan sesi otomatis saat browser di-refresh (khususnya di HP)
query_params = st.query_params
if not st.session_state.logged_in and "session_user" in query_params:
    saved_email = query_params["session_user"].strip()
    df_users = load_users()
    if not df_users.empty:
        user_match = df_users[df_users["email"] == saved_email]
        if not user_match.empty:
            saved_key = str(user_match.iloc[0]["active_session"]).strip()
            if saved_key != "" and saved_key != "nan" and pd.notna(saved_key):
                st.session_state.logged_in = True
                st.session_state.user_email = saved_email
                st.session_state.step = "app"

# =============================================================================
# 6. TAHAP AUTENTIKASI (LOGIN & AKTIVASI BERBASIS CSV)
# =============================================================================
if not st.session_state.logged_in:
    st.title("🔐 Login & Aktivasi Akun")
    st.write("Silakan masukkan akun terdaftar Anda untuk mengakses Factory Content Studio.")

    if st.session_state.step == "input_email":
        with st.form("email_form"):
            input_email = st.text_input("Masukkan Akun / Email:")
            submit_email = st.form_submit_button("Lanjut")

        if submit_email:
            clean_email = input_email.strip()
            if not clean_email:
                st.error("❌ Akun tidak boleh kosong!")
            else:
                df_users = load_users()
                if df_users.empty:
                    st.error("❌ File database 'license.csv' tidak ditemukan atau kosong!")
                else:
                    user_match = df_users[df_users["email"] == clean_email]
                    if not user_match.empty:
                        st.session_state.user_email = clean_email
                        saved_key = str(user_match.iloc[0]["active_session"]).strip()
                        
                        if saved_key != "" and saved_key != "nan" and pd.notna(saved_key):
                            st.session_state.logged_in = True
                            st.session_state.step = "app"
                            st.query_params["session_user"] = clean_email
                            st.rerun()
                        else:
                            st.session_state.step = "input_aktivasi"
                            st.rerun()
                    else:
                        st.error("❌ Akun tidak ditemukan di database!")

    elif st.session_state.step == "input_aktivasi":
        st.warning("⚠️ Akun Anda belum memiliki data aktivasi. Masukkan kode aktivasi Anda di bawah ini.")

        with st.form("aktivasi_form"):
            input_apikey = st.text_input("Masukkan Kode Aktivasi (Groq API Key):", type="password")
            submit_aktivasi = st.form_submit_button("Proses Aktivasi & Masuk")

        with st.expander("📖 Panduan Cara Mengambil Kode Aktivasi"):
            st.markdown("""
            1. Buka website [Groq Console](https://console.groq.com/keys).
            2. Masuk menggunakan akun Google atau GitHub Anda.
            3. Masuk ke menu **API Keys** dan klik **Create API Key**.
            4. Salin (copy) dan tempel (paste) kode api tersebut ke kolom di atas.
            """)

        if submit_aktivasi:
            clean_key = input_apikey.strip()
            if clean_key.startswith("gsk_"):
                update_user_activation(st.session_state.user_email, clean_key)
                st.session_state.logged_in = True
                st.session_state.step = "app"
                st.query_params["session_user"] = st.session_state.user_email
                st.success("✅ Aktivasi Berhasil! Memasuki aplikasi...")
                st.rerun()
            else:
                st.error("❌ Format aktivasi tidak valid! Harus diawali 'gsk_'")

        if st.button("⬅️ Kembali ke Input Akun"):
            st.session_state.step = "input_email"
            st.rerun()

# =============================================================================
# 7. APLIKASI UTAMA (JIKA SUDAH LOGIN / AKTIVASI OK)
# =============================================================================
else:
    # Ambil kunci aktivasi dari file CSV untuk akun yang sedang login
    df_users = load_users()
    current_row = df_users[df_users["email"] == st.session_state.user_email]
    active_activation_key = str(current_row.iloc[0]["active_session"]).strip()

    # -----------------------------------------------------------------------------
    # SIDEBAR CONTROL PANEL
    # -----------------------------------------------------------------------------
    with st.sidebar:
        st.title("🎬 Content Factory")
        st.caption("AI Script & Visual Asset Generator Engine")
        st.divider()

        # STATUS AKTIVASI DI SIDEBAR
        st.write(f"👤 **Akun:** `{st.session_state.user_email}`")
        st.markdown("---")
        st.markdown("🟢 **AKTIVASI OK**")
        st.markdown("---")

        if st.button("🚪 Logout / Ganti Akun"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.step = "input_email"
            if "session_user" in st.query_params:
                del st.query_params["session_user"]
            st.rerun()

        st.divider()

        # BLOCK 2: INPUT UTAMA
        project_title = st.text_input(
            "1. Judul / Ide Utama Video (WAJIB) *",
            placeholder="Misal: Kisah Tembok Besar China",
            key="project_title"
        )

        custom_notes = st.text_area(
            "2. Detail Cerita / Pesan Khusus AI (Opsional)",
            placeholder="Arahkan AI, misal: 'Fokuskan pada penderitaan fisik pekerja paksa di bawah cuaca ekstrem'...",
            height=120,
            key="custom_notes"
        )

        st.subheader("⚙ Parameter Utama")

        selected_type = st.selectbox("Jenis Video", VIDEO_TYPES)
        final_type = st.text_input("Tulis Jenis Video Khusus:", placeholder="Misal: Micro-Documentary") if selected_type == "✏️ Custom Type..." else selected_type

        selected_style = st.selectbox("Gaya Visual Graphics", VISUAL_STYLES)
        final_style = st.text_input("Tulis Gaya Visual Khusus:", placeholder="Misal: 1990s Dark Synthwave") if selected_style == "✏️ Custom Visual Style..." else selected_style

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            selected_img_engine = st.selectbox("Target Image Engine", IMAGE_ENGINES)
            final_img_engine = st.text_input("Image Engine Khusus:", placeholder="Misal: Recraft v3") if selected_img_engine == "✏️ Custom Image Engine..." else selected_img_engine

        with col_e2:
            selected_vid_engine = st.selectbox("Target Video Engine", VIDEO_ENGINES)
            final_vid_engine = st.text_input("Video Engine Khusus:", placeholder="Misal: Kling v2") if selected_vid_engine == "✏️ Custom Video Engine..." else selected_vid_engine

        selected_ratio = st.selectbox("Aspect Ratio / Format", ASPECT_RATIOS)
        final_ratio = st.text_input("Tulis Ratio Khusus:", placeholder="Misal: 4:3 Vintage") if selected_ratio == "✏ Custom Ratio..." else selected_ratio

        st.markdown("---")
        
        # ADVANCED VISUAL & CAMERA CONTROLS (EXPANDER)
        with st.expander("🎥 Advanced Camera & Lighting Controls (Opsional)", expanded=False):
            st.caption("Atur spesifikasi sinematografi mendalam:")
            
            selected_cam = st.selectbox("Sudut & Gerakan Kamera", CAMERA_SHOT_OPTIONS)
            final_cam = st.text_input("Sudut Kamera Khusus:", placeholder="Misal: Macro 100mm Focus") if selected_cam == "✏️ Custom Camera Shot..." else selected_cam

            selected_light = st.selectbox("Pencahayaan & Lighting", LIGHTING_OPTIONS)
            final_light = st.text_input("Lighting Khusus:", placeholder="Misal: Soft Neon Rim Light") if selected_light == "✏ Custom Lighting..." else selected_light

            selected_color = st.selectbox("Color Grading & Tone", COLOR_GRADING_OPTIONS)
            final_color = st.text_input("Color Grading Khusus:", placeholder="Misal: Vintage Sepia Tones") if selected_color == "✏️ Custom Color Grading..." else selected_color

        st.markdown("---")
        st.caption("🎬 **Kontrol Durasi & Audio**")

        selected_dur = st.selectbox("Durasi Per Adegan", DURATION_OPTIONS)
        if selected_dur == "✏️ Custom Durasi...":
            custom_dur_val = st.number_input("Input Angka Durasi (Detik):", min_value=1, max_value=120, value=5, step=1)
            final_duration = f"{custom_dur_val} Detik"
        else:
            final_duration = selected_dur

        selected_sc_count = st.selectbox("Jumlah Adegan (Maks 10)", SCENE_COUNT_OPTIONS)
        if selected_sc_count == "✏ Custom (Maksimal 10)...":
            custom_sc_val = st.number_input("Input Jumlah Adegan (1-10):", min_value=1, max_value=10, value=5, step=1)
            final_scene_count = f"{custom_sc_val} Scene"
        else:
            final_scene_count = selected_sc_count

        final_voice = st.selectbox("Format Voice / Suara", VOICE_TYPES)
        final_gender = st.selectbox("Profil / Gender Narator", NARRATOR_GENDER_OPTIONS)

        selected_lang = st.selectbox("Bahasa Naskah / Narasi", LANGUAGE_OPTIONS)
        final_language = st.text_input("Tulis Bahasa Khusus:", placeholder="Misal: Bahasa Jawa / Jepang") if selected_lang == "✏️ Custom Bahasa..." else selected_lang

        st.markdown("---")

        selected_model = st.selectbox(
            "Mode Performa Engine",
            options=["openai/gpt-oss-120b", "llama-3.3-70b-versatile"],
            index=0
        )

        st.divider()

        build_btn = st.button("🚀 BUILD PROJECT BIBLE & SCENES", type="primary")
        
        if st.button("🔄 Reset / Buat Proyek Baru"):
            st.session_state.show_bible = None
            st.session_state.scenes = []
            st.rerun()

        st.divider()

        # BLOCK 4: RECENT PROJECTS (TERISOLASI BERDASARKAN EMAIL)
        st.subheader("📂 Recent Projects")
        recent_dict = load_recent_projects(st.session_state.user_email)
        if recent_dict:
            selected_project_name = st.selectbox(
                "Pilih Proyek Sebelumnya:",
                options=["-- Pilih Proyek --"] + list(recent_dict.keys())
            )
            if selected_project_name != "-- Pilih Proyek --":
                if st.button("📂 Buka Proyek Ini"):
                    proj_data = recent_dict[selected_project_name]
                    st.session_state.show_bible = proj_data["show_bible"]
                    st.session_state.scenes = proj_data["scenes"]
                    st.success(f"Proyek '{selected_project_name}' berhasil dimuat!")
                    st.rerun()

    # -----------------------------------------------------------------------------
    # 8. MAIN CANVAS & SEQUENTIAL GENERATION LOGIC
    # -----------------------------------------------------------------------------
    st.title("🎬 Main Canvas & Script Studio")

    if build_btn:
        if not active_activation_key or not active_activation_key.startswith("gsk_"):
            st.error("⚠ Data aktivasi akun Anda tidak valid!")
        elif not project_title.strip():
            st.error("⚠️ Judul / Ide Utama Video wajib diisi terlebih dahulu!")
        else:
            with st.spinner("⏳ Menghubungkan ke Engine & Menyiapkan Adegan..."):
                sys_instruct = """
                You are 'Factory Content Engine', an elite AI scriptwriter and visual asset director.
                Generate a JSON object containing two main keys:
                1. 'show_bible': Object containing summary of main_character, visual_theme, mood, continuity_rules, narrator_profile.
                2. 'scenes': Array of objects, each containing:
                   - 'scene_num': integer
                   - 'narration': string (Voiceover text in requested language)
                   - 'dialogue': string (Character speech in requested language)
                
                STRICT NARRATION / DIALOGUE WORD LIMITS BASED ON DURATION:
                - 3 Seconds: MAXIMUM 7-9 WORDS per scene.
                - 5 Seconds: MAXIMUM 12-15 WORDS per scene.
                - 6 Seconds: MAXIMUM 15-18 WORDS per scene.
                - 10 Seconds: MAXIMUM 25-30 WORDS per scene.
                Return strictly valid JSON only.
                """

                user_prompt = f"""
                PROJECT SPECS:
                - Title/Idea: {project_title}
                - Custom Notes & Special Guidance: {custom_notes if custom_notes else 'None'}
                - Video Type: {final_type}
                - Visual Style: {final_style}
                - Target Image AI Engine: {final_img_engine}
                - Target Video AI Engine: {final_vid_engine}
                - Aspect Ratio: {final_ratio}
                - Camera Framing Preset: {final_cam}
                - Lighting Preset: {final_light}
                - Color Grading Preset: {final_color}
                - STRICT Target Scene Duration: {final_duration}
                - Requested Scene Count Limit: {final_scene_count} (STRICT MAXIMUM: 10 scenes)
                - Voice/Audio Style Selected: {final_voice}
                - Narrator Profile/Gender: {final_gender}
                - Script Target Language: {final_language}
                """

                result = call_groq_safe(
                    api_key=active_activation_key,
                    system_instruction=sys_instruct,
                    user_prompt=user_prompt,
                    selected_model=selected_model,
                    is_json=True
                )

                if result:
                    show_bible_data = result.get("show_bible", {})
                    show_bible_data["title"] = project_title
                    show_bible_data["image_engine"] = final_img_engine
                    show_bible_data["video_engine"] = final_vid_engine
                    show_bible_data["ratio"] = final_ratio
                    show_bible_data["camera_spec"] = final_cam
                    show_bible_data["lighting_spec"] = final_light
                    show_bible_data["color_spec"] = final_color
                    show_bible_data["duration_setting"] = final_duration
                    show_bible_data["language_setting"] = final_language
                    show_bible_data["voice_setting"] = final_voice
                    show_bible_data["narrator_gender"] = final_gender

                    scenes_input = result.get("scenes", [])
                    
                    formatted_scenes = []
                    for idx, sc in enumerate(scenes_input):
                        formatted_scenes.append({
                            "scene_num": sc.get("scene_num", idx + 1),
                            "narration": sc.get("narration", ""),
                            "dialogue": sc.get("dialogue", ""),
                            "prompt_image": "",
                            "prompt_video": "",
                            "is_unlocked": True if idx == 0 else False
                        })

                    st.session_state.show_bible = show_bible_data
                    st.session_state.scenes = formatted_scenes

                    save_project_to_history(st.session_state.user_email, project_title, show_bible_data, formatted_scenes)
                    st.success("✅ Project Bible & Adegan berhasil dibuat!")

    # DISPLAY MAIN CANVAS
    if st.session_state.show_bible:
        with st.expander("🟢 PROJECT BIBLE (Locked Continuity Rules)", expanded=True):
            col1, col2, col3 = st.columns(3)
            sb = st.session_state.show_bible
            with col1:
                st.write(f"**Judul:** {sb.get('title', '-')}")
                st.write(f"**Karakter Utama:** {sb.get('main_character', '-')}")
                st.write(f"**Bahasa Naskah:** {sb.get('language_setting', '-')}")
                st.write(f"**Profil Narator:** {sb.get('narrator_gender', '-')}")
            with col2:
                st.write(f"**Visual Theme:** {sb.get('visual_theme', '-')}")
                st.write(f"**Target Image Engine:** {sb.get('image_engine', '-')}")
                st.write(f"**Target Video Engine:** {sb.get('video_engine', '-')}")
                st.write(f"**Setting Durasi:** {sb.get('duration_setting', '-')}")
            with col3:
                st.write(f"**Format Ratio:** {sb.get('ratio', '-')}")
                st.write(f"**Kamera/Framing:** {sb.get('camera_spec', '-')}")
                st.write(f"**Lighting/Color:** {sb.get('lighting_spec', '-')} / {sb.get('color_spec', '-')}")

        st.divider()

        with st.expander("📋 Export All Script (Salin Seluruh Narasi & Dialog)", expanded=False):
            full_script_txt = ""
            for sc in st.session_state.scenes:
                full_script_txt += f"Adegan {sc['scene_num']}:\n"
                if sc['narration'] and sc['narration'] != "-":
                    full_script_txt += f"Narasi: {sc['narration']}\n"
                if sc['dialogue'] and sc['dialogue'] != "-":
                    full_script_txt += f"Dialog: {sc['dialogue']}\n"
                full_script_txt += "\n"
            st.text_area("Salin teks naskah di bawah ini:", value=full_script_txt.strip(), height=150)

        st.divider()

        st.subheader("🎬 Breakdown Prompt & Naskah Per Adegan")

        IMG_PROMPT_SYS = """You are a master AI Image Prompt Engineer (Midjourney, FLUX, Stable Diffusion).
        CRITICAL RULES:
        1. Output MUST be ONLY the specific image prompt for the SINGLE SCENE requested in English.
        2. VISUAL vs AUDIO SEPARATION: Narration is AUDIO ONLY.
        3. Incorporate requested camera framing, lighting, and color grading specs organically."""

        VID_PROMPT_SYS = """You are a master AI Video Prompt Engineer for multimodal audio-video engines.
        CRITICAL RULES:
        1. Output MUST be ONLY the single-scene video prompt in English.
        2. EXPLICITLY separate Voiceover/Narration audio from Character Dialogue audio in instructions."""

        for sc_idx, sc in enumerate(st.session_state.scenes):
            s_num = sc["scene_num"]
            is_unlocked = sc["is_unlocked"]

            with st.container(border=True):
                if not is_unlocked:
                    st.markdown(f"### 🔒 Adegan {s_num} (Terkunci)")
                    st.caption(f"Selesaikan pembuatan Prompt pada **Adegan {s_num-1}** terlebih dahulu.")
                else:
                    st.markdown(f"### 🟢 Adegan {s_num}")
                    
                    nar_txt = sc['narration'] if sc['narration'] and sc['narration'] != "-" else "N/A"
                    dia_txt = sc['dialogue'] if sc['dialogue'] and sc['dialogue'] != "-" else "N/A"
                    
                    word_cnt = len(nar_txt.split()) if nar_txt != "N/A" else 0
                    st.markdown(f"🎙️ **Narasi:** {nar_txt} `({word_cnt} kata)`")
                    st.markdown(f"💬 **Dialog:** {dia_txt}")

                    st.markdown("---")

                    col_p1, col_p2 = st.columns(2)

                    with col_p1:
                        st.markdown("#### 🖼️ Prompt Image")
                        p_user_img = f"Project Context: {st.session_state.show_bible}\nTarget Image Engine: {st.session_state.show_bible.get('image_engine', 'Universal')}\nTarget Scene: {s_num}\nNarration Context: {nar_txt}\nDialogue Context: {dia_txt}\nGenerate a single cinematic image prompt for Scene {s_num} ONLY."
                        
                        if sc["prompt_image"]:
                            st.code(sc["prompt_image"], language="markdown")
                            if st.button(f"🔄 Regenerate Prompt Image {s_num}", key=f"btn_regen_img_{s_num}"):
                                with st.spinner(f"Mengkoreksi Prompt Image Adegan {s_num}..."):
                                    new_img_p = call_groq_safe(active_activation_key, IMG_PROMPT_SYS, p_user_img, selected_model, is_json=False)
                                    if new_img_p:
                                        st.session_state.scenes[sc_idx]["prompt_image"] = new_img_p.strip()
                                        save_project_to_history(st.session_state.user_email, st.session_state.show_bible["title"], st.session_state.show_bible, st.session_state.scenes)
                                        st.rerun()
                        else:
                            if st.button(f"✨ Generate Prompt Image {s_num}", key=f"btn_gen_img_{s_num}", type="primary"):
                                with st.spinner(f"Membuat Prompt Image Adegan {s_num}..."):
                                    new_img_p = call_groq_safe(active_activation_key, IMG_PROMPT_SYS, p_user_img, selected_model, is_json=False)
                                    if new_img_p:
                                        st.session_state.scenes[sc_idx]["prompt_image"] = new_img_p.strip()
                                        save_project_to_history(st.session_state.user_email, st.session_state.show_bible["title"], st.session_state.show_bible, st.session_state.scenes)
                                        st.rerun()

                    with col_p2:
                        st.markdown("#### 🎥 Prompt Video (Narasi + Dialog Audio)")
                        p_user_vid = f"Project Context: {st.session_state.show_bible}\nTarget Video Engine: {st.session_state.show_bible.get('video_engine', 'Universal')}\nTarget Scene: {s_num}\nRequested Duration: {st.session_state.show_bible.get('duration_setting', '5 Detik')}\nEXACT NARRATION: \"{nar_txt}\"\nEXACT DIALOGUE: \"{dia_txt}\"\nGenerate video motion prompt for Scene {s_num} ONLY."

                        if sc["prompt_video"]:
                            st.code(sc["prompt_video"], language="markdown")
                            if st.button(f"🔄 Regenerate Prompt Video {s_num}", key=f"btn_regen_vid_{s_num}"):
                                with st.spinner(f"Mengkoreksi Prompt Video Adegan {s_num}..."):
                                    new_vid_p = call_groq_safe(active_activation_key, VID_PROMPT_SYS, p_user_vid, selected_model, is_json=False)
                                    if new_vid_p:
                                        st.session_state.scenes[sc_idx]["prompt_video"] = new_vid_p.strip()
                                        if sc_idx + 1 < len(st.session_state.scenes):
                                            st.session_state.scenes[sc_idx + 1]["is_unlocked"] = True
                                        save_project_to_history(st.session_state.user_email, st.session_state.show_bible["title"], st.session_state.show_bible, st.session_state.scenes)
                                        st.rerun()
                        else:
                            if st.button(f"✨ Generate Prompt Video {s_num}", key=f"btn_gen_vid_{s_num}", type="primary"):
                                with st.spinner(f"Membuat Prompt Video Adegan {s_num}..."):
                                    new_vid_p = call_groq_safe(active_activation_key, VID_PROMPT_SYS, p_user_vid, selected_model, is_json=False)
                                    if new_vid_p:
                                        st.session_state.scenes[sc_idx]["prompt_video"] = new_vid_p.strip()
                                        if sc_idx + 1 < len(st.session_state.scenes):
                                            st.session_state.scenes[sc_idx + 1]["is_unlocked"] = True
                                        save_project_to_history(st.session_state.user_email, st.session_state.show_bible["title"], st.session_state.show_bible, st.session_state.scenes)
                                        st.rerun()

    else:
        st.info("👈 Masukkan **Judul Proyek** & atur parameter di Sidebar sebelah kiri, lalu klik **BUILD PROJECT BIBLE & SCENES** untuk memulai!")

# -----------------------------------------------------------------------------
# FOOTER & COPYRIGHT NOTICE
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer-brand">
        Copyright &copy; 2026 <b>CONTENT FACTORY</b>. All Rights Reserved.<br>
        Dilarang keras menyebarluaskan, memperbanyak, atau memperjualbelikan aplikasi atau kode sumber ini tanpa izin tertulis dari pemegang hak cipta.
    </div>
""", unsafe_allow_html=True)
