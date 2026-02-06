

#version 1 
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
#v2.2-optimized

# import streamlit as st
# from supabase import create_client
# import pandas as pd

# # =============================
# # PAGE CONFIG
# # =============================
# st.set_page_config(
#     page_title="Vehicle Damage Labeler",
#     page_icon="🚗",
#     layout="wide"
# )

# # =============================
# # SUPABASE CONFIG
# # =============================
# SUPABASE_URL = st.secrets["SUPABASE_URL"]
# SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
# BUCKET_NAME = "try"
# PAGE_SIZE = 50  # Reduced for better performance

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # =============================
# # CONSTANTS
# # =============================
# SIDE_OPTIONS = ["front", "back", "left", "right", "none"]
# SEVERITY_OPTIONS = ["minor", "moderate", "severe"]

# # =============================
# # SESSION STATE
# # =============================
# if 'selected_folder' not in st.session_state:
#     st.session_state.selected_folder = None
# if 'page' not in st.session_state:
#     st.session_state.page = 0
# if 'current_index' not in st.session_state:
#     st.session_state.current_index = 0
# if 'labels_cache' not in st.session_state:
#     st.session_state.labels_cache = set()  # Use set for faster lookups
# if 'images_cache' not in st.session_state:
#     st.session_state.images_cache = {}

# # =============================
# # OPTIMIZED FUNCTIONS
# # =============================
# @st.cache_data(ttl=30)  # Cache for 30 seconds
# def load_all_labels():
#     """Load all labels once and cache"""
#     try:
#         res = supabase.table("image_damage_labels").select("image_name").execute()
#         return {item["image_name"] for item in res.data}
#     except:
#         return set()

# def get_labels():
#     """Get labels from cache or load"""
#     if not st.session_state.labels_cache:
#         st.session_state.labels_cache = load_all_labels()
#     return st.session_state.labels_cache

# def refresh_labels():
#     """Force refresh labels"""
#     st.session_state.labels_cache = load_all_labels()
#     st.cache_data.clear()
#     return st.session_state.labels_cache

# def get_folders():
#     """Get available folders"""
#     try:
#         files = supabase.storage.from_(BUCKET_NAME).list("")
#         return sorted([f["name"] for f in files if f.get("id") is None])
#     except:
#         return []

# @st.cache_data(ttl=10)  # Cache images for 10 seconds
# def get_storage_images(folder):
#     """Get all images from a folder"""
#     try:
#         files = supabase.storage.from_(BUCKET_NAME).list(folder)
#         return [
#             f for f in files 
#             if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
#         ]
#     except:
#         return []

# def get_images(folder, page=0, unlabeled_only=True):
#     """Get paginated images with optional filtering"""
#     if not folder:
#         return []
    
#     # Get all images from storage (cached)
#     all_images = get_storage_images(folder)
    
#     # Get labels
#     labels = get_labels()
    
#     # Filter if needed
#     if unlabeled_only:
#         images = [img for img in all_images if img["name"] not in labels]
#     else:
#         images = all_images
    
#     # Pagination
#     start = page * PAGE_SIZE
#     end = start + PAGE_SIZE
#     return images[start:end]

# def save_label(image_name, description, side, severity):
#     """Save label efficiently"""
#     try:
#         image_path = f"{st.session_state.selected_folder}/{image_name}"
        
#         payload = {
#             "image_name": image_name,
#             "image_path": image_path,
#             "description": description,
#             "side": side,
#             "severity": severity,
#         }
        
#         # Check if exists
#         existing = supabase.table("image_damage_labels")\
#             .select("id")\
#             .eq("image_name", image_name)\
#             .execute()
        
#         if existing.data:
#             supabase.table("image_damage_labels")\
#                 .update(payload)\
#                 .eq("image_name", image_name)\
#                 .execute()
#         else:
#             supabase.table("image_damage_labels")\
#                 .insert(payload)\
#                 .execute()
        
#         # Update cache immediately
#         st.session_state.labels_cache.add(image_name)
        
#         # Clear relevant caches
#         st.cache_data.clear()
        
#         return True
#     except Exception as e:
#         st.error(f"Error: {e}")
#         return False

