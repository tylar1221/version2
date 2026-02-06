# # # # # import streamlit as st
# # # # # from supabase import create_client
# # # # # import pandas as pd

# # # # # # =============================
# # # # # # PAGE CONFIG (MUST BE FIRST)
# # # # # # =============================
# # # # # st.set_page_config(
# # # # #     page_title="Vehicle Damage Labeler",
# # # # #     page_icon="🚗",
# # # # #     layout="wide"
# # # # # )

# # # # # # =============================
# # # # # # SUPABASE CONFIG (SECURE)
# # # # # # =============================
# # # # # SUPABASE_URL = st.secrets["SUPABASE_URL"]
# # # # # SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# # # # # BUCKET_NAME = "try"
# # # # # PAGE_SIZE = 80

# # # # # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # # # # # =============================
# # # # # # CONSTANTS
# # # # # # =============================
# # # # # SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
# # # # # SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# # # # # # =============================
# # # # # # SESSION STATE
# # # # # # =============================
# # # # # defaults = {
# # # # #     "selected_folder": None,
# # # # #     "page": 0,
# # # # #     "images": [],
# # # # #     "labels": {},
# # # # #     "current_index": 0,
# # # # #     "filter_unlabeled": True,
# # # # #     "current_name": None,
# # # # #     "current_image": None,
# # # # # }
# # # # # for k, v in defaults.items():
# # # # #     if k not in st.session_state:
# # # # #         st.session_state[k] = v

# # # # # # =============================
# # # # # # HELPERS
# # # # # # =============================
# # # # # @st.cache_data(show_spinner=False)
# # # # # def load_labels():
# # # # #     res = supabase.table("image_damage_labels").select("*").execute()
# # # # #     return {r["image_name"]: r for r in res.data}

# # # # # def get_folders():
# # # # #     files = supabase.storage.from_(BUCKET_NAME).list("")
# # # # #     return sorted([f["name"] for f in files if f.get("id") is None])

# # # # # def get_images_page(folder, page=0, unlabeled_only=True):
# # # # #     if not folder:
# # # # #         return []

# # # # #     files = supabase.storage.from_(BUCKET_NAME).list(folder)
# # # # #     images = [
# # # # #         f for f in files
# # # # #         if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
# # # # #     ]

# # # # #     if unlabeled_only:
# # # # #         images = [
# # # # #             img for img in images
# # # # #             if img["name"] not in st.session_state.labels
# # # # #         ]

# # # # #     start = page * PAGE_SIZE
# # # # #     end = start + PAGE_SIZE
# # # # #     return images[start:end]

# # # # # def load_current_image():
# # # # #     if not st.session_state.images:
# # # # #         st.session_state.current_name = None
# # # # #         st.session_state.current_image = None
# # # # #         return

# # # # #     img = st.session_state.images[st.session_state.current_index]
# # # # #     folder = st.session_state.selected_folder

# # # # #     st.session_state.current_name = img["name"]
# # # # #     st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
# # # # #         .get_public_url(f"{folder}/{img['name']}")

# # # # # def save_label(image_name, description, side, severity):
# # # # #     image_path = f"{st.session_state.selected_folder}/{image_name}"

# # # # #     payload = {
# # # # #         "image_name": image_name,
# # # # #         "image_path": image_path,
# # # # #         "description": description,
# # # # #         "side": side,
# # # # #         "severity": severity,
# # # # #     }

# # # # #     existing = supabase.table("image_damage_labels")\
# # # # #         .select("id")\
# # # # #         .eq("image_name", image_name)\
# # # # #         .execute()

# # # # #     if existing.data:
# # # # #         supabase.table("image_damage_labels")\
# # # # #             .update(payload)\
# # # # #             .eq("image_name", image_name)\
# # # # #             .execute()
# # # # #     else:
# # # # #         supabase.table("image_damage_labels")\
# # # # #             .insert(payload)\
# # # # #             .execute()

# # # # #     st.session_state.labels = load_labels()

# # # # # # =============================
# # # # # # INITIAL LOAD
# # # # # # =============================
# # # # # st.session_state.labels = load_labels()

# # # # # # =============================
# # # # # # UI
# # # # # # =============================
# # # # # st.title("📂 Vehicle Damage Labeler (ICS)")

# # # # # tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# # # # # # =============================
# # # # # # TAB 1: LABELING
# # # # # # =============================
# # # # # with tab1:
# # # # #     folders = get_folders()
# # # # #     selected = st.selectbox("📁 Select Batch Folder", folders)

# # # # #     if selected != st.session_state.selected_folder:
# # # # #         st.session_state.selected_folder = selected
# # # # #         st.session_state.page = 0
# # # # #         st.session_state.current_index = 0
# # # # #         st.session_state.images = get_images_page(
# # # # #             selected, 0, st.session_state.filter_unlabeled
# # # # #         )
# # # # #         load_current_image()

# # # # #     st.checkbox(
# # # # #         "Show only unlabeled images",
# # # # #         key="filter_unlabeled",
# # # # #         on_change=lambda: (
# # # # #             st.session_state.update({
# # # # #                 "page": 0,
# # # # #                 "current_index": 0,
# # # # #                 "images": get_images_page(
# # # # #                     st.session_state.selected_folder,
# # # # #                     0,
# # # # #                     st.session_state.filter_unlabeled
# # # # #                 )
# # # # #             }),
# # # # #             load_current_image()
# # # # #         )
# # # # #     )

# # # # #     if not st.session_state.images:
# # # # #         st.info("No images available in this folder.")
# # # # #         st.stop()

# # # # #     col1, col2 = st.columns([2, 1])

# # # # #     with col1:
# # # # #         st.image(st.session_state.current_image)
# # # # #         st.caption(st.session_state.current_name)
# # # # #         st.caption(
# # # # #             f"Page {st.session_state.page + 1} | "
# # # # #             f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
# # # # #         )

# # # # #     with col2:
# # # # #         existing = st.session_state.labels.get(
# # # # #             st.session_state.current_name, {}
# # # # #         )

# # # # #         with st.form("label_form"):
# # # # #             side = st.radio(
# # # # #                 "Vehicle Side",
# # # # #                 SIDE_OPTIONS,
# # # # #                 index=SIDE_OPTIONS.index(existing.get("side", "front"))
# # # # #             )
# # # # #             severity = st.selectbox(
# # # # #                 "Severity",
# # # # #                 SEVERITY_OPTIONS,
# # # # #                 index=SEVERITY_OPTIONS.index(existing.get("severity", "minor"))
# # # # #             )
# # # # #             description = st.text_area(
# # # # #                 "Damage Description",
# # # # #                 value=existing.get("description", ""),
# # # # #                 height=120
# # # # #             )

# # # # #             c1, c2, c3 = st.columns(3)
# # # # #             prev_btn = c1.form_submit_button("⬅️ Previous")
# # # # #             save_next_btn = c2.form_submit_button("💾 Save & Next")
# # # # #             next_btn = c3.form_submit_button("➡️ Next")

# # # # #             if save_next_btn and description.strip():
# # # # #                 save_label(
# # # # #                     st.session_state.current_name,
# # # # #                     description.strip(),
# # # # #                     side,
# # # # #                     severity
# # # # #                 )

# # # # #                 if st.session_state.current_index < len(st.session_state.images) - 1:
# # # # #                     st.session_state.current_index += 1
# # # # #                 else:
# # # # #                     st.session_state.page += 1
# # # # #                     st.session_state.current_index = 0
# # # # #                     st.session_state.images = get_images_page(
# # # # #                         st.session_state.selected_folder,
# # # # #                         st.session_state.page,
# # # # #                         st.session_state.filter_unlabeled
# # # # #                     )

# # # # #                 load_current_image()
# # # # #                 st.rerun()

# # # # #             if prev_btn and st.session_state.current_index > 0:
# # # # #                 st.session_state.current_index -= 1
# # # # #                 load_current_image()
# # # # #                 st.rerun()

# # # # #             if next_btn and st.session_state.current_index < len(st.session_state.images) - 1:
# # # # #                 st.session_state.current_index += 1
# # # # #                 load_current_image()
# # # # #                 st.rerun()

# # # # # # =============================
# # # # # # TAB 2: LIVE DB PREVIEW
# # # # # # =============================
# # # # # with tab2:
# # # # #     st.header("📊 Live Supabase Table Preview")

