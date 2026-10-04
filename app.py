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
from datetime import date, datetime
from groq import Groq

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Factory Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
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
    .api-guide {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff4b4b;
        margin-bottom: 15px;
        font-size: 0.9rem;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        .stButton>button { height: 3.2em; font-size: 0.95rem; }
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FILE CSV & MANAJEMEN LISENSI
# -----------------------------------------------------------------------------
CSV_FILE = "license.csv"

def load_users():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, dtype=str)
            df.columns = df.columns.str.strip().str.lower()
            if "email" in df.columns:
                df["email"] = df["email"].str.strip().str.lower()
            if "expired_date" not in df.columns:
                df["expired_date"] = "2026-12-31"
            return df
        except:
            return pd.DataFrame(columns=["email", "expired_date"])
    else:
        default_df = pd.DataFrame([
            {"email": "master", "expired_date": "2026-12-31"}
        ])
        default_df.to_csv(CSV_FILE, index=False)
        return default_df

def check_user_license(username):
    clean_name = username.strip().lower()
    df = load_users()
    if df.empty or "email" not in df.columns:
        return False, "Database lisensi kosong."
    
    match = df[df["email"] == clean_name]
    if match.empty:
        return False, "ID/Username tidak terdaftar di database lisensi!"
    
    exp_date_str = match.iloc[0].get("expired_date", "2026-12-31")
    try:
        exp_date = datetime.strptime(str(exp_date_str).strip(), "%Y-%m-%d").date()
        if date.today() > exp_date:
            return False, f"Lisensi Anda telah kedaluwarsa pada {exp_date_str}!"
    except:
        pass
    return True, "Lisensi Aktif"

# -----------------------------------------------------------------------------
# 3. MANAJEMEN SESSION & STORAGE LOKAL
# -----------------------------------------------------------------------------
def get_device_token_filename(username):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', username)
    return f".device_token_{safe_name}.json"

def get_device_apikey_filename(username):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', username)
    return f".device_apikey_{safe_name}.json"

def save_device_token(username, token):
    if not username: return
    with open(get_device_token_filename(username), "w") as f:
        json.dump({"token": token, "time": time.time()}, f)

def check_device_token(username, token):
    if not username: return True
    filename = get_device_token_filename(username)
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f).get("token") == token
        except:
            return True
    return True

def save_device_local_apikey(username, api_key):
    if not username or not api_key: return
    try:
        with open(get_device_apikey_filename(username), "w") as f:
            json.dump({"api_key": api_key}, f)
    except:
        pass

def load_device_local_apikey(username):
    if not username: return ""
    filename = get_device_apikey_filename(username)
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f).get("api_key", "")
        except:
            return ""
    return ""

def get_user_history_filename(username):
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', username)
    return f".private_history_{safe_name}.json"

def load_recent_projects(username):
    if not username: return {}
    filename = get_user_history_filename(username)
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_project_to_history(username, title, show_bible, scenes, characters, brief_text):
    if not username: return
    filename = get_user_history_filename(username)
    projects = load_recent_projects(username)
    projects[title] = {
        "show_bible": show_bible,
        "scenes": scenes,
        "characters": characters,
        "brief_text": brief_text,
        "timestamp": time.strftime("%Y-%m-%d %H:%M")
    }
    with open(filename, "w") as f:
        json.dump(projects, f, indent=2)

def delete_project_from_history(username, title):
    if not username: return
    filename = get_user_history_filename(username)
    projects = load_recent_projects(username)
    if title in projects:
        del projects[title]
        with open(filename, "w") as f:
            json.dump(projects, f, indent=2)

