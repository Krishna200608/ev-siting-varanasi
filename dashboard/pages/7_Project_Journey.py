"""Page 7: Project Methodology Journey & Architectural Decisions."""

import streamlit as st

st.set_page_config(page_title="Project Journey — EV Siting Varanasi", page_icon=":material/menu_book:", layout="wide")

st.title(":material/menu_book: Project Methodology Journey & Key Decisions")
st.markdown(
    "A transparent, chronological chronicle of the core scientific, architectural, and data engineering decisions "
    "governing the evolution of this research project. Each decision documents: **What We Tried → What We Found → What We Did Instead**."
)

st.markdown("---")

# AD-1
with st.expander(":material/grid_on: AD-1: Metric UTM Zone 44N Fishnet Grid vs. Voronoi Tessellation", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Considered generating candidate EVCS siting locations via centroid Voronoi tessellation around existing amenities vs. regular spatial fishnets.
        * **What We Found:** Voronoi partitions bias candidate selection towards pre-existing dense clusters, failing to evaluate unserved transition zones.
        * **What We Did Instead:** Standardized on a **500m regular fishnet grid projected into EPSG:32644 (UTM Zone 44N)**, ensuring equal-area, metric spatial sampling across the entire urban expanse.
        """
    )

# AD-4
with st.expander(":material/block: AD-4: Rejection of Synthetic Kaggle EV Datasets", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Investigated public Kaggle datasets purporting to provide EV charging station demand and vehicle features.
        * **What We Found:** Statistical auditing revealed synthetic, AI-generated distributions with artificial correlations, zero real timestamp metadata, and fabricated columns.
        * **What We Did Instead:** Established a strict **Zero-Fabrication Policy** and adopted the **Caltech/JPL Adaptive Charging Network (ACN-Data)** repository containing **30,000+ real, physical charging session transactions** with verified energy delivered and session durations.
        """
    )

# AD-6
with st.expander(":material/block: AD-6: Rejection of Fabricated Dwell-Time Proxies", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Explored creating an `estimate_proxy_dwell_time()` function to assign assumed session durations (e.g. 3.5h for malls, 0.75h for fuel bunks) to simulate site-specific ML demand in Varanasi.
        * **What We Found:** Dwell duration accounts for ~76.2% of predictive power in the ACN model; assigning fabricated constants would make Varanasi demand scores a mere restatement of made-up numbers.
        * **What We Did Instead:** Explicitly rejected dwell-time proxies. Built a **Transferable Temporal Model** restricted strictly to observable temporal dimensions (`connection_hour`, `day_of_week`, `is_weekend`, `month`), honestly reporting **R² ≈ 0.02** as the true empirical bound of temporal-only prediction.
        """
    )

# AD-8
with st.expander(":material/lightbulb: AD-8: Rejection of Mathematically Inert Compositing (Resolution of RQ3)", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Attempted a composite demand score multiplying candidate GIS footfall by transferable ML temporal predictions: `S_i = F_i × W_temporal`.
        * **What We Found:** `W_temporal` is a uniform scalar across all candidate sites in a given time window; upon min-max normalization, multiplying by a constant produces identical rankings to footfall alone (mathematically inert). Furthermore, footfall duplicated existing MCDM criteria.
        * **What We Did Instead:** Resolved **Research Question 3 (RQ3)** with methodological clarity: GIS-MCDM TOPSIS determines **spatial location (*Where*)**, while Machine Learning temporal curves determine **operational charging schedules, dynamic tariffs, and grid transformer sizing (*When*)**.
        """
    )

# AD-9
with st.expander(":material/polyline: AD-9: Bounding Polygon Sourcing & Administrative Conformance", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Evaluated OSM administrative boundary queries vs. manual bounding boxes for Varanasi Nagar Nigam.
        * **What We Found:** OSM contains only a point node for Varanasi Nagar Nigam (`admin_level=8`), while administrative district queries cover over **1,500 km²** of predominantly rural farmland. Hand-drawn approximations risked unverified coverage.
        * **What We Did Instead:** Sourced a verified **76.99 km² urban municipal polygon** bounded by the Ganga crescent, BHU, Manduadih, Cantt, and Sarnath, generating exactly **308 candidate alternatives** representing true urban/semi-urban territory.
        """
    )

# AD-10
with st.expander(":material/balance: AD-10: Equal-Scrutiny Multi-Zone Validation & Recalibration Insight", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Investigated whether Godowlia's dominance in Milestone 6 was an artifact of receiving 5 extra nested Google Places tiles (radius 800m) while other commercial zones received only coarse grid coverage.
        * **What We Found:** Built symmetric 5-tile nested meshes across Sigra, Lanka, and Cantt (40 tiles total). Godowlia maintained 100% Top-5 dominance with a comfortable lead (+0.14). Discovered that minor score shifts in Godowlia were due to continuous raster min-max rescaling `(d_max - d_min)`, while uncovering and curing a silent API rate-limit failure in `C6_POI_Hospitals`.
        * **What We Did Instead:** Implemented permanent automated data quality validation (`validate_decision_matrix_quality()`) inside the build pipeline with 100% unit test coverage.
        """
    )

# AD-11
with st.expander(":material/cloud_done: AD-11: Dependency-Light Dashboard Architecture for Cloud Deployment", expanded=True):
    st.markdown(
        """
        * **What We Tried:** Evaluated deploying a unified Streamlit dashboard on Streamlit Community Cloud with local viva demo support.
        * **What We Found:** Heavy geospatial/ML libraries (`geopandas`, `rasterio`, `xgboost`, `shap`, `gdal`) frequently fail cloud build environments due to C-extension and system dependency conflicts.
        * **What We Did Instead:** Architected the dashboard to be **dependency-light**, reading pre-computed static artifacts for visual inspection while importing only pure Python/NumPy ranking routines from `src/mcdm/` for interactive live What-If calculations. Maintained an isolated canonical `dashboard/requirements.txt`.
        """
    )