# # # # #     data = supabase.table("image_damage_labels").select("*").execute().data
# # # # #     if not data:
# # # # #         st.info("No labels yet.")
# # # # #         st.stop()

# # # # #     df = pd.DataFrame(data)

# # # # #     c1, c2, c3 = st.columns(3)
# # # # #     c1.metric("Total Labels", len(df))
# # # # #     c2.metric("Unique Images", df["image_name"].nunique())
# # # # #     c3.metric("Status", "Live")

# # # # #     st.divider()

# # # # #     st.subheader("🗂️ Full Label Table")
# # # # #     st.dataframe(df, use_container_width=True)
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
#     """Load labels from Supabase - no caching to ensure fresh data"""
#     res = supabase.table("image_damage_labels").select("*").execute()
#     return {r["image_name"]: r for r in res.data}

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
#         images = [
#             img for img in images
#             if img["name"] not in st.session_state.labels
#         ]

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
#         existing = st.session_state.labels.get(
#             st.session_state.current_name, {}
#         )

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
#     st.dataframe(df, use_container_width=True) #analyse this code there is somthing wrong for showing unlabled image becasue even the image is labled it is shwowin no unlabled 
# =============================
# FIXED VERSION OF THE CODE
# =============================
import streamlit as st
from supabase import create_client
import pandas as pd

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Vehicle Damage Labeler",
    page_icon="🚗",
    layout="wide"
)

# =============================
# SUPABASE CONFIG
# =============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET_NAME = "try"
PAGE_SIZE = 50  # Reduced for better performance

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================
# CONSTANTS
# =============================
SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# =============================
# SESSION STATE
# =============================
if 'selected_folder' not in st.session_state:
    st.session_state.selected_folder = None
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'labels_cache' not in st.session_state:
    st.session_state.labels_cache = set()  # Use set for faster lookups
if 'images_cache' not in st.session_state:
    st.session_state.images_cache = {}

# =============================
# OPTIMIZED FUNCTIONS
# =============================
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_all_labels():
    """Load all labels once and cache"""
    try:
        res = supabase.table("image_damage_labels").select("image_name").execute()
        return {item["image_name"] for item in res.data}
    except:
        return set()

def get_labels():
    """Get labels from cache or load"""
    if not st.session_state.labels_cache:
        st.session_state.labels_cache = load_all_labels()
    return st.session_state.labels_cache

def refresh_labels():
    """Force refresh labels"""
    st.session_state.labels_cache = load_all_labels()
    st.cache_data.clear()
    return st.session_state.labels_cache

def get_folders():
    """Get available folders"""
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except:
        return []