# -----------------------------------------------------------------------------
# 4. PRESET LISTS
# -----------------------------------------------------------------------------
VIDEO_TYPES = ["Auto AI / Smart Mode (Default)", "Music Video / Karaoke Visualizer", "Short Drama / Mini Series / Film Story", "Movie Cinematic / Trailer", "Iklan / Affiliate Product / Marketing", "Fakta Unik / Edukasi / Dokumenter", "Horor / Thriller / Misteri", "Motivasi / Podcast Visual / Quote", "✏ Custom Type..."]
VISUAL_STYLES = ["Auto AI / Smart Match (Default)", "Cinematic Photorealistic (8k, Moody Lighting, 35mm Lens)", "Tilt-Shift / Diorama Miniature World", "Claymation / Stop-Motion Animation", "3D Animation / Pixar & DreamWorks Style", "2D Anime / Japanese Animation (Makoto Shinkai Style)", "Papercraft / Cutout Origami Art", "Cyberpunk / Neon Future Aesthetic", "Vintage 80s / 90s VHS Retro Aesthetic", "Dark Fantasy / Gothic Oil Painting", "Vector Flat Design / Minimalist Motion", "Isometric 3D / Low Poly Art", "✏ Custom Visual Style..."]
IMAGE_ENGINES = ["Auto AI / Universal (Default)", "Midjourney (v6 / Niji 6)", "FLUX.1 (Dev / Schnell / Pro)", "Stable Diffusion (SDXL / SD 3.5)", "Ideogram 2.0 (Text/Typography Focused)", "DALL-E 3 (OpenAI)", "Leonardo AI / Recraft", "✏️ Custom Image Engine..."]
VIDEO_ENGINES = ["Auto AI / Universal (Default)", "Google Veo / Flow", "Kling AI (v1.5 / v2)", "Hailuo AI / Minimax", "Runway (Gen-3 Alpha / Gen-2)", "Luma Dream Machine", "Pika Labs (2.0)", "CogVideoX / Hunyuan Video", "✏️ Custom Video Engine..."]
ASPECT_RATIOS = ["Auto AI / 16:9 Landscape (Default)", "9:16 Vertical (TikTok/Reels/Shorts)", "1:1 Square (Feed)", "21:9 Ultrawide Cinematic", "✏ Custom Ratio..."]
DURATION_OPTIONS = ["AI AUTO / Flexible (Default)", "3 Detik per Adegan", "5 Detik per Adegan", "6 Detik per Adegan", "10 Detik per Adegan", "✏️ Custom Durasi..."]
SCENE_COUNT_OPTIONS = ["AI AUTO / Flexible (Default)", "4 Scene", "5 Scene", "8 Scene", "10 Scene (Maksimal)", "✏ Custom (Maksimal 10)..."]
VOICE_MODE_OPTIONS = ["AI Auto / Bebas", "Narasi", "Dialog"]
LANGUAGE_OPTIONS = ["AI AUTO / Ikuti Input (Default)", "Bahasa Indonesia", "Bahasa Inggris (English)", "✏ Custom Bahasa..."]
CAMERA_SHOT_OPTIONS = ["AI AUTO / Smart Framing (Default)", "Extreme Wide Shot / Landscape Overview", "Wide Shot / Full Body Action", "Medium Shot / Waist Up Character Focus", "Close-Up / Facial Emotion Focus", "Extreme Close-Up / Eye & Detail Focus", "Low Angle / Hero Dynamic Shot", "High Angle / Top-Down Bird's Eye View", "Drone Flythrough / Tracking Shot", "Orbiting Dynamic Camera Motion", "✏ Custom Camera Shot..."]
LIGHTING_OPTIONS = ["AI AUTO / Natural Dynamic (Default)", "Golden Hour / Warm Sunset Glow", "Cinematic Moody / High-Contrast Chiaroscuro", "Volumetric Fog & God Rays", "Neon Cyberpunk Glow / Vibrant Lights", "Soft Studio Portrait Lighting", "Dramatic Dark & Shadowy (Horror/Thriller)", "Bright Natural Sunlight", "✏ Custom Lighting..."]
COLOR_GRADING_OPTIONS = ["AI AUTO / Standard Color (Default)", "Teal & Orange Hollywood Style", "Vintage Kodak / VHS Grain 90s Film", "Black & White / High-Contrast Film Noir", "Pastel Aesthetic / Soft Dreamy Tones", "Vibrant High-Saturated Color", "Desaturated Dark & Gritty", "✏ Custom Color Grading..."]
GROQ_MODELS = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]

# -----------------------------------------------------------------------------
# 5. HELPER: SAFE GROQ API CALL
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
    
    st.error("❌ Proses gagal diproses. Periksa kembali API Key Groq Anda.")
    return None

# -----------------------------------------------------------------------------
# 6. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "current_device_token" not in st.session_state: st.session_state.current_device_token = ""
if "local_api_key" not in st.session_state: st.session_state.local_api_key = ""
if "step" not in st.session_state: st.session_state.step = "input_email"
if "show_bible" not in st.session_state: st.session_state.show_bible = None
if "scenes" not in st.session_state: st.session_state.scenes = []
if "characters" not in st.session_state: st.session_state.characters = []
if "brief_text" not in st.session_state: st.session_state.brief_text = ""
if "reset_count" not in st.session_state: st.session_state.reset_count = 0
if "input_title_val" not in st.session_state: st.session_state.input_title_val = ""
if "input_notes_val" not in st.session_state: st.session_state.input_notes_val = ""

# =============================================================================
# 7. TAHAP AUTENTIKASI / LOGIN & DEVICE BINDING
# =============================================================================
if not st.session_state.logged_in:
    st.title("🔐 Login & Aktivasi Perangkat")
    st.write("Masukkan Username Anda yang terdaftar di database `license.csv`.")

    if st.session_state.step == "input_email":
        with st.form("email_form"):
            input_username = st.text_input("Masukkan Username / ID:")
            submit_login = st.form_submit_button("Lanjut")

        if submit_login:
            clean_username = input_username.strip().lower()
            if not clean_username:
                st.error("❌ Username/ID tidak boleh kosong!")
            else:
                is_valid, msg = check_user_license(clean_username)
                if is_valid:
                    st.session_state.user_email = clean_username
                    new_token = str(random.randint(100000, 999999))
                    st.session_state.current_device_token = new_token
                    save_device_token(clean_username, new_token)

                    saved_key = load_device_local_apikey(clean_username)
                    if saved_key:
                        st.session_state.local_api_key = saved_key
                        st.session_state.logged_in = True
                        st.session_state.step = "app"
                        st.success("✅ Berhasil masuk dengan API Key tersimpan di perangkat ini!")
                        st.rerun()
                    else:
                        st.session_state.step = "input_apikey"
                        st.rerun()
                else:
                    st.error(f"❌ {msg}")

    elif st.session_state.step == "input_apikey":
        st.info(f"👤 User: **{st.session_state.user_email}**")
        st.markdown("""
            <div class="api-guide">
                <b>💡 Cara Mendapatkan Groq API Key Gratis:</b><br>
                1. Buka website <a href="https://console.groq.com" target="_blank">console.groq.com</a> dan login/daftar akun.<br>
                2. Masuk ke menu <b>API Keys</b>, klik <b>Create API Key</b>, salin kodenya (diawali <code>gsk_</code>).<br>
                3. Tempel di bawah ini. Key aman tersimpan di perangkat ini!
            </div>
        """, unsafe_allow_html=True)

        with st.form("apikey_form"):
            input_apikey = st.text_input("Groq API Key (gsk_...):", type="password")
            submit_key = st.form_submit_button("Masuk ke Studio")

        if submit_key:
            clean_key = input_apikey.strip()
            if clean_key.startswith("gsk_"):
                st.session_state.local_api_key = clean_key
                save_device_local_apikey(st.session_state.user_email, clean_key)
                st.session_state.logged_in = True
                st.session_state.step = "app"
                st.success("✅ Berhasil masuk!")
                st.rerun()
            else:
                st.error("❌ API Key tidak valid! Harus diawali dengan 'gsk_'")

        if st.button("⬅️ Ganti Username"):
            st.session_state.step = "input_email"
            st.rerun()

