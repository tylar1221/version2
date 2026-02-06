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
    "labels_refresh_counter": 0,
    "current_index": 0,
    "filter_unlabeled": True,
    "current_name": None,
    "current_image": None,
    "last_refresh_counter": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# HELPERS
# =============================
def load_labels(force_refresh=False):
    """Load labels from Supabase"""
    try:
        res = supabase.table("image_damage_labels").select("*").execute()
        if res.data:
            return {r["image_name"]: r for r in res.data}
        return {}
    except Exception as e:
        st.error(f"Error loading labels: {e}")
        return {}

def get_folders():
    """Get list of folders from storage"""
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except Exception as e:
        st.error(f"Error loading folders: {e}")
        return []

def get_images_page(folder, page=0, unlabeled_only=True):
    """Get images for current page - FIXED VERSION"""
    if not folder:
        return []
    
    try:
        # Get ALL images from storage
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        images = [
            f for f in files
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        # Always refresh labels from database
        fresh_labels = load_labels(force_refresh=True)
        st.session_state.labels = fresh_labels
        
        # Filter using fresh labels
        if unlabeled_only:
            images = [
                img for img in images
                if img["name"] not in fresh_labels
            ]
        
        # Pagination
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return images[start:end]
        
    except Exception as e:
        st.error(f"Error loading images: {e}")
        return []

def load_current_image():
    """Load current image URL"""
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

def save_label(image_name, description, side, severity):
    """Save label to database"""
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
        
        # Force refresh
        st.session_state.labels = load_labels(force_refresh=True)
        st.session_state.labels_refresh_counter += 1
        
        st.success(f"✅ Label saved for {image_name}")
        return True
        
    except Exception as e:
        st.error(f"Error saving label: {e}")
        return False

# =============================
# INITIAL LOAD
# =============================
st.session_state.labels = load_labels(force_refresh=True)

# =============================
# UI
# =============================
st.title("📂 Vehicle Damage Labeler")

tab1, tab2 = st.tabs(["🏷️ Labeling", "📊 Live Supabase Data"])

# =============================
# TAB 1: LABELING
# =============================
with tab1:
    # Folder selection
    folders = get_folders()
    if not folders:
        st.info("No folders found in storage.")
        st.stop()
    
    selected = st.selectbox("📁 Select Batch Folder", folders)
    
    # Check if refresh needed
    refresh_needed = st.session_state.get('labels_refresh_counter', 0) != st.session_state.get('last_refresh_counter', 0)
    
    if selected != st.session_state.selected_folder or refresh_needed:
        st.session_state.selected_folder = selected
        st.session_state.page = 0
        st.session_state.current_index = 0
        st.session_state.images = get_images_page(
            selected, 0, st.session_state.filter_unlabeled
        )
        load_current_image()
        st.session_state.last_refresh_counter = st.session_state.labels_refresh_counter
    
    # Filter checkbox with callback
    def update_filter():
        st.session_state.page = 0
        st.session_state.current_index = 0
        st.session_state.images = get_images_page(
            st.session_state.selected_folder,
            0,
            st.session_state.filter_unlabeled
        )
        load_current_image()
    
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        st.checkbox(
            "Show only unlabeled images",
            key="filter_unlabeled",
            on_change=update_filter,
            help="Images will disappear immediately after labeling."
        )
    
    # Check if no images
    if not st.session_state.images:
        st.info("✅ No unlabeled images in this folder!" if st.session_state.filter_unlabeled else "No images available in this folder.")
        
        # Show statistics
        if st.session_state.selected_folder:
            try:
                total_images = len([
                    f for f in supabase.storage.from_(BUCKET_NAME).list(st.session_state.selected_folder)
                    if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
                ])
                labeled = len([name for name in st.session_state.labels.keys() 
                              if name.startswith(st.session_state.selected_folder)])
                st.metric(f"📊 Progress", 
                         f"{labeled}/{total_images} labeled ({labeled/total_images*100:.0f}%)")
            except:
                pass
        st.stop()
    
    # Main columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display current image
        if st.session_state.current_image:
            st.image(st.session_state.current_image)
            st.caption(st.session_state.current_name)
            
            # Show progress
            st.caption(
                f"📄 Page {st.session_state.page + 1} | "
                f"🖼️ Image {st.session_state.current_index + 1} of {len(st.session_state.images)}"
            )
            
            # Show if already labeled
            if st.session_state.current_name in st.session_state.labels:
                st.success("✅ This image is already labeled")
    
    with col2:
        # Get existing label data
        existing = st.session_state.labels.get(st.session_state.current_name, {})
        
        # Create form
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
                height=120,
                placeholder="Describe the damage location, type, and extent..."
            )
            
            # Buttons
            c1, c2, c3 = st.columns(3)
            prev_btn = c1.form_submit_button("⬅️ Previous", use_container_width=True)
            save_next_btn = c2.form_submit_button("💾 Save & Next", use_container_width=True)
            next_btn = c3.form_submit_button("➡️ Next", use_container_width=True)
            
            # Handle save
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
            
            # Handle navigation
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
    
    # Refresh button
    if st.button("🔄 Refresh Live Data", type="primary"):
        st.session_state.labels = load_labels(force_refresh=True)
        st.rerun()
    
    # Load data
    try:
        res = supabase.table("image_damage_labels").select("*").execute()
        data = res.data
        
        if not data:
            st.info("No labels in database yet.")
            st.stop()
        
        df = pd.DataFrame(data)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Labels", len(df))
        col2.metric("Unique Images", df["image_name"].nunique())
        
        # Add batch column if image_path exists
        if 'image_path' in df.columns:
            df['batch'] = df['image_path'].apply(lambda x: x.split('/')[0] if '/' in x and isinstance(x, str) else 'unknown')
            col3.metric("Unique Batches", df['batch'].nunique())
        
        st.divider()
        
        # Show full table
        st.subheader("🗂️ Full Label Table")
        st.dataframe(df, width='stretch')
        
    except Exception as e:
        st.error(f"Error loading database: {e}")

# =============================
# DEBUG PANEL (Optional)
# =============================
with st.expander("🔧 Debug Info"):
    st.write("### Session State")
    debug_data = {}
    for k, v in st.session_state.items():
        if isinstance(v, dict):
            debug_data[k] = f"dict with {len(v)} items"
        elif isinstance(v, list):
            debug_data[k] = f"list with {len(v)} items"
        else:
            debug_data[k] = str(v)[:100]
    st.json(debug_data)
    
    st.write("### Database Status")
    st.write(f"Labels loaded: {len(st.session_state.labels)}")
    st.write(f"Current folder: {st.session_state.selected_folder}")
    st.write(f"Images in view: {len(st.session_state.images)}")
    
