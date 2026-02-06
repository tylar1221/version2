# # # # import streamlit as st
# # # # from supabase import create_client
# # # # import pandas as pd

# # # # # =============================
# # # # # PAGE CONFIG (MUST BE FIRST)
# # # # # =============================
# # # # st.set_page_config(
# # # #     page_title="Vehicle Damage Labeler",
# # # #     page_icon="🚗",
# # # #     layout="wide"
# # # # )

# # # # # =============================
# # # # # SUPABASE CONFIG (SECURE)
# # # # # =============================
# # # # SUPABASE_URL = st.secrets["SUPABASE_URL"]
# # # # SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# # # # BUCKET_NAME = "try"
# # # # PAGE_SIZE = 80

# # # # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # # # # =============================
# # # # # CONSTANTS
# # # # # =============================
# # # # SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
# # # # SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# # # # # =============================
# # # # # SESSION STATE
# # # # # =============================
# # # # defaults = {
# # # #     "selected_folder": None,
# # # #     "page": 0,
# # # #     "images": [],
# # # #     "labels": {},
# # # #     "current_index": 0,
# # # #     "filter_unlabeled": True,
# # # #     "current_name": None,
# # # #     "current_image": None,
# # # # }
# # # # for k, v in defaults.items():
# # # #     if k not in st.session_state:
# # # #         st.session_state[k] = v

# # # # # =============================
# # # # # HELPERS
# # # # # =============================
# # # # @st.cache_data(show_spinner=False)
# # # # def load_labels():
# # # #     res = supabase.table("image_damage_labels").select("*").execute()
# # # #     return {r["image_name"]: r for r in res.data}

# # # # def get_folders():
# # # #     files = supabase.storage.from_(BUCKET_NAME).list("")
# # # #     return sorted([f["name"] for f in files if f.get("id") is None])

# # # # def get_images_page(folder, page=0, unlabeled_only=True):
# # # #     if not folder:
# # # #         return []

# # # #     files = supabase.storage.from_(BUCKET_NAME).list(folder)
# # # #     images = [
# # # #         f for f in files
# # # #         if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
# # # #     ]

# # # #     if unlabeled_only:
# # # #         images = [
# # # #             img for img in images
# # # #             if img["name"] not in st.session_state.labels
# # # #         ]

# # # #     start = page * PAGE_SIZE
# # # #     end = start + PAGE_SIZE
# # # #     return images[start:end]

# # # # def load_current_image():
# # # #     if not st.session_state.images:
# # # #         st.session_state.current_name = None
# # # #         st.session_state.current_image = None
# # # #         return

# # # #     img = st.session_state.images[st.session_state.current_index]
# # # #     folder = st.session_state.selected_folder

# # # #     st.session_state.current_name = img["name"]
# # # #     st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
# # # #         .get_public_url(f"{folder}/{img['name']}")

# # # # def save_label(image_name, description, side, severity):
# # # #     image_path = f"{st.session_state.selected_folder}/{image_name}"

# # # #     payload = {
# # # #         "image_name": image_name,
# # # #         "image_path": image_path,
# # # #         "description": description,
# # # #         "side": side,
# # # #         "severity": severity,
# # # #     }

# # # #     existing = supabase.table("image_damage_labels")\
# # # #         .select("id")\
# # # #         .eq("image_name", image_name)\
# # # #         .execute()

# # # #     if existing.data:
# # # #         supabase.table("image_damage_labels")\
# # # #             .update(payload)\
# # # #             .eq("image_name", image_name)\
# # # #             .execute()
# # # #     else:
# # # #         supabase.table("image_damage_labels")\
# # # #             .insert(payload)\
# # # #             .execute()

# # # #     st.session_state.labels = load_labels()

# # # # # =============================
# # # # # INITIAL LOAD
# # # # # =============================
# # # # st.session_state.labels = load_labels()

# # # # # =============================
# # # # # UI
# # # # # =============================
# # # # st.title("📂 Vehicle Damage Labeler (ICS)")

# # # # tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# # # # # =============================
# # # # # TAB 1: LABELING
# # # # # =============================
# # # # with tab1:
# # # #     folders = get_folders()
# # # #     selected = st.selectbox("📁 Select Batch Folder", folders)

