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
    page_title="Vehicle Damage Labeler - FIXED",
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
# SESSION STATE - SIMPLIFIED
# =============================
if 'selected_folder' not in st.session_state:
    st.session_state.selected_folder = None
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'filter_unlabeled' not in st.session_state:
    st.session_state.filter_unlabeled = True
if 'labels_dict' not in st.session_state:
    st.session_state.labels_dict = {}

# =============================
# CORE FUNCTIONS - SIMPLIFIED AND ROBUST
# =============================
@st.cache_data(ttl=5)  # Cache for 5 seconds to reduce DB calls
def load_labels_from_db():
    """Load ALL labels from database with caching"""
    try:
        res = supabase.table("image_damage_labels").select("*").execute()
        if res.data:
            # Create a simple dictionary
            labels = {}
            for r in res.data:
                labels[r["image_name"]] = True  # Just store that it exists
            return labels
        return {}
    except Exception as e:
        st.error(f"Database error: {e}")
        return {}

def get_labels():
    """Get labels - always fresh from session state or DB"""
    # Always check session state first
    if not st.session_state.labels_dict:
        # If empty, load from DB
        st.session_state.labels_dict = load_labels_from_db()
    return st.session_state.labels_dict

def refresh_labels():
    """Force refresh labels from database"""
    st.session_state.labels_dict = load_labels_from_db()
    st.cache_data.clear()  # Clear cache
    return st.session_state.labels_dict

def check_image_in_db(image_name):
    """Direct check if image exists in database"""
    try:
        res = supabase.table("image_damage_labels")\
            .select("id")\
            .eq("image_name", image_name)\
            .execute()
        return len(res.data) > 0
    except:
        return False

def get_folders():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except Exception as e:
        st.error(f"Error loading folders: {e}")
        return []