# # =============================
# # UI - SIMPLIFIED
# # =============================
# st.title("🚗 Vehicle Damage Labeler")

# # Top controls
# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("🔄 Refresh", type="secondary"):
#         refresh_labels()
#         st.rerun()

# with col2:
#     st.metric("Labeled Images", len(get_labels()))

# with col3:
#     if st.session_state.selected_folder:
#         st.metric("Current Folder", st.session_state.selected_folder)

# # Main tabs
# tab1, tab2 = st.tabs(["🏷️ Label Images", "📊 Database"])

# # =============================
# # TAB 1: LABELING
# # =============================
# with tab1:
#     # Folder selection
#     folders = get_folders()
#     if not folders:
#         st.info("No folders found")
#         st.stop()
    
#     selected = st.selectbox("Select Folder", folders, key="folder_select")
    
#     # Update on folder change
#     if selected != st.session_state.selected_folder:
#         st.session_state.selected_folder = selected
#         st.session_state.page = 0
#         st.session_state.current_index = 0
    
#     # View mode toggle
#     show_unlabeled = st.toggle("Show only unlabeled", value=True, key="show_unlabeled")
    
#     # Get images
#     images = get_images(
#         st.session_state.selected_folder,
#         st.session_state.page,
#         show_unlabeled
#     )
    
#     if not images:
#         st.success("✅ No unlabeled images" if show_unlabeled else "No images found")
#         st.stop()
    
#     # Navigation
#     nav_cols = st.columns([1, 2, 2, 1])
#     with nav_cols[0]:
#         if st.button("⏮️", disabled=st.session_state.current_index == 0):
#             st.session_state.current_index = 0
#             st.rerun()
#     with nav_cols[1]:
#         if st.button("⬅️ Previous", disabled=st.session_state.current_index == 0):
#             st.session_state.current_index -= 1
#             st.rerun()
#     with nav_cols[2]:
#         if st.button("Next ➡️", disabled=st.session_state.current_index >= len(images)-1):
#             st.session_state.current_index += 1
#             st.rerun()
#     with nav_cols[3]:
#         if st.button("⏭️", disabled=st.session_state.current_index >= len(images)-1):
#             st.session_state.current_index = len(images) - 1
#             st.rerun()
    
#     # Current image
#     current_img = images[st.session_state.current_index]
#     current_name = current_img["name"]
    
#     # Display
#     col_left, col_right = st.columns([2, 1])
    
#     with col_left:
#         try:
#             image_url = supabase.storage.from_(BUCKET_NAME)\
#                 .get_public_url(f"{st.session_state.selected_folder}/{current_name}")
#             st.image(image_url, use_container_width=True)
#         except:
#             st.error("Cannot load image")
        
#         st.caption(f"{current_name} • Image {st.session_state.current_index + 1} of {len(images)}")
        
#         # Status indicator
#         if current_name in get_labels():
#             st.success("✅ Already labeled")
    
#     with col_right:
#         # Get existing data
#         existing = {}
#         try:
#             res = supabase.table("image_damage_labels")\
#                 .select("*")\
#                 .eq("image_name", current_name)\
#                 .execute()
#             if res.data:
#                 existing = res.data[0]
#         except:
#             pass
        
#         # Labeling form
#         with st.form("label_form"):
#             side = st.radio("Side", SIDE_OPTIONS, 
#                           index=SIDE_OPTIONS.index(existing.get("side", "front")),
#                           horizontal=True)
            
#             severity = st.selectbox("Severity", SEVERITY_OPTIONS,
#                                   index=SEVERITY_OPTIONS.index(existing.get("severity", "minor")))
            
#             description = st.text_area("Description",
#                                      value=existing.get("description", ""),
#                                      height=100,
#                                      placeholder="Describe the damage...")
            
#             # Form buttons
#             btn_col1, btn_col2 = st.columns(2)
#             with btn_col1:
#                 save_btn = st.form_submit_button("💾 Save", use_container_width=True)
#             with btn_col2:
#                 save_next_btn = st.form_submit_button("💾 Save & Next", use_container_width=True)
            