# # # #     if selected != st.session_state.selected_folder:
# # # #         st.session_state.selected_folder = selected
# # # #         st.session_state.page = 0
# # # #         st.session_state.current_index = 0
# # # #         st.session_state.images = get_images_page(
# # # #             selected, 0, st.session_state.filter_unlabeled
# # # #         )
# # # #         load_current_image()

# # # #     st.checkbox(
# # # #         "Show only unlabeled images",
# # # #         key="filter_unlabeled",
# # # #         on_change=lambda: (
# # # #             st.session_state.update({
# # # #                 "page": 0,
# # # #                 "current_index": 0,
# # # #                 "images": get_images_page(
# # # #                     st.session_state.selected_folder,
# # # #                     0,
# # # #                     st.session_state.filter_unlabeled
# # # #                 )
# # # #             }),
# # # #             load_current_image()
# # # #         )
# # # #     )

# # # #     if not st.session_state.images:
# # # #         st.info("No images available in this folder.")
# # # #         st.stop()

# # # #     col1, col2 = st.columns([2, 1])

# # # #     with col1:
# # # #         st.image(st.session_state.current_image)
# # # #         st.caption(st.session_state.current_name)
# # # #         st.caption(
# # # #             f"Page {st.session_state.page + 1} | "
# # # #             f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
# # # #         )

# # # #     with col2:
# # # #         existing = st.session_state.labels.get(
# # # #             st.session_state.current_name, {}
# # # #         )

# # # #         with st.form("label_form"):
# # # #             side = st.radio(
# # # #                 "Vehicle Side",
# # # #                 SIDE_OPTIONS,
# # # #                 index=SIDE_OPTIONS.index(existing.get("side", "front"))
# # # #             )
# # # #             severity = st.selectbox(
# # # #                 "Severity",
# # # #                 SEVERITY_OPTIONS,
# # # #                 index=SEVERITY_OPTIONS.index(existing.get("severity", "minor"))
# # # #             )
# # # #             description = st.text_area(
# # # #                 "Damage Description",
# # # #                 value=existing.get("description", ""),
# # # #                 height=120
# # # #             )

# # # #             c1, c2, c3 = st.columns(3)
# # # #             prev_btn = c1.form_submit_button("⬅️ Previous")
# # # #             save_next_btn = c2.form_submit_button("💾 Save & Next")
# # # #             next_btn = c3.form_submit_button("➡️ Next")

# # # #             if save_next_btn and description.strip():
# # # #                 save_label(
# # # #                     st.session_state.current_name,
# # # #                     description.strip(),
# # # #                     side,
# # # #                     severity
# # # #                 )

# # # #                 if st.session_state.current_index < len(st.session_state.images) - 1:
# # # #                     st.session_state.current_index += 1
# # # #                 else:
# # # #                     st.session_state.page += 1
# # # #                     st.session_state.current_index = 0
# # # #                     st.session_state.images = get_images_page(
# # # #                         st.session_state.selected_folder,
# # # #                         st.session_state.page,
# # # #                         st.session_state.filter_unlabeled
# # # #                     )

# # # #                 load_current_image()
# # # #                 st.rerun()

# # # #             if prev_btn and st.session_state.current_index > 0:
# # # #                 st.session_state.current_index -= 1
# # # #                 load_current_image()
# # # #                 st.rerun()

# # # #             if next_btn and st.session_state.current_index < len(st.session_state.images) - 1:
# # # #                 st.session_state.current_index += 1
# # # #                 load_current_image()
# # # #                 st.rerun()

# # # # # =============================
# # # # # TAB 2: LIVE DB PREVIEW
# # # # # =============================
# # # # with tab2:
# # # #     st.header("📊 Live Supabase Table Preview")

# # # #     data = supabase.table("image_damage_labels").select("*").execute().data
# # # #     if not data:
# # # #         st.info("No labels yet.")
# # # #         st.stop()

# # # #     df = pd.DataFrame(data)

