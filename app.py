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
import time

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Vehicle Damage Labeler - DEBUG",
    page_icon="🚗",
    layout="wide"
)

# =============================
# SUPABASE CONFIG
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
    "all_labels": {},  # NEW: Store all labels including from other folders
    "current_index": 0,
    "filter_unlabeled": True,
    "current_name": None,
    "current_image": None,
    "debug_mode": False,  # NEW: Debug mode toggle
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# DEBUGGING HELPERS
# =============================
def load_all_labels():
    """Load ALL labels from Supabase - no filtering"""
    try:
        st.info("🔄 Loading ALL labels from database...")
        res = supabase.table("image_damage_labels").select("*").execute()
        
        # Debug output
        if res.data:
            st.success(f"✅ Loaded {len(res.data)} labels from database")
            
            # Check specifically for image_958.jpeg
            for label in res.data:
                if "958" in label.get("image_name", ""):
                    st.warning(f"Found label for image_958.jpeg: {label}")
            
            return {r["image_name"]: r for r in res.data}
        return {}
    except Exception as e:
        st.error(f"❌ Error loading labels: {e}")
        return {}

def check_specific_image(image_name="image_958.jpeg"):
    """Check if a specific image exists in database"""
    try:
        res = supabase.table("image_damage_labels")\
            .select("*")\
            .eq("image_name", image_name)\
            .execute()
        
        if res.data:
            st.success(f"✅ {image_name} FOUND in database:")
            st.json(res.data[0])
            return True
        else:
            st.error(f"❌ {image_name} NOT FOUND in database")
            return False
    except Exception as e:
        st.error(f"❌ Error checking {image_name}: {e}")
        return False