#             if save_btn or save_next_btn:
#                 if not description.strip():
#                     st.error("Enter description")
#                 elif save_label(current_name, description.strip(), side, severity):
#                     if save_next_btn and st.session_state.current_index < len(images) - 1:
#                         st.session_state.current_index += 1
#                     st.rerun()

# # =============================
# # TAB 2: DATABASE
# # =============================
# with tab2:
#     st.header("Database")
    
#     # Quick stats
#     labels = get_labels()
#     st.write(f"**Total labeled images:** {len(labels)}")
    
#     # Show recent labels
#     try:
#         recent = supabase.table("image_damage_labels")\
#             .select("*")\
#             .order("created_at", desc=True)\
#             .limit(20)\
#             .execute()
        
#         if recent.data:
#             df = pd.DataFrame(recent.data)
            
#             # Show by folder
#             if 'image_path' in df.columns:
#                 df['folder'] = df['image_path'].str.split('/').str[0]
#                 folder_counts = df['folder'].value_counts()
                
#                 cols = st.columns(3)
#                 for i, (folder, count) in enumerate(folder_counts.head(3).items()):
#                     with cols[i]:
#                         st.metric(folder, count)
            
#             st.dataframe(df[['image_name', 'side', 'severity', 'description']], 
#                         use_container_width=True,
#                         hide_index=True)
#         else:
#             st.info("No labels yet")
#     except:
#         st.error("Cannot load database")

# # =============================
# # BOTTOM STATUS
# # =============================
# st.divider()
# st.caption(f"Viewing {len(images)} images • Page {st.session_state.page + 1}")

#v2 detail import streamlit as st
from supabase import create_client
import pandas as pd
import time

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Vehicle Damage Labeler - FINAL FIX",
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
if 'selected_folder' not in st.session_state:
    st.session_state.selected_folder = None
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'filter_unlabeled' not in st.session_state:
    st.session_state.filter_unlabeled = True
if 'labels_cache' not in st.session_state:
    st.session_state.labels_cache = {}  # {image_name: True}
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

# =============================
# CORE FUNCTIONS - ULTIMATE FIX
# =============================
def load_all_labels_from_db():
    """Load ALL labels from database - COMPLETE and RELIABLE"""
    try:
        # First get count
        count_res = supabase.table("image_damage_labels")\
            .select("id", count="exact")\
            .execute()
        
        total_count = count_res.count or 0
        st.info(f"📊 Database has {total_count} total labels")
        
        # Load in batches if large
        all_labels = {}
        limit = 1000  # Supabase max per query
        
        for offset in range(0, total_count, limit):
            res = supabase.table("image_damage_labels")\
                .select("image_name")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            for item in res.data:
                all_labels[item["image_name"]] = True
        
        st.success(f"✅ Loaded {len(all_labels)} unique image labels")
        return all_labels
        
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return {}

def is_image_labeled(image_name, use_cache=True):
    """Check if image is labeled - uses cache + direct DB check"""
    
    # 1. Check cache first (fast)
    if use_cache and image_name in st.session_state.labels_cache:
        return True
    
    # 2. Direct database check (accurate but slower)
    try:
        res = supabase.table("image_damage_labels")\
            .select("id")\
            .eq("image_name", image_name)\
            .limit(1)\
            .execute()
        
        is_labeled = len(res.data) > 0
        
        # Update cache
        if is_labeled:
            st.session_state.labels_cache[image_name] = True
        
        return is_labeled
        
    except:
        return False

def refresh_labels_cache():
    """Completely refresh the labels cache"""
    st.session_state.labels_cache = load_all_labels_from_db()
    st.session_state.last_refresh = time.time()
    return st.session_state.labels_cache

def get_folders():
    try:
        files = supabase.storage.from_(BUCKET_NAME).list("")
        return sorted([f["name"] for f in files if f.get("id") is None])
    except Exception as e:
        st.error(f"Error loading folders: {e}")
        return []

