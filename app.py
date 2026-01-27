import streamlit as st
from supabase import create_client
import pandas as pd

# =============================
# PAGE CONFIG (MUST BE FIRST)
# =============================
st.set_page_config(
    page_title="Vehicle Damage Labeler",
    page_icon="🚗",
    layout="wide"
)

# =============================
# SUPABASE CONFIG (SECURE)
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "try"
PAGE_SIZE = 80

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================
# CONSTANTS
# =============================
SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# =============================
# SESSION STATE
# =============================
defaults = {
    "selected_folder": None,
    "page": 0,
    "images": [],
    "labels": {},
    "current_index": 0,
    "filter_unlabeled": True,
    "current_name": None,
    "current_image": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# HELPERS
# =============================
@st.cache_data(show_spinner=False)
def load_labels():
    res = supabase.table("image_damage_labels").select("*").execute()
    return {r["image_name"]: r for r in res.data}

def get_folders():
    files = supabase.storage.from_(BUCKET_NAME).list("")
    return sorted([f["name"] for f in files if f.get("id") is None])

def get_images_page(folder, page=0, unlabeled_only=True):
    if not folder:
        return []

    files = supabase.storage.from_(BUCKET_NAME).list(folder)
    images = [
        f for f in files
        if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if unlabeled_only:
        images = [
            img for img in images
            if img["name"] not in st.session_state.labels
        ]

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return images[start:end]

def load_current_image():
    if not st.session_state.images:
        st.session_state.current_name = None
        st.session_state.current_image = None
        return

    img = st.session_state.images[st.session_state.current_index]
    folder = st.session_state.selected_folder

    st.session_state.current_name = img["name"]
    st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
        .get_public_url(f"{folder}/{img['name']}")

def save_label(image_name, description, side, severity):
    image_path = f"{st.session_state.selected_folder}/{image_name}"

    payload = {
        "image_name": image_name,
        "image_path": image_path,
        "description": description,
        "side": side,
        "severity": severity,
    }

    existing = supabase.table("image_damage_labels")\
        .select("id")\
        .eq("image_name", image_name)\
        .execute()

    if existing.data:
        supabase.table("image_damage_labels")\
            .update(payload)\
            .eq("image_name", image_name)\
            .execute()
    else:
        supabase.table("image_damage_labels")\
            .insert(payload)\
            .execute()

    st.session_state.labels = load_labels()

# =============================
# INITIAL LOAD
# =============================
st.session_state.labels = load_labels()

# =============================
# UI
# =============================
st.title("📂 Vehicle Damage Labeler (ICS)")

tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# =============================
# TAB 1: LABELING
# =============================
with tab1:
    folders = get_folders()
    selected = st.selectbox("📁 Select Batch Folder", folders)

    if selected != st.session_state.selected_folder:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
        st.session_state.images = get_images_page(
            selected, 0, st.session_state.filter_unlabeled
        )
        load_current_image()

    st.checkbox(
        "Show only unlabeled images",
        key="filter_unlabeled",
        on_change=lambda: (
            st.session_state.update({
                "page": 0,
                "current_index": 0,
                "images": get_images_page(
                    st.session_state.selected_folder,
                    0,
                    st.session_state.filter_unlabeled
                )
            }),
            load_current_image()
        )
    )

    if not st.session_state.images:
        st.info("No images available in this folder.")
        st.stop()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(st.session_state.current_image)
        st.caption(st.session_state.current_name)
        st.caption(
            f"Page {st.session_state.page + 1} | "
            f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
        )

    with col2:
        existing = st.session_state.labels.get(
            st.session_state.current_name, {}
        )

        with st.form("label_form"):
            side = st.radio(
                "Vehicle Side",
                SIDE_OPTIONS,
                index=SIDE_OPTIONS.index(existing.get("side", "front"))
            )
            severity = st.selectbox(
                "Severity",
                SEVERITY_OPTIONS,
                index=SEVERITY_OPTIONS.index(existing.get("severity", "minor"))
            )
            description = st.text_area(
                "Damage Description",
                value=existing.get("description", ""),
                height=120
            )

            c1, c2, c3 = st.columns(3)
            prev_btn = c1.form_submit_button("⬅️ Previous")
            save_next_btn = c2.form_submit_button("💾 Save & Next")
            next_btn = c3.form_submit_button("➡️ Next")

            if save_next_btn and description.strip():
                save_label(
                    st.session_state.current_name,
                    description.strip(),
                    side,
                    severity
                )

                if st.session_state.current_index < len(st.session_state.images) - 1:
                    st.session_state.current_index += 1
                else:
                    st.session_state.page += 1
                    st.session_state.current_index = 0
                    st.session_state.images = get_images_page(
                        st.session_state.selected_folder,
                        st.session_state.page,
                        st.session_state.filter_unlabeled
                    )

                load_current_image()
                st.rerun()

            if prev_btn and st.session_state.current_index > 0:
                st.session_state.current_index -= 1
                load_current_image()
                st.rerun()

            if next_btn and st.session_state.current_index < len(st.session_state.images) - 1:
                st.session_state.current_index += 1
                load_current_image()
                st.rerun()

# =============================
# TAB 2: LIVE DB PREVIEW
# =============================
with tab2:
    st.header("📊 Live Supabase Table Preview")

    data = supabase.table("image_damage_labels").select("*").execute().data
    if not data:
        st.info("No labels yet.")
        st.stop()

    df = pd.DataFrame(data)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Labels", len(df))
    c2.metric("Unique Images", df["image_name"].nunique())
    c3.metric("Status", "Live")

    st.divider()

    st.subheader("🗂️ Full Label Table")
    st.dataframe(df, use_container_width=True)