# =============================================================================
# 8. APLIKASI UTAMA (FACTORY CONTENT STUDIO)
# =============================================================================
else:
    if not check_device_token(st.session_state.user_email, st.session_state.current_device_token):
        st.error("⚠ Sesi Anda telah berakhir karena akun ini baru saja melakukan login di perangkat lain!")
        if st.button("🔄 Login Ulang di Perangkat Ini"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.local_api_key = ""
            st.session_state.step = "input_email"
            st.rerun()
        st.stop()

    active_activation_key = st.session_state.local_api_key

    # HEADER UTAMA
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.markdown(f"### 🎬 Factory Content Studio | `👤 {st.session_state.user_email}`")
    with col_h2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.local_api_key = ""
            st.session_state.step = "input_email"
            st.rerun()

    st.divider()

    # SIDEBAR STUDIO
    with st.sidebar:
        st.subheader("⚙️ Studio Control Panel")

        # MENU API KEYS
        with st.expander("🔑 API KEYS", expanded=False):
            st.caption("Ganti atau perbarui API Key Groq Anda:")
            st.markdown("""
                <div style="font-size: 0.8rem; color: #bbb; margin-bottom: 8px;">
                    💡 <b>Aktivasi API Key:</b> Buka <a href="https://console.groq.com" target="_blank" style="color: #ff4b4b;">console.groq.com</a> &gt; Menu <b>API Keys</b> &gt; Salin kode (diawali <code>gsk_</code>).
                </div>
            """, unsafe_allow_html=True)
            new_api_input = st.text_input("Groq API Key Baru:", value=active_activation_key, type="password", key="sidebar_apikey_input")
            if st.button("Simpan & Update Key"):
                clean_new_key = new_api_input.strip()
                if clean_new_key.startswith("gsk_"):
                    st.session_state.local_api_key = clean_new_key
                    save_device_local_apikey(st.session_state.user_email, clean_new_key)
                    st.success("✅ API Key berhasil diperbarui & disimpan!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ API Key tidak valid! Harus diawali dengan 'gsk_'")

        st.divider()

        # Input teks dengan dynamic key
        project_title = st.text_input(
            "1. Judul / Ide Utama Video (WAJIB) *", 
            value=st.session_state.input_title_val,
            placeholder="Misal: Linda dan Iwan di Bali", 
            key=f"proj_title_input_{st.session_state.reset_count}"
        )
        custom_notes = st.text_input(
            "2. Detail Cerita / Pesan Khusus AI (Opsional)", 
            value=st.session_state.input_notes_val,
            placeholder="Misal: Pertemuan di Ubud hingga berpisah di bandara", 
            key=f"custom_notes_input_{st.session_state.reset_count}"
        )

        st.divider()
        st.subheader("🛠 Parameter Visual & Engine")

        selected_type = st.selectbox("Jenis Video", VIDEO_TYPES, key=f"sel_type_{st.session_state.reset_count}")
        final_type = st.text_input("Jenis Video Khusus:", placeholder="Micro-Doc", key=f"custom_type_{st.session_state.reset_count}") if selected_type == "✏ Custom Type..." else selected_type

        selected_style = st.selectbox("Gaya Visual", VISUAL_STYLES, key=f"sel_style_{st.session_state.reset_count}")
        final_style = st.text_input("Gaya Visual Khusus:", placeholder="Cyberpunk", key=f"custom_style_{st.session_state.reset_count}") if selected_style == "✏ Custom Visual Style..." else selected_style

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            selected_img_engine = st.selectbox("Image Engine", IMAGE_ENGINES, key=f"sel_img_{st.session_state.reset_count}")
            final_img_engine = st.text_input("Image Engine Khusus:", placeholder="Midjourney", key=f"custom_img_{st.session_state.reset_count}") if selected_img_engine == "✏ Custom Image Engine..." else selected_img_engine
        with col_e2:
            selected_vid_engine = st.selectbox("Video Engine", VIDEO_ENGINES, key=f"sel_vid_{st.session_state.reset_count}")
            final_vid_engine = st.text_input("Video Engine Khusus:", placeholder="Kling", key=f"custom_vid_{st.session_state.reset_count}") if selected_vid_engine == "✏ Custom Video Engine..." else selected_vid_engine

        selected_ratio = st.selectbox("Aspect Ratio", ASPECT_RATIOS, key=f"sel_ratio_{st.session_state.reset_count}")
        final_ratio = st.text_input("Ratio Khusus:", placeholder="9:16", key=f"custom_ratio_{st.session_state.reset_count}") if selected_ratio == "✏ Custom Ratio..." else selected_ratio

        st.markdown("---")
        with st.expander("🎥 Kamera & Pencahayaan", expanded=False):
            selected_cam = st.selectbox("Kamera", CAMERA_SHOT_OPTIONS, key=f"sel_cam_{st.session_state.reset_count}")
            final_cam = st.text_input("Kamera Khusus", placeholder="Close-Up", key=f"custom_cam_{st.session_state.reset_count}") if selected_cam == "✏ Custom Camera Shot..." else selected_cam

            selected_light = st.selectbox("Lighting", LIGHTING_OPTIONS, key=f"sel_light_{st.session_state.reset_count}")
            final_light = st.text_input("Lighting Khusus", placeholder="Moody", key=f"custom_light_{st.session_state.reset_count}") if selected_light == "✏ Custom Lighting..." else selected_light

            selected_color = st.selectbox("Color Grading", COLOR_GRADING_OPTIONS, key=f"sel_color_{st.session_state.reset_count}")
            final_color = st.text_input("Color Khusus", placeholder="Teal & Orange", key=f"custom_color_{st.session_state.reset_count}") if selected_color == "✏ Custom Color Grading..." else selected_color

        st.markdown("---")
        selected_dur = st.selectbox("Durasi per Adegan", DURATION_OPTIONS, key=f"sel_dur_{st.session_state.reset_count}")
        final_duration = selected_dur if selected_dur != "✏ Custom Durasi..." else "5 Detik"

        selected_sc_count = st.selectbox("Jumlah Adegan", SCENE_COUNT_OPTIONS, key=f"sel_sc_cnt_{st.session_state.reset_count}")
        final_scene_count = selected_sc_count if selected_sc_count != "✏ Custom (Maksimal 10)..." else "5 Scene"

        final_voice_mode = st.selectbox("Mode Suara", VOICE_MODE_OPTIONS, key=f"sel_voice_{st.session_state.reset_count}")
        selected_lang = st.selectbox("Bahasa Naskah", LANGUAGE_OPTIONS, key=f"sel_lang_{st.session_state.reset_count}")
        final_language = selected_lang if selected_lang != "✏ Custom Bahasa..." else "Bahasa Indonesia"

        selected_model = st.selectbox("Model AI Engine", GROQ_MODELS, index=0, key=f"sel_model_{st.session_state.reset_count}")

        st.divider()
        st.subheader("👥 Character Management")
        st.caption("Dukung banyak karakter (otomatis disesuaikan cerita).")

        with st.form("add_char_form", clear_on_submit=True):
            c_name = st.text_input("Nama Karakter / Hewan *", placeholder="Misal: Linda / Iwan")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                c_age = st.text_input("Usia", placeholder="20-an thn")
                c_gender = st.selectbox("Gender / Jenis", ["Pria / Male", "Wanita / Female", "Hewan / Animal"])
            with col_c2:
                c_region = st.text_input("Region / Ras", placeholder="Indonesian / French")
                c_height = st.text_input("Tinggi / Ukuran", placeholder="Proporsional")
            
            c_hair = st.text_input("Ciri Rambut/Bulu/Wajah", placeholder="Rambut pendek hitam / Rambut pirang")
            c_traits = st.text_input("Kepribadian", placeholder="Kreatif / Ramah")
            add_char_btn = st.form_submit_button("➕ Tambah Karakter")

        if add_char_btn:
            if c_name.strip():
                new_char_obj = {
                    "name": c_name.strip(), "age": c_age.strip() if c_age else "Bebas", "gender": c_gender,
                    "region": c_region.strip() if c_region else "Bebas", "height": c_height.strip() if c_height else "Proporsional",
                    "hair_face": c_hair.strip() if c_hair else "AI Auto", "traits": c_traits.strip() if c_traits else "AI Auto"
                }
                st.session_state.characters.append(new_char_obj)
                st.success(f"Karakter '{c_name}' ditambahkan!")
                st.rerun()
            else:
                st.error("Nama wajib diisi!")

        if st.session_state.characters:
            st.markdown("##### Karakter Aktif:")
            for idx, char in enumerate(st.session_state.characters):
                with st.expander(f"👤 {char['name']} ({char['region']})"):
                    st.write(f"Ciri/Detail: {char['hair_face']}")
                    if st.button(f"Hapus {char['name']}", key=f"del_char_{idx}"):
                        st.session_state.characters.pop(idx)
                        st.rerun()
        else:
            st.info("Belum ada karakter aktif. Karakter akan otomatis terisi saat BUILD atau bisa ditambah manual di atas.")

        st.divider()
        build_btn = st.button("🚀 BUILD PROJECT BIBLE & SCENES", type="primary")
        
        # Reset Studio Mutlak
        if st.button("🔄 Reset Studio"):
            st.session_state.show_bible = None
            st.session_state.scenes = []
            st.session_state.characters = []
            st.session_state.brief_text = ""
            st.session_state.input_title_val = ""
            st.session_state.input_notes_val = ""
            st.session_state.reset_count += 1
            st.rerun()

        st.divider()
        st.subheader("📂 Private Project History")
        user_history = load_recent_projects(st.session_state.user_email)
        if user_history:
            for proj_name, proj_data in sorted(user_history.items(), key=lambda x: x[1].get("timestamp", ""), reverse=True):
                col_hist1, col_hist2 = st.columns([3, 1])
                with col_hist1:
                    if st.button(f"📁 {proj_name}", key=f"load_hist_{proj_name}"):
                        st.session_state.show_bible = proj_data.get("show_bible")
                        st.session_state.scenes = proj_data.get("scenes")
                        st.session_state.characters = proj_data.get("characters", [])
                        st.session_state.brief_text = proj_data.get("brief_text", "")
                        st.session_state.input_title_val = proj_name
                        st.session_state.input_notes_val = proj_data.get("brief_text", "")
                        st.session_state.reset_count += 1
                        st.success(f"Proyek '{proj_name}' dimuat!")
                        st.rerun()
                with col_hist2:
                    if st.button("🗑", key=f"del_hist_{proj_name}", help=f"Hapus proyek {proj_name}"):
                        delete_project_from_history(st.session_state.user_email, proj_name)
                        st.success(f"Proyek '{proj_name}' dihapus!")
                        st.rerun()
        else:
            st.info("Belum ada riwayat proyek tersimpan.")

    # -----------------------------------------------------------------------------
    # 9. KONTEN UTAMA: WORKSPACE STUDIO KONTEN
    # -----------------------------------------------------------------------------
    if build_btn:
        if not active_activation_key or not active_activation_key.startswith("gsk_"):
            st.error("⚠ Groq API Key belum dimasukkan atau tidak valid!")
        elif not project_title.strip():
            st.error("⚠ Judul / Ide Utama Video wajib diisi!")
        else:
            with st.spinner("⏳ Menganalisis Judul, Ekstraksi Karakter, & Meramu Master Brief..."):
                
                # LANGKAH 1: Ekstraksi Karakter Otomatis
                extract_char_sys = """You are an AI casting director. Analyze the project title and custom story details provided by the user. 
                Extract the characters mentioned in the story. If the user specifies new characters, create character objects for them.
                Return a JSON object with a key "characters" containing an array of character objects, where each object has:
                - name (string)
                - age (string, e.g., 'early 20s' or '20-an thn')
                - gender (string, e.g., 'Pria / Male' or 'Wanita / Female')
                - region (string, e.g., 'Indonesian' or 'French' or 'Swiss')
                - height (string, e.g., '170 cm')
                - hair_face (string, detailed facial and hair description)
                - traits (string, personality traits)
                Return ONLY valid JSON object."""
                
                extract_prompt = f"Title: {project_title}\nCustom Details: {custom_notes}\nExisting Characters: {json.dumps(st.session_state.characters)}"
                
                extracted_res = call_groq_safe(active_activation_key, extract_char_sys, extract_prompt, selected_model, is_json=True)
                if extracted_res:
                    if isinstance(extracted_res, list) and len(extracted_res) > 0:
                        st.session_state.characters = extracted_res
                    elif isinstance(extracted_res, dict) and "characters" in extracted_res:
                        st.session_state.characters = extracted_res["characters"]

                # LANGKAH 2: Build Master Brief, Production Bible & Scenes
                sys_instruct = f"""
                You are an elite AI scriptwriter, director, and visual prompt engineer for multi-scene episodic video series.
                Your task is to prepare a comprehensive production framework based on the user's title: "{project_title}" and custom notes/story details: "{custom_notes}".
                
                MANDATORY & UNBREAKABLE REGIONAL IDENTITY ENFORCEMENT:
                - Strictly enforce ethnic, national, gender, age, and physical metadata defined in the Character Input List for every character.
                
                MANDATORY PROFESSIONAL CHARACTER REFERENCE BOARD FORMAT:
                - 'character_cards': Array of objects for each character, with 'name' and 'character_card_prompt'.
                - STRICT METADATA HEADER RULE: Each character card prompt MUST START with an explicit metadata text banner directive:
                  "A professional cinematic Character Reference Sheet of [Name]. Top banner text clearly displays: 'CHARACTER REFERENCE BOARD: [NAME] | GENDER: [GENDER] | AGE: [AGE] | REGION: [REGION] | ETHNICITY: [FACIAL TRAITS]'."
                - MULTI-PANEL LAYOUT (MANDATORY):
                  1. Left Panel: Full-body view standing neutral pose against a clean studio background.
                  2. Top Center Panel: Close-up front view, neutral expression.
                  3. Top Right Panel: Close-up side profile view.
                  4. Bottom Row Panel: 6 facial expression studies labeled with text: Neutral, Smiling, Laughing, Sad, Angry, Surprised.
                - STRICT NEUTRAL ANATOMY & WARDROBE: Plain clean white sleeveless tank top (singlet), dark denim knee-length cargo shorts, and classic black-and-white sneakers.
                - Style: Ultra-photorealistic 8K, crisp studio lighting, neutral light-grey backdrop, razor sharp focus, accurate anatomy without narrative clutter.
                
                STORY SCENES CREATIVITY:
                - Allow the AI to write rich, episodic, natural narrative scenes without locked wardrobe restrictions across the story.
                
                CRITICAL RULES FOR SYSTEM OUTPUT (JSON format ONLY):
                1. 'brief_text': Provide the exact conversational greeting brief in Indonesian.
                2. 'show_bible': Must contain 'visual_theme', 'mood', 'continuity_rules', and 'character_cards'.
                3. 'scenes': Array of objects, each containing 'scene_num' and 'script_text'.
                Return strictly valid JSON only.
                """

                user_prompt = f"""
                PROJECT SPECS:
                - Title/Idea: {project_title}
                - Custom Notes: {custom_notes if custom_notes else 'None'}
                - Characters: {json.dumps(st.session_state.characters)}
                - Scene Count: {final_scene_count}
                - Style: {final_style}, Engine: {final_img_engine}, Ratio: {final_ratio}
                - Voice Mode: {final_voice_mode}, Language: {final_language}
                """

                result = call_groq_safe(active_activation_key, sys_instruct, user_prompt, selected_model, is_json=True)

                if result:
                    show_bible_data = result.get("show_bible", {})
                    show_bible_data["title"] = project_title
                    show_bible_data["image_engine"] = final_img_engine
                    show_bible_data["video_engine"] = final_vid_engine
                    show_bible_data["ratio"] = final_ratio
                    show_bible_data["duration_setting"] = final_duration
                    show_bible_data["language_setting"] = final_language
                    show_bible_data["voice_mode"] = final_voice_mode

                    brief_generated = result.get("brief_text", f"Hai AI, siap-siap ya saya akan berikan prompt dari image berseri konten judul {project_title}. Tolong dijaga konsistensinya, baik ketika saya berikan referensi karakter card, maupun ketika saya tidak berikan. Siap-siap saya akan berikan promptnya setelah ini.")
                    scenes_input = result.get("scenes", [])
                    
                    formatted_scenes = []
                    for idx, sc in enumerate(scenes_input):
                        formatted_scenes.append({
                            "scene_num": sc.get("scene_num", idx + 1),
                            "script_text": sc.get("script_text", sc.get("narration", "")),
                            "prompt_image": "", "prompt_video": "",
                            "is_unlocked": True if idx == 0 else False
                        })

                    st.session_state.show_bible = show_bible_data
                    st.session_state.scenes = formatted_scenes
                    st.session_state.brief_text = brief_generated

                    save_project_to_history(st.session_state.user_email, project_title, show_bible_data, formatted_scenes, st.session_state.characters, brief_generated)
                    st.success("✅ Karakter, Master Brief, & Naskah Berhasil Dibangun!")
                    st.rerun()

    # DISPLAY WORKSPACE UTAMA
    if st.session_state.show_bible:
        sb = st.session_state.show_bible

        # 1. MASTER BRIEF
        st.subheader("📝 1. Master Brief (Pesan Komunikasi ke Platform AI)")
        st.info("💡 **Langkah Pertama:** Klik ikon salin di pojok kanan atas kotak teks di bawah ini untuk menyalin Master Brief.")
        
        brief_val = st.session_state.get("brief_text", "")
        st.code(brief_val, language="text")

        st.divider()

        # 2. PROJECT PRODUCTION BIBLE (OTAK & ARSIP PRODUKSI)
        st.subheader("📖 2. Project Production Bible (Otak Kontinuitas & Arsip)")
        st.info("💡 **Arsip Sutradara:** Rangkuman visual, mood, dan aturan kontinuitas dunia cerita.")
        
        bible_summary = f"""[PROJECT PRODUCTION BIBLE: {sb.get('title', 'Untitled')}]
• Visual Theme: {sb.get('visual_theme', 'Cinematic Photorealistic 8K, 35mm lens')}
• Mood & Lighting: {sb.get('mood', 'Moody, warm ambient lighting, high contrast')}
• Continuity Rules: {sb.get('continuity_rules', 'Persistent character facial & anatomical identity. Realistic temporal wardrobe logic.')}
• Aspect Ratio: {sb.get('ratio', '16:9')} | Image Engine: {sb.get('image_engine', 'Universal')} | Video Engine: {sb.get('video_engine', 'Universal')}
"""
        st.code(bible_summary.strip(), language="text")

        st.divider()

        # 3. CHARACTER REFERENCE CARDS (PROFESIONAL MULTI-PANEL)
        st.subheader("👤 3. Professional Character Reference Board(s) (Validasi Identitas Regional)")
        st.info("💡 **Langkah Ketiga:** Karakter card profesional (singlet putih & denim cargo shorts) murni untuk mengunci fitur wajah, ekspresi, dan anatomi.")
        
        char_cards_list = sb.get('character_cards', [])
        if not char_cards_list:
            single_prompt = sb.get('character_card_prompt', 'Professional character reference sheet layout.')
            char_cards_list = [{"name": "Karakter Utama", "character_card_prompt": single_prompt}]

        for c_idx, c_card in enumerate(char_cards_list):
            with st.container(border=True):
                c_name_title = c_card.get('name', f'Karakter {c_idx + 1}')
                st.markdown(f"#### 👤 {c_name_title}")
                char_prompt_text = c_card.get('character_card_prompt', '')
                st.code(char_prompt_text, language="text")

        st.divider()

        # 4. PROMPT BERSERI DENGAN LOGIKA WAKTU & NASKAH DIALOG/NARASI
        st.subheader("🎬 4. Prompt Berseri & Naskah per Adegan")
        
        IMG_PROMPT_SYS = """You are an elite Master Cinematic Image Prompt Engineer for narrative film scenes.

CRITICAL NEGATIVE CONSTRAINTS (ABSOLUTE RULES):
1. NO CHARACTER BOARDS / NO MODEL SHEETS: NEVER generate reference sheets, split panels, multi-angle layouts, expression grids, turnarounds, or text typography labels. Output MUST describe a single, unified, authentic cinematic camera shot.
2. IMMERSIVE ENVIRONMENT ONLY: The scene MUST take place entirely within an authentic narrative setting (e.g. real beach, local traditional market, cafe, real living room, taxi). NEVER use a plain photography studio backdrop, white/grey cyclorama, or minimalist studio wall.
3. NEVER USE REFERENCE ATTIRE IN NARRATIVE SCENES: Under NO circumstances should any character wear the white sleeveless tank top / singlet / cargo shorts from the character reference card! Characters must always wear stylish, believable, cinematic narrative garments appropriate to the setting and culture.
4. INTELLIGENT NARRATIVE WARDROBE CONTINUITY & TIME-JUMP LOGIC:
   - READ PREVIOUS SCENE CONTEXT: Check the outfits worn in the immediately preceding scene(s) and analyze the story time passage.
   - SAME DAY / CONTINUOUS ACTION: If this scene takes place on the same day, immediately following, or closely after previous scenes (and characters did not go to change), MAINTAIN the exact same outfit from the previous scene for visual continuity.
   - NEW DAY / TIME TRANSITION / WARDROBE CHANGE: If the script or action indicates a new day (e.g., 'keesokan paginya', 'hari ketiga', 'next morning', 'hari terakhir', 'later that week') OR the narrative mentions changing clothes, you MUST design a FRESH, NEW, stylish, context-appropriate outfit fitting the new day and activity (e.g., sunrise beach casual, morning market wear, yoga sportswear, travel attire).
5. SPATIAL & EYE-LINE ANCHORING: Ground character orientation clearly in 3D space. Characters interacting must face each other directly with natural eye contact.
6. OBJECT PERSISTENCE & PHYSICALITY: Small props (cups, pens, baskets, books) must have static physical reality resting stably on tables or surfaces.

Output ONLY the final descriptive English cinematic prompt text, rich in lighting, mood, camera lens (e.g. 35mm lens, shallow depth of field), and authentic human emotion."""

        VID_PROMPT_SYS = """You are an elite Master AI Video Prompt Engineer for tools like Google Veo, Kling, Flow, and Runway.

CRITICAL FIRST-FRAME CONTINUATION RULES:
1. NO GHOST CLONES / NO DUPLICATE SUBJECTS: When starting from the initial image frame, treat the people already visible as the established primary characters. Do NOT introduce or describe a duplicate version of the main character into the scene.
2. SEAMLESS ACTION CONTINUATION: Describe natural, organic character motion continuing directly from the exact pose established in the initial frame (subtle head turn, lifting the cup, smiling in reaction, natural eye blink).
3. CINEMATIC CAMERA MOTION: Direct smooth cinematic camera movement (e.g. subtle slow push-in, gentle arc shot, shallow depth of field shift).

Output ONLY the final English cinematic video generation prompt."""

        for sc_idx, sc in enumerate(st.session_state.scenes):
            s_num = sc["scene_num"]
            is_unlocked = sc["is_unlocked"]

            with st.container(border=True):
                if not is_unlocked:
                    st.markdown(f"### 🔒 Adegan {s_num} (Terkunci)")
                else:
                    st.markdown(f"### 🟢 Adegan {s_num}")
                    script_txt = sc['script_text'] if sc['script_text'] else "N/A"
                    
                    st.markdown("🎙 **Naskah / Dialog Adegan:**")
                    st.code(script_txt, language="text")

                    # Kumpulkan riwayat adegan sebelumnya agar AI tahu baju & alur waktu sebelumnya
                    prior_context_list = []
                    for p_i in range(max(0, sc_idx - 2), sc_idx):
                        prev_sc = st.session_state.scenes[p_i]
                        prior_context_list.append(f"Scene {prev_sc['scene_num']} Script: {prev_sc['script_text']} | Established Visual Prompt: {prev_sc['prompt_image'][:280]}...")
                    prior_context_str = "\n".join(prior_context_list) if prior_context_list else "This is Scene 1 (Opening scene). Establish stylish opening day outfits suited for the location and story."

                    common_context = f"""
PROJECT TITLE: {sb.get('title', '')}
CURRENT SCENE NUMBER: {s_num}
CURRENT SCRIPT / ACTION: {script_txt}

PREVIOUS SCENE CHRONOLOGY & ESTABLISHED OUTFITS:
{prior_context_str}

CHARACTERS METADATA:
{json.dumps(st.session_state.characters)}

VISUAL & CINEMATIC SPECS:
- Style: {sb.get('visual_theme', 'Cinematic Photorealistic 8K, 35mm lens')}
- Mood & Lighting: {sb.get('mood', 'Moody, warm ambient lighting, high contrast')}
- Aspect Ratio: {sb.get('ratio', '16:9')}

DIRECTIVE FOR WARDROBE:
Analyze CURRENT SCRIPT vs PREVIOUS SCENE. If time jump/new day/clothing change occurred, design fresh stylish attire. If continuous same-day action, strictly match the previous scene's outfit. NEVER use white tank tops or studio attire.
"""

                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("#### 🖼 Prompt Image")
                        if sc["prompt_image"]:
                            st.code(sc["prompt_image"], language="text")
                            if st.button(f"🔄 Regenerate Image {s_num}", key=f"regen_img_{s_num}"):
                                new_p = call_groq_safe(active_activation_key, IMG_PROMPT_SYS, common_context, selected_model, is_json=False)
                                if new_p:
                                    st.session_state.scenes[sc_idx]["prompt_image"] = new_p.strip()
                                    save_project_to_history(st.session_state.user_email, project_title, sb, st.session_state.scenes, st.session_state.characters, st.session_state.brief_text)
                                    st.rerun()
                        else:
                            if st.button(f"✨ Generate Image {s_num}", key=f"gen_img_{s_num}", type="primary"):
                                new_p = call_groq_safe(active_activation_key, IMG_PROMPT_SYS, common_context, selected_model, is_json=False)
                                if new_p:
                                    st.session_state.scenes[sc_idx]["prompt_image"] = new_p.strip()
                                    save_project_to_history(st.session_state.user_email, project_title, sb, st.session_state.scenes, st.session_state.characters, st.session_state.brief_text)
                                    st.rerun()

                    with col_p2:
                        st.markdown("#### 🎥 Prompt Video")
                        if sc["prompt_video"]:
                            st.code(sc["prompt_video"], language="text")
                            if st.button(f"🔄 Regenerate Video {s_num}", key=f"regen_vid_{s_num}"):
                                video_context = f"""
SCENE CONTEXT:
Scene Number: {s_num}
Script/Action: {script_txt}
First Frame Image Reference: {sc.get('prompt_image', 'Scene setting with characters')}
Characters: {json.dumps(st.session_state.characters)}
"""
                                new_vp = call_groq_safe(active_activation_key, VID_PROMPT_SYS, video_context, selected_model, is_json=False)
                                if new_vp:
                                    st.session_state.scenes[sc_idx]["prompt_video"] = new_vp.strip()
                                    if sc_idx + 1 < len(st.session_state.scenes):
                                        st.session_state.scenes[sc_idx + 1]["is_unlocked"] = True
                                    save_project_to_history(st.session_state.user_email, project_title, sb, st.session_state.scenes, st.session_state.characters, st.session_state.brief_text)
                                    st.rerun()
                        else:
                            if st.button(f"✨ Generate Video {s_num}", key=f"gen_vid_{s_num}", type="primary"):
                                video_context = f"""
SCENE CONTEXT:
Scene Number: {s_num}
Script/Action: {script_txt}
First Frame Image Reference: {sc.get('prompt_image', 'Scene setting with characters')}
Characters: {json.dumps(st.session_state.characters)}
"""
                                new_vp = call_groq_safe(active_activation_key, VID_PROMPT_SYS, video_context, selected_model, is_json=False)
                                if new_vp:
                                    st.session_state.scenes[sc_idx]["prompt_video"] = new_vp.strip()
                                    if sc_idx + 1 < len(st.session_state.scenes):
                                        st.session_state.scenes[sc_idx + 1]["is_unlocked"] = True
                                    save_project_to_history(st.session_state.user_email, project_title, sb, st.session_state.scenes, st.session_state.characters, st.session_state.brief_text)
                                    st.rerun()

        # -----------------------------------------------------------------------------
        # 5. MASTER EXPORT WORKSPACE (AUDIO, ALL IMAGES, ALL VIDEOS)
        # -----------------------------------------------------------------------------
        st.divider()
        st.subheader("📦 5. Master Production Export (Batch Copy)")
        
        tab_audio, tab_img, tab_vid = st.tabs(["🎙️ Master Audio Script", "🖼️ Copy All Image Prompts", "🎥 Copy All Video Prompts"])
        
        with tab_audio:
            st.info("💡 **Audio AI Workflow:** Salin seluruh naskah di bawah ini sekali klik untuk di-paste ke platform Voice AI / TTS (ElevenLabs, PlayHT, dll.).")
            all_scripts_list = []
            for sc in st.session_state.scenes:
                s_text = sc.get('script_text', '').strip()
                if s_text:
                    all_scripts_list.append(f"[Scene {sc['scene_num']}]\n{s_text}")
            full_audio_script = "\n\n".join(all_scripts_list) if all_scripts_list else "Belum ada naskah narasi/dialog."
            st.code(full_audio_script, language="text")

        with tab_img:
            st.info("💡 **Batch Image Workflow:** Salin seluruh prompt gambar yang sudah digenerate dengan penanda judul adegan yang rapi.")
            all_imgs_list = []
            for sc in st.session_state.scenes:
                p_img = sc.get('prompt_image', '').strip()
                if p_img:
                    all_imgs_list.append(f"=== [SCENE {sc['scene_num']}: IMAGE PROMPT] ===\n{p_img}")
                else:
                    all_imgs_list.append(f"=== [SCENE {sc['scene_num']}: IMAGE PROMPT] ===\n(Prompt belum di-generate)")
            full_imgs_script = "\n\n".join(all_imgs_list) if all_imgs_list else "Belum ada prompt gambar."
            st.code(full_imgs_script, language="text")

        with tab_vid:
            st.info("💡 **Batch Video Workflow:** Salin seluruh prompt video yang sudah digenerate dengan penanda judul adegan yang rapi.")
            all_vids_list = []
            for sc in st.session_state.scenes:
                p_vid = sc.get('prompt_video', '').strip()
                if p_vid:
                    all_vids_list.append(f"=== [SCENE {sc['scene_num']}: VIDEO PROMPT] ===\n{p_vid}")
                else:
                    all_vids_list.append(f"=== [SCENE {sc['scene_num']}: VIDEO PROMPT] ===\n(Prompt belum di-generate)")
            full_vids_script = "\n\n".join(all_vids_list) if all_vids_list else "Belum ada prompt video."
            st.code(full_vids_script, language="text")

    else:
        st.info("👈 Masukkan **Judul Proyek** & **Detail Cerita** di Sidebar, lalu klik **BUILD PROJECT BIBLE & SCENES** untuk mulai!")

# FOOTER
st.markdown("""
    <div class="footer-brand">
        Copyright &copy; 2026 <b>CONTENT FACTORY</b>. All Rights Reserved.
    </div>
""", unsafe_allow_html=True)