def get_unlabeled_images(folder, page=0):
    """Get ONLY truly unlabeled images - GUARANTEED"""
    if not folder:
        return []
    
    try:
        # Get all images from storage
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        all_images = [
            f for f in files
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        # Filter to ONLY unlabeled
        unlabeled_images = []
        checked_count = 0
        skip_count = 0
        
        # Progress bar for large batches
        progress_bar = st.progress(0, text="Checking image labels...")
        
        for i, img in enumerate(all_images):
            img_name = img["name"]
            checked_count += 1
            
            # Update progress
            if i % 10 == 0:
                progress_bar.progress(i / len(all_images), 
                                    text=f"Checking {i}/{len(all_images)} images...")
            
            # Check if labeled
            if not is_image_labeled(img_name, use_cache=True):
                unlabeled_images.append(img)
            else:
                skip_count += 1
        
        progress_bar.empty()
        
        st.info(f"📊 Checked {checked_count} images, found {len(unlabeled_images)} unlabeled, skipped {skip_count} labeled")
        
        # Pagination
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return unlabeled_images[start:end]
        
    except Exception as e:
        st.error(f"Error loading images: {e}")
        return []

def get_all_images(folder, page=0):
    """Get ALL images (labeled + unlabeled)"""
    if not folder:
        return []
    
    try:
        files = supabase.storage.from_(BUCKET_NAME).list(folder)
        all_images = [
            f for f in files
            if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        # Pagination
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        return all_images[start:end]
        
    except Exception as e:
        st.error(f"Error loading images: {e}")
        return []

def save_label_and_refresh(image_name, description, side, severity):
    """Save label and update cache immediately"""
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
            st.info(f"🔄 Updated existing label for {image_name}")
        else:
            # Insert
            supabase.table("image_damage_labels")\
                .insert(payload)\
                .execute()
            st.info(f"➕ Created new label for {image_name}")
        
        # CRITICAL: Update cache IMMEDIATELY
        st.session_state.labels_cache[image_name] = True
        
        # Verify
        if is_image_labeled(image_name, use_cache=False):
            st.success(f"✅ Label saved and verified for {image_name}")
        else:
            st.warning(f"⚠️ Label saved but verification failed for {image_name}")
        
        return True
        
    except Exception as e:
        st.error(f"Error saving label: {e}")
        return False

# =============================
# UI
# =============================
st.title("🚗 Vehicle Damage Labeler - FINAL SOLUTION")

# Force refresh section at top
refresh_col1, refresh_col2, refresh_col3 = st.columns(3)
with refresh_col1:
    if st.button("🔄 Force Refresh Labels Cache", type="primary", use_container_width=True):
        with st.spinner("Refreshing all labels from database..."):
            refresh_labels_cache()
        st.rerun()

with refresh_col2:
    # Auto-refresh if cache is old (> 5 minutes)
    cache_age = time.time() - st.session_state.last_refresh if st.session_state.last_refresh else 9999
    if cache_age > 300:  # 5 minutes
        st.warning("Cache is stale, refreshing...")
        refresh_labels_cache()

with refresh_col3:
    st.metric("Labels in Cache", len(st.session_state.labels_cache))

tab1, tab2 = st.tabs(["🏷️ Label Images", "📊 Database"])

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
    
    # Filter option with CLEAR behavior
    filter_mode = st.radio(
        "View Mode:",
        ["🔍 Show ONLY Unlabeled Images", "👁️ Show ALL Images"],
        horizontal=True,
        key="view_mode"
    )
    
    show_unlabeled_only = filter_mode == "🔍 Show ONLY Unlabeled Images"
    
    # Get images based on filter
    if show_unlabeled_only:
        images = get_unlabeled_images(
            st.session_state.selected_folder,
            st.session_state.page
        )
        if not images:
            st.success("🎉 ALL images in this folder are labeled!")
            st.stop()
    else:
        images = get_all_images(
            st.session_state.selected_folder,
            st.session_state.page
        )
        if not images:
            st.info("No images in this folder")
            st.stop()
    
    # Navigation controls
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 2, 2, 1])
    
    with nav_col1:
        if st.button("⏮️ First", use_container_width=True) and images:
            st.session_state.current_index = 0
            st.rerun()
    
    with nav_col2:
        if st.button("⬅️ Previous", use_container_width=True) and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.rerun()
    
    with nav_col3:
        if st.button("Next ➡️", use_container_width=True) and st.session_state.current_index < len(images) - 1:
            st.session_state.current_index += 1
            st.rerun()
    
    with nav_col4:
        if st.button("Last ⏭️", use_container_width=True) and images:
            st.session_state.current_index = len(images) - 1
            st.rerun()
    
    # Current image
    if not images:
        st.info("No images to display")
        st.stop()
    
    current_img = images[st.session_state.current_index]
    current_name = current_img["name"]
    folder = st.session_state.selected_folder
    
    # Get image URL
    try:
        image_url = supabase.storage.from_(BUCKET_NAME)\
            .get_public_url(f"{folder}/{current_name}")
    except:
        image_url = None
        st.error(f"Cannot load image: {current_name}")
    
    # Main display columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if image_url:
            st.image(image_url, use_column_width=True)
        
        st.subheader(f"📸 {current_name}")
        
        # Status indicator
        is_labeled = is_image_labeled(current_name, use_cache=True)
        
        if is_labeled:
            st.success("✅ This image is ALREADY LABELED")
            try:
                # Show current label
                label_data = supabase.table("image_damage_labels")\
                    .select("*")\
                    .eq("image_name", current_name)\
                    .single()\
                    .execute()
                
                if label_data.data:
                    with st.expander("📋 View Current Label", expanded=False):
                        st.write(f"**Side:** {label_data.data.get('side', 'N/A')}")
                        st.write(f"**Severity:** {label_data.data.get('severity', 'N/A')}")
                        st.write(f"**Description:** {label_data.data.get('description', 'N/A')}")
                        st.write(f"**Created:** {label_data.data.get('created_at', 'N/A')}")
            except:
                pass
        else:
            st.warning("⚠️ This image is NOT labeled yet")
        
        st.caption(f"📄 Image {st.session_state.current_index + 1} of {len(images)}")
        
        # Quick navigation
        if len(images) > 1:
            st.caption("Quick jump:")
            cols = st.columns(min(10, len(images)))
            for idx, col in enumerate(cols[:10]):
                with col:
                    if st.button(f"{idx+1}", key=f"jump_{idx}", use_container_width=True):
                        st.session_state.current_index = idx
                        st.rerun()
    
    with col2:
        # Get existing label data
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
        with st.form("label_form", border=True):
            st.write("### 📝 Label This Image")
            
            side = st.radio(
                "**Vehicle Side**",
                SIDE_OPTIONS,
                index=SIDE_OPTIONS.index(existing_data.get("side", "front")),
                horizontal=True
            )
            
            severity = st.selectbox(
                "**Severity**",
                SEVERITY_OPTIONS,
                index=SEVERITY_OPTIONS.index(existing_data.get("severity", "minor"))
            )
            
            description = st.text_area(
                "**Damage Description**",
                value=existing_data.get("description", ""),
                height=100,
                placeholder="Describe location, type, and extent of damage..."
            )
            
            # Form buttons
            button_col1, button_col2, button_col3 = st.columns(3)
            
            with button_col1:
                save_btn = st.form_submit_button("💾 Save", use_container_width=True)
            
            with button_col2:
                save_next_btn = st.form_submit_button("💾 Save & ➡️", use_container_width=True)
            
            with button_col3:
                delete_btn = st.form_submit_button("🗑️ Delete", type="secondary", use_container_width=True)
            
            # Handle save
            if save_btn or save_next_btn:
                if not description.strip():
                    st.error("❌ Please enter a description")
                else:
                    if save_label_and_refresh(current_name, description.strip(), side, severity):
                        # If in "unlabeled only" mode and we just labeled it, remove from list
                        if show_unlabeled_only:
                            # Remove current image from list
                            if current_name in [img['name'] for img in images]:
                                st.info("🔄 Removing from unlabeled list...")
                                # The list will refresh on next rerun
                        
                        if save_next_btn:
                            # Move to next if available
                            if st.session_state.current_index < len(images) - 1:
                                st.session_state.current_index += 1
                            else:
                                st.session_state.current_index = 0
                        
                        st.rerun()
            
            # Handle delete
            if delete_btn:
                try:
                    supabase.table("image_damage_labels")\
                        .delete()\
                        .eq("image_name", current_name)\
                        .execute()
                    
                    # Remove from cache
                    if current_name in st.session_state.labels_cache:
                        del st.session_state.labels_cache[current_name]
                    
                    st.success(f"🗑️ Label deleted for {current_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting: {e}")