# # # #     c1, c2, c3 = st.columns(3)
# # # #     c1.metric("Total Labels", len(df))
# # # #     c2.metric("Unique Images", df["image_name"].nunique())
# # # #     c3.metric("Status", "Live")

# # # #     st.divider()

# # # #     st.subheader("🗂️ Full Label Table")
# # # #     st.dataframe(df, use_container_width=True)
# import streamlit as st
# from supabase import create_client
# import pandas as pd

# # =============================
# # PAGE CONFIG (MUST BE FIRST)
# # =============================
# st.set_page_config(
#     page_title="Vehicle Damage Labeler",
#     page_icon="🚗",
#     layout="wide"
# )

# # =============================
# # SUPABASE CONFIG (SECURE)
# # =============================
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# BUCKET_NAME = "try"
# PAGE_SIZE = 80

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # =============================
# # CONSTANTS
# # =============================
# SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
# SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# # =============================
# # SESSION STATE
# # =============================
# defaults = {
#     "selected_folder": None,
#     "page": 0,
#     "images": [],
#     "labels": {},
#     "current_index": 0,
#     "filter_unlabeled": True,
#     "current_name": None,
#     "current_image": None,
# }
# for k, v in defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # =============================
# # HELPERS
# # =============================
# def load_labels():
#     res = supabase.table("image_damage_labels").select("*").execute()
#     return {r["image_path"]: r for r in res.data if r["image_path"]}


# def get_folders():
#     files = supabase.storage.from_(BUCKET_NAME).list("")
#     return sorted([f["name"] for f in files if f.get("id") is None])

# def get_images_page(folder, page=0, unlabeled_only=True):
#     if not folder:
#         return []

#     files = supabase.storage.from_(BUCKET_NAME).list(folder)
#     images = [
#         f for f in files
#         if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
#     ]

#     if unlabeled_only:
#     images = [
#         img for img in images
#         if f"{folder}/{img['name']}" not in st.session_state.labels
#     ]


#     start = page * PAGE_SIZE
#     end = start + PAGE_SIZE
#     return images[start:end]

# def load_current_image():
#     if not st.session_state.images:
#         st.session_state.current_name = None
#         st.session_state.current_image = None
#         return

#     img = st.session_state.images[st.session_state.current_index]
#     folder = st.session_state.selected_folder

#     st.session_state.current_name = img["name"]
#     st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
#         .get_public_url(f"{folder}/{img['name']}")

# def save_label(image_name, description, side, severity):
#     image_path = f"{st.session_state.selected_folder}/{image_name}"

#     payload = {
#         "image_name": image_name,
#         "image_path": image_path,
#         "description": description,
#         "side": side,
#         "severity": severity,
#     }

#     existing = supabase.table("image_damage_labels")\
#         .select("id")\
#         .eq("image_name", image_name)\
#         .execute()

#     if existing.data:
#         supabase.table("image_damage_labels")\
#             .update(payload)\
#             .eq("image_name", image_name)\
#             .execute()
#     else:
#         supabase.table("image_damage_labels")\
#             .insert(payload)\
#             .execute()

#     # Refresh labels from database after save
#     st.session_state.labels = load_labels()

# # =============================
# # INITIAL LOAD
# # =============================
# st.session_state.labels = load_labels()

# # =============================
# # UI
# # =============================
# st.title("📂 Vehicle Damage Labeler (ICS)")

# tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# # =============================
# # TAB 1: LABELING
# # =============================
# with tab1:
#     folders = get_folders()
#     selected = st.selectbox("📁 Select Batch Folder", folders)

#     if selected != st.session_state.selected_folder:
#         st.session_state.selected_folder = selected
#         st.session_state.page = 0
#         st.session_state.current_index = 0
#         st.session_state.images = get_images_page(
#             selected, 0, st.session_state.filter_unlabeled
#         )
#         load_current_image()

#     st.checkbox(
#         "Show only unlabeled images",
#         key="filter_unlabeled",
#         on_change=lambda: (
#             st.session_state.update({
#                 "page": 0,
#                 "current_index": 0,
#                 "images": get_images_page(
#                     st.session_state.selected_folder,
#                     0,
#                     st.session_state.filter_unlabeled
#                 )
#             }),
#             load_current_image()
#         )
#     )