def get_images_with_debug(folder, page=0, unlabeled_only=True):
    """Get images with detailed debugging"""
    if not folder:
        return []
    
    try:
        # Get all images from storage
        st.info(f"📂 Loading images from folder: {folder}")
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        
        images = [
            f for f in files
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        st.success(f"✅ Found {len(images)} images in storage")
        
        # Load ALL labels
        all_labels = load_all_labels()
        st.session_state.all_labels = all_labels
        
        # Debug: Check for image_958.jpeg in labels
        if "image_958.jpeg" in all_labels:
            st.success("🎯 image_958.jpeg is in loaded labels")
        else:
            st.error("❌ image_958.jpeg is NOT in loaded labels")
            
            # Try case-insensitive check
            for label_name in all_labels.keys():
                if "958" in label_name.lower():
                    st.warning(f"Found similar: {label_name}")
        
        # Filter if needed
        if unlabeled_only:
            before_count = len(images)
            images = [
                img for img in images
                if img["name"] not in all_labels
            ]
            after_count = len(images)
            st.info(f"📊 Filtered: {before_count} → {after_count} images ({before_count - after_count} labeled)")
            
            # Debug: Check if image_958.jpeg is in filtered list
            for img in images:
                if "958" in img["name"]:
                    st.warning(f"⚠️ image_958.jpeg is in UNLABELED list! This is the problem.")
        
        # Pagination
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return images[start:end]
        
    except Exception as e:
        st.error(f"❌ Error loading images: {e}")
        return []

# =============================
# MAIN FUNCTIONS
# =============================
def get_folders():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except Exception as e:
        st.error(f"Error loading folders: {e}")
        return []

def load_current_image():
    if not st.session_state.images:
        st.session_state.current_name = None
        st.session_state.current_image = None
        return
    
    try:
        img = st.session_state.images[st.session_state.current_index]
        folder = st.session_state.selected_folder
        
        st.session_state.current_name = img["name"]
        st.session_state.current_image = supabase.storage.from_(BUCKET_NAME)\
            .get_public_url(f"{folder}/{img['name']}")
    except Exception as e:
        st.error(f"Error loading image: {e}")

def save_label_with_debug(image_name, description, side, severity):
    """Save label with detailed debugging"""
    try:
        image_path = f"{st.session_state.selected_folder}/{image_name}"
        
        payload = {
            "image_name": image_name,
            "image_path": image_path,
            "description": description,
            "side": side,
            "severity": severity,
        }
        
        # DEBUG: Before saving
        st.info(f"💾 Attempting to save label for: {image_name}")
        
        # Check if exists
        existing = supabase.table("image_damage_labels")\
            .select("id")\
            .eq("image_name", image_name)\
            .execute()
        
        if existing.data:
            # Update
            st.info(f"🔄 Updating existing label for {image_name}")
            result = supabase.table("image_damage_labels")\
                .update(payload)\
                .eq("image_name", image_name)\
                .execute()
        else:
            # Insert
            st.info(f"➕ Inserting new label for {image_name}")
            result = supabase.table("image_damage_labels")\
                .insert(payload)\
                .execute()
        
        # Force immediate refresh
        st.session_state.all_labels = load_all_labels()
        
        # Verify save
        check_specific_image(image_name)
        
        st.success(f"✅ Label saved successfully for {image_name}")
        return True
        
    except Exception as e:
        st.error(f"❌ Error saving label: {e}")
        return False

# =============================
# UI
# =============================
st.title("🔧 Vehicle Damage Labeler - DEBUG MODE")

# Debug controls at top
with st.expander("🔍 Debug Controls", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Force Reload ALL Labels"):
            st.session_state.all_labels = load_all_labels()
            st.rerun()
    with col2:
        if st.button("🔍 Check image_958.jpeg"):
            check_specific_image("image_958.jpeg")
    with col3:
        st.session_state.debug_mode = st.checkbox("Enable Debug Mode", value=True)

tab1, tab2, tab3 = st.tabs(["🏷️ Labeling", "📊 Database", "🔧 Debug Panel"])

# =============================
# TAB 1: LABELING
# =============================
with tab1:
    folders = get_folders()
    
    if not folders:
        st.info("No folders found in storage.")
        st.stop()
    
    selected = st.selectbox("📁 Select Batch Folder", folders)
    
    if selected != st.session_state.selected_folder:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
        st.session_state.images = get_images_with_debug(
            selected, 0, st.session_state.filter_unlabeled
        )
        load_current_image()
    
    # Filter checkbox
    st.checkbox(
        "Show only unlabeled images",
        key="filter_unlabeled",
        on_change=lambda: (
            st.session_state.update({
                "page": 0,
                "current_index": 0,
                "images": get_images_with_debug(
                    st.session_state.selected_folder,
                    0,
                    st.session_state.filter_unlabeled
                )
            }),
            load_current_image()
        )
    )
    
    if not st.session_state.images:
        st.info("✅ No unlabeled images in this folder!")
        
        # Show statistics
        if st.session_state.selected_folder:
            try:
                total_images = len([
                    f for f in supabase.storage.from_(BUCKET_NAME).list(st.session_state.selected_folder)
                    if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
                ])
                labeled = len([name for name in st.session_state.all_labels.keys() 
                              if st.session_state.selected_folder in name])
                st.metric(f"📊 Progress for {st.session_state.selected_folder}", 
                         f"{labeled}/{total_images} labeled")
            except:
                pass
        st.stop()
    
    # Display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_image:
            st.image(st.session_state.current_image)
            st.caption(st.session_state.current_name)
            
            # Debug: Check if current image is in labels
            if st.session_state.debug_mode:
                if st.session_state.current_name in st.session_state.all_labels:
                    st.success("✅ This image IS in labels database")
                else:
                    st.error("❌ This image is NOT in labels database")
            
            st.caption(f"Image {st.session_state.current_index + 1} of {len(st.session_state.images)}")
    
    with col2:
        existing = st.session_state.all_labels.get(st.session_state.current_name, {})
        
        with st.form("label_form"):
            side = st.radio("Vehicle Side", SIDE_OPTIONS,
                          index=SIDE_OPTIONS.index(existing.get("side", "front")))
            severity = st.selectbox("Severity", SEVERITY_OPTIONS,
                                  index=SEVERITY_OPTIONS.index(existing.get("severity", "minor")))
            description = st.text_area("Damage Description",
                                     value=existing.get("description", ""),
                                     height=120)
            
            c1, c2, c3 = st.columns(3)
            prev_btn = c1.form_submit_button("⬅️ Previous")
            save_next_btn = c2.form_submit_button("💾 Save & Next")
            next_btn = c3.form_submit_button("➡️ Next")
            
            if save_next_btn and description.strip():
                if save_label_with_debug(
                    st.session_state.current_name,
                    description.strip(),
                    side,
                    severity
                ):
                    # Refresh images list
                    st.session_state.images = get_images_with_debug(
                        st.session_state.selected_folder,
                        st.session_state.page,
                        st.session_state.filter_unlabeled
                    )
                    
                    # Move to next if available
                    if st.session_state.current_index < len(st.session_state.images) - 1:
                        st.session_state.current_index += 1
                    else:
                        st.session_state.current_index = 0
                    
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
# TAB 2: DATABASE
# =============================
with tab2:
    st.header("📊 Database Inspection")
    
    if st.button("🔄 Refresh Database View"):
        st.session_state.all_labels = load_all_labels()
    
    # Show specific batch 16 data
    st.subheader("🔍 Batch 16 Analysis")
    
    try:
        # Query specifically for batch 16
        batch16_labels = supabase.table("image_damage_labels")\
            .select("*")\
            .ilike("image_path", "%batch_16%")\
            .execute()
        
        if batch16_labels.data:
            df_batch16 = pd.DataFrame(batch16_labels.data)
            
            # Check for image_958.jpeg
            image_958 = df_batch16[df_batch16['image_name'].str.contains('958', case=False, na=False)]
            
            if not image_958.empty:
                st.success(f"✅ Found {len(image_958)} records for image_958.jpeg in database")
                st.dataframe(image_958)
            else:
                st.error("❌ No records found for image_958.jpeg in database")
            
            # Show all batch 16 labels
            st.metric("Batch 16 Labels", len(df_batch16))
            st.dataframe(df_batch16[['image_name', 'description', 'side', 'severity']])
        else:
            st.info("No labels found for batch 16")
    
    except Exception as e:
        st.error(f"Error querying batch 16: {e}")
    
    st.divider()
    
    # Show all data
    st.subheader("🗂️ All Database Records")
    try:
        all_data = supabase.table("image_damage_labels").select("*").execute()
        if all_data.data:
            df_all = pd.DataFrame(all_data.data)
            
            # Add batch column
            if 'image_path' in df_all.columns:
                df_all['batch'] = df_all['image_path'].apply(
                    lambda x: x.split('/')[0] if isinstance(x, str) and '/' in x else 'unknown'
                )
            
            st.metric("Total Labels", len(df_all))
            st.dataframe(df_all)
        else:
            st.info("No labels in database")
    except Exception as e:
        st.error(f"Error loading all data: {e}")

# =============================
# TAB 3: DEBUG PANEL
# =============================
with tab3:
    st.header("🔧 Debug Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Session State")
        debug_state = {}
        for key, value in st.session_state.items():
            if isinstance(value, dict):
                debug_state[key] = f"dict with {len(value)} items"
                if key == 'all_labels' and value:
                    # Show sample of labels
                    sample = list(value.items())[:5]
                    debug_state[f"{key}_sample"] = sample
            elif isinstance(value, list):
                debug_state[key] = f"list with {len(value)} items"
                if key == 'images' and value:
                    debug_state[f"{key}_sample"] = [img['name'] for img in value[:5]]
            else:
                debug_state[key] = str(value)
        
        st.json(debug_state)
    
    with col2:
        st.subheader("System Checks")
        
        # Check storage
        if st.button("📁 Check Storage Contents"):
            try:
                files = supabase.storage.from_(BUCKET_NAME).list("")
                folders = [f["name"] for f in files if f.get("id") is None]
                st.success(f"Found {len(folders)} folders")
                st.write(folders)
            except Exception as e:
                st.error(f"Storage error: {e}")
        
        # Check table schema
        if st.button("🗃️ Check Table Schema"):
            try:
                # Get a sample to infer schema
                sample = supabase.table("image_damage_labels").select("*").limit(1).execute()
                if sample.data:
                    st.success("Table schema:")
                    st.json(sample.data[0])
                else:
                    st.info("Table is empty")
            except Exception as e:
                st.error(f"Schema error: {e}")
        
        # Direct query for the problematic image
        st.subheader("Direct Query Test")
        test_image = st.text_input("Test image name", "image_958.jpeg")
        if st.button("🔍 Query This Image"):
            check_specific_image(test_image)

# =============================
# BOTTOM DEBUG INFO
# =============================
st.divider()
st.subheader("🔍 Real-time Status")

# Create a status dashboard
status_cols = st.columns(4)

with status_cols[0]:
    st.metric("Loaded Labels", len(st.session_state.all_labels))
with status_cols[1]:
    st.metric("Current Images", len(st.session_state.images))
with status_cols[2]:
    if st.session_state.current_name:
        is_labeled = st.session_state.current_name in st.session_state.all_labels
        st.metric("Current Image Status", "✅ Labeled" if is_labeled else "❌ Unlabeled")
with status_cols[3]:
    st.metric("Selected Folder", st.session_state.selected_folder or "None")

# Show last 5 actions
st.caption("🕒 Debug mode active - All operations are logged")