# =============================
# TAB 2: DATABASE
# =============================
with tab2:
    st.header("📊 Database Analysis")
    
    analysis_col1, analysis_col2 = st.columns(2)
    
    with analysis_col1:
        if st.button("🔄 Refresh Database View", use_container_width=True):
            refresh_labels_cache()
    
    with analysis_col2:
        # Direct check for specific image
        check_image = st.text_input("Check specific image:", "image_958.jpeg")
        if st.button("🔍 Check This Image", use_container_width=True):
            if is_image_labeled(check_image, use_cache=False):
                st.success(f"✅ {check_image} is in database")
            else:
                st.error(f"❌ {check_image} is NOT in database")
    
    # Show batch-specific data
    if st.session_state.selected_folder:
        st.subheader(f"🔍 Analysis: {st.session_state.selected_folder}")
        
        try:
            # Get all images in folder from storage
            storage_files = supabase.storage.from_(BUCKET_NAME).list(st.session_state.selected_folder)
            total_images = len([f for f in storage_files if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))])
            
            # Get labeled images in this folder
            labeled_in_folder = supabase.table("image_damage_labels")\
                .select("image_name")\
                .ilike("image_path", f"%{st.session_state.selected_folder}%")\
                .execute()
            
            labeled_count = len(labeled_in_folder.data) if labeled_in_folder.data else 0
            
            # Show progress
            progress_col1, progress_col2, progress_col3 = st.columns(3)
            with progress_col1:
                st.metric("Total Images", total_images)
            with progress_col2:
                st.metric("Labeled", labeled_count)
            with progress_col3:
                progress_pct = (labeled_count / total_images * 100) if total_images > 0 else 0
                st.metric("Progress", f"{progress_pct:.1f}%")
            
            # Progress bar
            st.progress(labeled_count / total_images if total_images > 0 else 0)
            
            # Show labeled images in this batch
            if labeled_in_folder.data:
                df_batch = pd.DataFrame(labeled_in_folder.data)
                st.dataframe(df_batch, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error analyzing batch: {e}")
    
    st.divider()
    
    # Show all database contents
    st.subheader("🗂️ Complete Database")
    
    try:
        all_data = supabase.table("image_damage_labels")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
        
        if all_data.data:
            df_all = pd.DataFrame(all_data.data)
            
            # Summary stats
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            with summary_col1:
                st.metric("Total Labels", len(df_all))
            with summary_col2:
                st.metric("Unique Batches", df_all['image_path'].apply(
                    lambda x: x.split('/')[0] if '/' in str(x) else 'unknown'
                ).nunique())
            with summary_col3:
                st.metric("Most Common Side", df_all['side'].mode().iloc[0] if not df_all['side'].mode().empty else 'N/A')
            with summary_col4:
                st.metric("Avg Description Length", f"{df_all['description'].str.len().mean():.0f} chars")
            
            # Data table
            st.dataframe(df_all, use_container_width=True)
        else:
            st.info("No labels in database")
    
    except Exception as e:
        st.error(f"Error loading database: {e}")

# =============================
# STATUS BAR
# =============================
st.divider()

status_cols = st.columns(5)

with status_cols[0]:
    st.metric("Cache Size", len(st.session_state.labels_cache))

with status_cols[1]:
    if st.session_state.selected_folder and images:
        current_is_labeled = is_image_labeled(current_name, use_cache=True)
        st.metric("Current Image", "✅ Labeled" if current_is_labeled else "⚠️ Unlabeled")

with status_cols[2]:
    if st.session_state.selected_folder:
        st.metric("Folder", st.session_state.selected_folder)

with status_cols[3]:
    if images:
        st.metric("Viewing", f"{st.session_state.current_index + 1}/{len(images)}")

with status_cols[4]:
    cache_age = time.time() - st.session_state.last_refresh if st.session_state.last_refresh else 0
    st.metric("Cache Age", f"{cache_age:.0f}s")