#     if not st.session_state.images:
#         st.info("No images available in this folder.")
#         st.stop()

#     col1, col2 = st.columns([2, 1])

#     with col1:
#         st.image(st.session_state.current_image)
#         st.caption(st.session_state.current_name)
#         st.caption(
#             f"Page {st.session_state.page + 1} | "
#             f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
#         )

#     with col2:
#         image_path = f"{st.session_state.selected_folder}/{st.session_state.current_name}"
#         existing = st.session_state.labels.get(image_path, {})


#         with st.form("label_form"):
#             side = st.radio(
#                 "Vehicle Side",
#                 SIDE_OPTIONS,
#                 index=SIDE_OPTIONS.index(existing.get("side", "front"))
#             )
#             severity = st.selectbox(
#                 "Severity",
#                 SEVERITY_OPTIONS,
#                 index=SEVERITY_OPTIONS.index(existing.get("severity", "minor"))
#             )
#             description = st.text_area(
#                 "Damage Description",
#                 value=existing.get("description", ""),
#                 height=120
#             )

#             c1, c2, c3 = st.columns(3)
#             prev_btn = c1.form_submit_button("⬅️ Previous")
#             save_next_btn = c2.form_submit_button("💾 Save & Next")
#             next_btn = c3.form_submit_button("➡️ Next")

#             if save_next_btn and description.strip():
#                 save_label(
#                     st.session_state.current_name,
#                     description.strip(),
#                     side,
#                     severity
#                 )

#                 if st.session_state.current_index < len(st.session_state.images) - 1:
#                     st.session_state.current_index += 1
#                 else:
#                     st.session_state.page += 1
#                     st.session_state.current_index = 0
#                     st.session_state.images = get_images_page(
#                         st.session_state.selected_folder,
#                         st.session_state.page,
#                         st.session_state.filter_unlabeled
#                     )

#                 load_current_image()
#                 st.rerun()

#             if prev_btn and st.session_state.current_index > 0:
#                 st.session_state.current_index -= 1
#                 load_current_image()
#                 st.rerun()

#             if next_btn and st.session_state.current_index < len(st.session_state.images) - 1:
#                 st.session_state.current_index += 1
#                 load_current_image()
#                 st.rerun()

# # =============================
# # TAB 2: LIVE DB PREVIEW
# # =============================
# with tab2:
#     st.header("📊 Live Supabase Table Preview")

#     data = supabase.table("image_damage_labels").select("*").execute().data
#     if not data:
#         st.info("No labels yet.")
#         st.stop()

#     df = pd.DataFrame(data)

#     c1, c2, c3 = st.columns(3)
#     c1.metric("Total Labels", len(df))
#     c2.metric("Unique Images", df["image_name"].nunique())
#     c3.metric("Status", "Live")

#     st.divider()

#     st.subheader("🗂️ Full Label Table")
#     st.dataframe(df, use_container_width=True)

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