@st.cache_data(ttl=10)  # Cache images for 10 seconds
def get_storage_images(folder):
    """Get all images from a folder"""
    try:
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        return [
            f for f in files 
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
    except:
        return []

def get_images(folder, page=0, unlabeled_only=True):
    """Get paginated images with optional filtering"""
    if not folder:
        return []
    
    # Get all images from storage (cached)
    all_images = get_storage_images(folder)
    
    # Get labels
    labels = get_labels()
    
    # Filter if needed
    if unlabeled_only:
        images = [img for img in all_images if img["name"] not in labels]
    else:
        images = all_images
    
    # Pagination
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return images[start:end]

def save_label(image_name, description, side, severity):
    """Save label efficiently"""
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
        
        # Update cache immediately
        st.session_state.labels_cache.add(image_name)
        
        # Clear relevant caches
        st.cache_data.clear()
        
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# =============================
# UI - SIMPLIFIED
# =============================
st.title("🚗 Vehicle Damage Labeler")

# Top controls
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 Refresh", type="secondary"):
        refresh_labels()
        st.rerun()

with col2:
    st.metric("Labeled Images", len(get_labels()))

with col3:
    if st.session_state.selected_folder:
        st.metric("Current Folder", st.session_state.selected_folder)

# Main tabs
tab1, tab2 = st.tabs(["🏷️ Label Images", "📊 Database"])

# =============================
# TAB 1: LABELING
# =============================
with tab1:
    # Folder selection
    folders = get_folders()
    if not folders:
        st.info("No folders found")
        st.stop()
    
    selected = st.selectbox("Select Folder", folders, key="folder_select")
    
    # Update on folder change
    if selected != st.session_state.selected_folder:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
    
    # View mode toggle
    show_unlabeled = st.toggle("Show only unlabeled", value=True, key="show_unlabeled")
    
    # Get images
    images = get_images(
        st.session_state.selected_folder,
        st.session_state.page,
        show_unlabeled
    )
    
    if not images:
        st.success("✅ No unlabeled images" if show_unlabeled else "No images found")
        st.stop()
    
    # Navigation
    nav_cols = st.columns([1, 2, 2, 1])
    with nav_cols[0]:
        if st.button("⏮️", disabled=st.session_state.current_index == 0):
            st.session_state.current_index = 0
            st.rerun()
    with nav_cols[1]:
        if st.button("⬅️ Previous", disabled=st.session_state.current_index == 0):
            st.session_state.current_index -= 1
            st.rerun()
    with nav_cols[2]:
        if st.button("Next ➡️", disabled=st.session_state.current_index >= len(images)-1):
            st.session_state.current_index += 1
            st.rerun()
    with nav_cols[3]:
        if st.button("⏭️", disabled=st.session_state.current_index >= len(images)-1):
            st.session_state.current_index = len(images) - 1
            st.rerun()
    
    # Current image
    current_img = images[st.session_state.current_index]
    current_name = current_img["name"]
    
    # Display
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        try:
            image_url = supabase.storage.from_(BUCKET_NAME)\
                .get_public_url(f"{st.session_state.selected_folder}/{current_name}")
            st.image(image_url, use_container_width=True)
        except:
            st.error("Cannot load image")
        
        st.caption(f"{current_name} • Image {st.session_state.current_index + 1} of {len(images)}")
        
        # Status indicator
        if current_name in get_labels():
            st.success("✅ Already labeled")
    
    with col_right:
        # Get existing data
        existing = {}
        try:
            res = supabase.table("image_damage_labels")\
                .select("*")\
                .eq("image_name", current_name)\
                .execute()
            if res.data:
                existing = res.data[0]
        except:
            pass
        
        # Labeling form
        with st.form("label_form"):
            side = st.radio("Side", SIDE_OPTIONS, 
                          index=SIDE_OPTIONS.index(existing.get("side", "front")),
                          horizontal=True)
            
            severity = st.selectbox("Severity", SEVERITY_OPTIONS,
                                  index=SEVERITY_OPTIONS.index(existing.get("severity", "minor")))
            
            description = st.text_area("Description",
                                     value=existing.get("description", ""),
                                     height=100,
                                     placeholder="Describe the damage...")
            
            # Form buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                save_btn = st.form_submit_button("💾 Save", use_container_width=True)
            with btn_col2:
                save_next_btn = st.form_submit_button("💾 Save & Next", use_container_width=True)
            
            if save_btn or save_next_btn:
                if not description.strip():
                    st.error("Enter description")
                elif save_label(current_name, description.strip(), side, severity):
                    if save_next_btn and st.session_state.current_index < len(images) - 1:
                        st.session_state.current_index += 1
                    st.rerun()

# =============================
# TAB 2: DATABASE
# =============================
with tab2:
    st.header("Database")
    
    # Quick stats
    labels = get_labels()
    st.write(f"**Total labeled images:** {len(labels)}")
    
    # Show recent labels
    try:
        recent = supabase.table("image_damage_labels")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        
        if recent.data:
            df = pd.DataFrame(recent.data)
            
            # Show by folder
            if 'image_path' in df.columns:
                df['folder'] = df['image_path'].str.split('/').str[0]
                folder_counts = df['folder'].value_counts()
                
                cols = st.columns(3)
                for i, (folder, count) in enumerate(folder_counts.head(3).items()):
                    with cols[i]:
                        st.metric(folder, count)
            
            st.dataframe(df[['image_name', 'side', 'severity', 'description']], 
                        use_container_width=True,
                        hide_index=True)
        else:
            st.info("No labels yet")
    except:
        st.error("Cannot load database")

# =============================
# BOTTOM STATUS
# =============================
st.divider()
st.caption(f"Viewing {len(images)} images • Page {st.session_state.page + 1}")