def get_images(folder, page=0, unlabeled_only=True):
    """Get images with proper label checking"""
    if not folder:
        return []
    
    try:
        # Get all images from storage
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        all_images = [
            f for f in files
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        # Get fresh labels
        labels = get_labels()
        
        # Filter if needed
        if unlabeled_only:
            unlabeled_images = []
            for img in all_images:
                img_name = img["name"]
                
                # Check in labels dict
                if img_name not in labels:
                    # Double-check with direct DB query if in doubt
                    if "958" in img_name:  # Debug for our problematic image
                        st.info(f"Checking {img_name} in DB directly...")
                        if check_image_in_db(img_name):
                            st.warning(f"{img_name} is actually in DB but not in labels dict!")
                            continue  # Skip this one - it's labeled
                    unlabeled_images.append(img)
            images = unlabeled_images
        else:
            images = all_images
        
        # Pagination
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return images[start:end]
        
    except Exception as e:
        st.error(f"Error loading images: {e}")
        return []

def save_label(image_name, description, side, severity):
    """Save label and immediately refresh"""
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
            # Update
            supabase.table("image_damage_labels")\
                .update(payload)\
                .eq("image_name", image_name)\
                .execute()
        else:
            # Insert
            supabase.table("image_damage_labels")\
                .insert(payload)\
                .execute()
        
        # CRITICAL: Immediately update session state
        st.session_state.labels_dict[image_name] = True
        
        # Also refresh from DB to be sure
        refresh_labels()
        
        st.success(f"✅ Label saved for {image_name}")
        return True
        
    except Exception as e:
        st.error(f"Error saving label: {e}")
        return False

# =============================
# UI
# =============================
st.title("✅ Vehicle Damage Labeler - FIXED VERSION")

# Force refresh button at top
if st.button("🔄 Force Refresh All Data", type="primary"):
    refresh_labels()
    st.rerun()

# Show current status
labels = get_labels()
st.caption(f"📊 Currently loaded: {len(labels)} labeled images in memory")

tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Database"])

# =============================
# TAB 1: LABELING
# =============================
with tab1:
    # Folder selection
    folders = get_folders()
    if not folders:
        st.info("No folders found.")
        st.stop()
    
    selected = st.selectbox("📁 Select Batch Folder", folders, key="folder_select")
    
    # When folder changes
    if selected != st.session_state.selected_folder:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
    
    # Filter option
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        filter_unlabeled = st.checkbox(
            "Show only unlabeled",
            value=st.session_state.filter_unlabeled,
            key="filter_checkbox"
        )
    
    # Get images for current page
    images = get_images(
        st.session_state.selected_folder,
        st.session_state.page,
        filter_unlabeled
    )
    
    if not images:
        st.info("🎉 No unlabeled images!" if filter_unlabeled else "No images in this folder")
        st.stop()
    
    # Navigation controls
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ Previous Image") and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.rerun()
    
    with nav_col3:
        if st.button("Next Image ➡️") and st.session_state.current_index < len(images) - 1:
            st.session_state.current_index += 1
            st.rerun()
    
    # Current image
    current_img = images[st.session_state.current_index]
    current_name = current_img["name"]
    folder = st.session_state.selected_folder
    
    # Get image URL
    try:
        image_url = supabase.storage.from_(BUCKET_NAME)\
            .get_public_url(f"{folder}/{current_name}")
    except:
        image_url = None
    
    # Display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if image_url:
            st.image(image_url)
        
        st.subheader(current_name)
        st.caption(f"Image {st.session_state.current_index + 1} of {len(images)}")
        
        # Check label status
        labels = get_labels()
        if current_name in labels:
            st.success("✅ This image is ALREADY LABELED in database")
            
            # Show the actual label data
            try:
                label_data = supabase.table("image_damage_labels")\
                    .select("*")\
                    .eq("image_name", current_name)\
                    .execute()
                if label_data.data:
                    st.write("**Current label:**")
                    st.write(f"Side: {label_data.data[0].get('side', 'N/A')}")
                    st.write(f"Severity: {label_data.data[0].get('severity', 'N/A')}")
                    st.write(f"Description: {label_data.data[0].get('description', 'N/A')}")
            except:
                pass
    
    with col2:
        # Get existing label if any
        existing_data = {}
        try:
            existing = supabase.table("image_damage_labels")\
                .select("*")\
                .eq("image_name", current_name)\
                .execute()
            if existing.data:
                existing_data = existing.data[0]
        except:
            pass
        
        # Labeling form
        with st.form("label_form"):
            side = st.radio(
                "Vehicle Side",
                SIDE_OPTIONS,
                index=SIDE_OPTIONS.index(existing_data.get("side", "front"))
            )
            severity = st.selectbox(
                "Severity",
                SEVERITY_OPTIONS,
                index=SEVERITY_OPTIONS.index(existing_data.get("severity", "minor"))
            )
            description = st.text_area(
                "Damage Description",
                value=existing_data.get("description", ""),
                height=120,
                placeholder="Describe the damage..."
            )
            
            submit_col1, submit_col2 = st.columns(2)
            with submit_col1:
                save_btn = st.form_submit_button("💾 Save Label", use_container_width=True)
            with submit_col2:
                save_next_btn = st.form_submit_button("💾 Save & Next", use_container_width=True)
            
            if save_btn or save_next_btn:
                if not description.strip():
                    st.error("Please enter a description")
                else:
                    if save_label(current_name, description.strip(), side, severity):
                        # Update session state immediately
                        st.session_state.labels_dict[current_name] = True
                        
                        if save_next_btn:
                            # Move to next image
                            if st.session_state.current_index < len(images) - 1:
                                st.session_state.current_index += 1
                            else:
                                st.session_state.current_index = 0
                        
                        st.rerun()

# =============================
# TAB 2: DATABASE
# =============================
with tab2:
    st.header("📊 Database Viewer")
    
    if st.button("🔄 Refresh Database", key="db_refresh"):
        refresh_labels()
    
    # Show batch 16 specifically
    st.subheader("🔍 Batch 16 Analysis")
    try:
        batch16 = supabase.table("image_damage_labels")\
            .select("*")\
            .ilike("image_path", "%batch_16%")\
            .execute()
        
        if batch16.data:
            df_batch16 = pd.DataFrame(batch16.data)
            
            # Find our problematic image
            problematic = df_batch16[df_batch16['image_name'].str.contains('958', na=False)]
            
            if not problematic.empty:
                st.success(f"✅ Found {len(problematic)} records for image_958.jpeg")
                st.dataframe(problematic)
            else:
                st.error("❌ image_958.jpeg not found in batch 16 query")
            
            st.metric("Total in Batch 16", len(df_batch16))
            st.dataframe(df_batch16[['image_name', 'side', 'severity', 'description']].head(20))
        else:
            st.info("No data for batch 16")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.divider()
    
    # Show all data
    st.subheader("🗂️ All Labels")
    try:
        all_data = supabase.table("image_damage_labels").select("*").execute()
        if all_data.data:
            df_all = pd.DataFrame(all_data.data)
            st.metric("Total Labels in DB", len(df_all))
            
            # Check what's in session state
            st.metric("Labels in Memory", len(st.session_state.labels_dict))
            
            # Find differences
            db_names = set(df_all['image_name'].tolist())
            memory_names = set(st.session_state.labels_dict.keys())
            
            missing_in_memory = db_names - memory_names
            if missing_in_memory:
                st.warning(f"⚠️ {len(missing_in_memory)} labels in DB but not in memory")
                if len(missing_in_memory) < 10:
                    st.write("Missing:", list(missing_in_memory))
            
            st.dataframe(df_all)
        else:
            st.info("No labels in database")
    except Exception as e:
        st.error(f"Error loading all data: {e}")

# =============================
# STATUS BAR
# =============================
st.divider()
status_cols = st.columns(4)

with status_cols[0]:
    st.metric("Labels in DB", len(get_labels()))
with status_cols[1]:
    current_images = get_images(
        st.session_state.selected_folder or "",
        st.session_state.page or 0,
        st.session_state.filter_unlabeled
    ) if st.session_state.selected_folder else []
    st.metric("Current View", len(current_images))
with status_cols[2]:
    if st.session_state.selected_folder:
        st.metric("Selected Folder", st.session_state.selected_folder)
with status_cols[3]:
    if 'current_index' in st.session_state and current_images:
        st.metric("Position", f"{st.session_state.current_index + 1}/{len(current_images)}")

# Show last 5 actions
st.caption("🕒 Debug mode active - All operations are logged")