@st.cache_resource
def get_supabase_client():
    """Create and cache Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

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
    "last_refresh": 0,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================= 
# HELPERS
# ============================= 
def load_labels():
    """Load all labels from database"""
    try:
        res = supabase.table("image_damage_labels").select("*").execute()
        return {r["image_path"]: r for r in res.data if r.get("image_path")}
    except Exception as e:
        st.error(f"Error loading labels: {str(e)}")
        return {}

def get_folders():
    """Get list of folders from storage bucket"""
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except Exception as e:
        st.error(f"Error loading folders: {str(e)}")
        return []

def get_images_page(folder, page=0, unlabeled_only=True):
    """Get paginated images from folder with fresh label check"""
    if not folder:
        return []
    
    try:
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        images = [
            f for f in files 
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        if unlabeled_only:
            # Always reload labels fresh when filtering
            fresh_labels = load_labels()
            images = [
                img for img in images 
                if f"{folder}/{img['name']}" not in fresh_labels
            ]
        
        # Sort by name for consistency
        images = sorted(images, key=lambda x: x["name"])
        
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return images[start:end]
    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        return []

def load_current_image():
    """Load current image URL and name"""
    if not st.session_state.images:
        st.session_state.current_name = None
        st.session_state.current_image = None
        return
    
    # Bounds check
    if st.session_state.current_index >= len(st.session_state.images):
        st.session_state.current_index = 0
    
    if st.session_state.current_index < 0:
        st.session_state.current_index = 0
    
    try:
        img = st.session_state.images[st.session_state.current_index]
        folder = st.session_state.selected_folder
        st.session_state.current_name = img["name"]
        st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
            .get_public_url(f"{folder}/{img['name']}")
    except Exception as e:
        st.error(f"Error loading current image: {str(e)}")
        st.session_state.current_name = None
        st.session_state.current_image = None

def save_label(image_name, description, side, severity):
    """Save or update label in database"""
    try:
        image_path = f"{st.session_state.selected_folder}/{image_name}"
        payload = {
            "image_name": image_name,
            "image_path": image_path,
            "description": description,
            "side": side,
            "severity": severity,
        }
        
        # Check if exists
        existing = supabase.table("image_damage_labels")\
            .select("id")\
            .eq("image_path", image_path)\
            .execute()
        
        if existing.data:
            # Update existing
            supabase.table("image_damage_labels")\
                .update(payload)\
                .eq("image_path", image_path)\
                .execute()
        else:
            # Insert new
            supabase.table("image_damage_labels")\
                .insert(payload)\
                .execute()
        
        # Refresh labels from database
        st.session_state.labels = load_labels()
        return True
    except Exception as e:
        st.error(f"Error saving label: {str(e)}")
        return False

def refresh_data():
    """Manually refresh all data"""
    st.session_state.labels = load_labels()
    st.session_state.images = get_images_page(
        st.session_state.selected_folder,
        st.session_state.page,
        st.session_state.filter_unlabeled
    )
    load_current_image()
    st.session_state.last_refresh = pd.Timestamp.now().timestamp()

def handle_filter_change():
    """Handle filter checkbox change"""
    st.session_state.labels = load_labels()
    st.session_state.page = 0
    st.session_state.current_index = 0
    st.session_state.images = get_images_page(
        st.session_state.selected_folder,
        0,
        st.session_state.filter_unlabeled
    )
    load_current_image()

# ============================= 
# INITIAL LOAD
# ============================= 
if not st.session_state.labels:
    st.session_state.labels = load_labels()

# ============================= 
# UI
# ============================= 
st.title("📂 Vehicle Damage Labeler (ICS)")

# Add refresh button in header
col_title, col_refresh = st.columns([4, 1])
with col_refresh:
    if st.button("🔄 Refresh Data", use_container_width=True):
        refresh_data()
        st.success("Data refreshed!")
        st.rerun()

tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# ============================= 
# TAB 1: LABELING
# ============================= 
with tab1:
    folders = get_folders()
    
    if not folders:
        st.warning("No folders found in storage bucket.")
        st.stop()
    
    selected = st.selectbox("📁 Select Batch Folder", folders)
    
    # Handle folder change
    if selected != st.session_state.selected_folder:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
        st.session_state.labels = load_labels()
        st.session_state.images = get_images_page(
            selected, 
            0, 
            st.session_state.filter_unlabeled
        )
        load_current_image()
    
    # Filter checkbox
    st.checkbox(
        "Show only unlabeled images",
        key="filter_unlabeled",
        on_change=handle_filter_change
    )
    
    # Check if images available
    if not st.session_state.images:
        if st.session_state.filter_unlabeled:
            st.success("🎉 All images in this folder are labeled!")
            st.info("Uncheck 'Show only unlabeled images' to view all images.")
        else:
            st.info("No images available in this folder.")
        st.stop()
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_image:
            st.image(st.session_state.current_image, use_container_width=True)
            st.caption(f"📷 {st.session_state.current_name}")
            st.caption(
                f"Page {st.session_state.page + 1} | "
                f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
            )
        else:
            st.warning("No image to display")
    
    with col2:
        if not st.session_state.current_name:
            st.warning("No image selected")
            st.stop()
        
        image_path = f"{st.session_state.selected_folder}/{st.session_state.current_name}"
        existing = st.session_state.labels.get(image_path, {})
        
        with st.form("label_form"):
            st.subheader("Label Image")
            
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
                height=120,
                placeholder="Describe the damage in detail..."
            )
            
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            prev_btn = c1.form_submit_button("⬅️ Previous", use_container_width=True)
            save_next_btn = c2.form_submit_button("💾 Save & Next", use_container_width=True, type="primary")
            next_btn = c3.form_submit_button("➡️ Next", use_container_width=True)
            
            # Handle buttons
            if save_next_btn:
                if not description.strip():
                    st.error("Please enter a description before saving.")
                else:
                    if save_label(
                        st.session_state.current_name,
                        description.strip(),
                        side,
                        severity
                    ):
                        st.success("✅ Label saved!")
                        
                        # Move to next image
                        if st.session_state.current_index < len(st.session_state.images) - 1:
                            st.session_state.current_index += 1
                        else:
                            # Move to next page
                            st.session_state.page += 1
                            st.session_state.current_index = 0
                            st.session_state.images = get_images_page(
                                st.session_state.selected_folder,
                                st.session_state.page,
                                st.session_state.filter_unlabeled
                            )
                        
                        load_current_image()
                        st.rerun()
            
            if prev_btn:
                if st.session_state.current_index > 0:
                    st.session_state.current_index -= 1
                    load_current_image()
                    st.rerun()
                elif st.session_state.page > 0:
                    # Go to previous page
                    st.session_state.page -= 1
                    st.session_state.images = get_images_page(
                        st.session_state.selected_folder,
                        st.session_state.page,
                        st.session_state.filter_unlabeled
                    )
                    st.session_state.current_index = len(st.session_state.images) - 1
                    load_current_image()
                    st.rerun()
            
            if next_btn:
                if st.session_state.current_index < len(st.session_state.images) - 1:
                    st.session_state.current_index += 1
                    load_current_image()
                    st.rerun()
                else:
                    # Try to move to next page
                    st.session_state.page += 1
                    new_images = get_images_page(
                        st.session_state.selected_folder,
                        st.session_state.page,
                        st.session_state.filter_unlabeled
                    )
                    if new_images:
                        st.session_state.images = new_images
                        st.session_state.current_index = 0
                        load_current_image()
                        st.rerun()
                    else:
                        st.session_state.page -= 1
                        st.info("No more images available.")

# ============================= 
# TAB 2: LIVE DB PREVIEW
# ============================= 
with tab2:
    st.header("📊 Live Supabase Table Preview")
    
    col_refresh1, col_refresh2 = st.columns([3, 1])
    with col_refresh2:
        if st.button("🔄 Refresh Table", key="refresh_table"):
            st.rerun()
    
    try:
        data = supabase.table("image_damage_labels").select("*").execute().data
        
        if not data:
            st.info("No labels yet. Start labeling in the Labeling tab!")
            st.stop()
        
        df = pd.DataFrame(data)
        
        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Labels", len(df))
        c2.metric("Unique Images", df["image_name"].nunique())
        
        if "severity" in df.columns:
            severity_counts = df["severity"].value_counts()
            c3.metric("Severe Cases", severity_counts.get("severe", 0))
        
        if "side" in df.columns:
            side_counts = df["side"].value_counts()
            most_common_side = side_counts.idxmax() if not side_counts.empty else "N/A"
            c4.metric("Most Common Side", most_common_side)
        
        st.divider()
        
        # Filters
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            if "severity" in df.columns:
                severity_filter = st.multiselect(
                    "Filter by Severity",
                    options=df["severity"].unique(),
                    default=df["severity"].unique()
                )
                df = df[df["severity"].isin(severity_filter)]
        
        with col_filter2:
            if "side" in df.columns:
                side_filter = st.multiselect(
                    "Filter by Side",
                    options=df["side"].unique(),
                    default=df["side"].unique()
                )
                df = df[df["side"].isin(side_filter)]
        
        st.divider()
        
        st.subheader("🗂️ Full Label Table")
        st.dataframe(
            df,
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"vehicle_damage_labels_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
        
    except Exception as e:
        st.error(f"Error loading database: {str(e)}")
        
