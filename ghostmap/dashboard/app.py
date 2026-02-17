"""
GHOSTMAP Dashboard — Interactive Streamlit visualization of audit results.
"""

import json
import sys
import os

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def load_data(filepath: str) -> dict:
    """Load audit results JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """Main Streamlit dashboard application."""
    st.set_page_config(
        page_title="👻 GHOSTMAP Dashboard",
        page_icon="👻",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown("""
    <style>
    .ghost-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #313244;
    }
    .risk-high { color: #f38ba8; font-weight: bold; }
    .risk-medium { color: #fab387; font-weight: bold; }
    .risk-low { color: #a6e3a1; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="ghost-header">
        <h1>👻 GHOSTMAP Dashboard</h1>
        <p>Discover undocumented API endpoints before attackers do</p>
    </div>
    """, unsafe_allow_html=True)

    # File selector
    input_file = None

    # Check command line args
    if len(sys.argv) > 2 and sys.argv[-2] == "--input":
        input_file = sys.argv[-1]

    # Sidebar file upload / path input
    with st.sidebar:
        st.header("📁 Data Source")
        upload = st.file_uploader("Upload audit results JSON", type=["json"])
        if upload:
            data = json.load(upload)
            input_file = "uploaded"
        else:
            file_path = st.text_input("Or enter file path:", value=input_file or "")
            if file_path and os.path.isfile(file_path):
                input_file = file_path

    if not input_file:
        st.info("👈 Upload or specify an audit results JSON file to get started.")
        st.markdown("""
        ### How to generate audit data:
        ```bash
        ghostmap collect --domain example.com --output footprint.json
        ghostmap sanitize --input footprint.json --output sanitized.json
        ghostmap audit --input sanitized.json --output audit_results.json
        ghostmap dashboard --input audit_results.json
        ```
        """)
        return

    # Load data
    if input_file == "uploaded":
        pass  # Already loaded
    else:
        data = load_data(input_file)

    meta = data.get("meta", {})
    summary = data.get("summary", {})
    endpoints = data.get("endpoints", [])

    if not endpoints:
        st.warning("No endpoints found in the data file.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(endpoints)

    # ======================================================================
    # Sidebar Filters
    # ======================================================================
    with st.sidebar:
        st.header("🔍 Filters")

        # Risk level filter
        risk_filter = st.multiselect(
            "Risk Level",
            options=["HIGH", "MEDIUM", "LOW"],
            default=["HIGH", "MEDIUM", "LOW"],
        )

        # Score range
        min_score, max_score = st.slider(
            "Risk Score Range", 0, 100, (0, 100)
        )

        # Source filter
        if "sources" in df.columns:
            all_sources = set()
            for sources_list in df["sources"].dropna():
                if isinstance(sources_list, list):
                    all_sources.update(sources_list)
            source_filter = st.multiselect(
                "Source",
                options=sorted(all_sources),
                default=sorted(all_sources),
            )
        else:
            source_filter = None

        # Ghost only toggle
        ghost_only = st.checkbox("Show Ghost Endpoints Only", value=False)

    # Apply filters
    filtered = df.copy()
    if "risk_level" in filtered.columns:
        filtered = filtered[filtered["risk_level"].isin(risk_filter)]
    if "risk_score" in filtered.columns:
        filtered = filtered[
            (filtered["risk_score"] >= min_score) &
            (filtered["risk_score"] <= max_score)
        ]
    if ghost_only and "is_ghost" in filtered.columns:
        filtered = filtered[filtered["is_ghost"] == True]
    if source_filter and "sources" in filtered.columns:
        filtered = filtered[
            filtered["sources"].apply(
                lambda x: bool(set(x if isinstance(x, list) else []) & set(source_filter))
            )
        ]

    # ======================================================================
    # Summary Cards
    # ======================================================================
    st.header("📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Endpoints", summary.get("total_endpoints", len(endpoints)))
    with col2:
        st.metric("🔴 High Risk", summary.get("high_risk", 0))
    with col3:
        st.metric("🟡 Medium Risk", summary.get("medium_risk", 0))
    with col4:
        st.metric("🟢 Low Risk", summary.get("low_risk", 0))
    with col5:
        st.metric("📋 Documented", summary.get("documented", 0))

    # ======================================================================
    # Risk Distribution Chart
    # ======================================================================
    st.header("📈 Risk Distribution")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if "risk_level" in filtered.columns:
            risk_counts = filtered["risk_level"].value_counts()
            colors = {"HIGH": "#f38ba8", "MEDIUM": "#fab387", "LOW": "#a6e3a1"}

            fig_pie = go.Figure(data=[go.Pie(
                labels=risk_counts.index.tolist(),
                values=risk_counts.values.tolist(),
                hole=0.4,
                marker=dict(colors=[colors.get(r, "#ccc") for r in risk_counts.index]),
                textinfo="label+value+percent",
            )])
            fig_pie.update_layout(
                title="Risk Level Distribution",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        if "risk_score" in filtered.columns:
            fig_hist = px.histogram(
                filtered, x="risk_score",
                nbins=20,
                title="Risk Score Distribution",
                color_discrete_sequence=["#89b4fa"],
                template="plotly_dark",
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)

    # ======================================================================
    # Score Scatter Plot
    # ======================================================================
    if "risk_score" in filtered.columns and len(filtered) > 0:
        st.header("🗺️ Ghost Map Visualization")

        # Create a scatter plot showing all endpoints
        fig_scatter = go.Figure()

        for level, color in [("HIGH", "#f38ba8"), ("MEDIUM", "#fab387"), ("LOW", "#a6e3a1")]:
            level_data = filtered[filtered.get("risk_level", pd.Series()) == level] if "risk_level" in filtered.columns else pd.DataFrame()
            if not level_data.empty:
                urls = level_data.get("url", level_data.get("normalized_url", pd.Series([""] * len(level_data))))
                # Shorten URLs for display
                short_urls = urls.apply(lambda x: x[-50:] if isinstance(x, str) and len(x) > 50 else x)

                fig_scatter.add_trace(go.Scatter(
                    x=list(range(len(level_data))),
                    y=level_data["risk_score"],
                    mode="markers",
                    name=f"{level} Risk",
                    text=short_urls,
                    marker=dict(
                        color=color,
                        size=level_data["risk_score"] / 8 + 5,
                        opacity=0.7,
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate="<b>%{text}</b><br>Risk Score: %{y}<extra></extra>",
                ))

        fig_scatter.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_title="Endpoint Index",
            yaxis_title="Risk Score",
            showlegend=True,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ======================================================================
    # Endpoint Table
    # ======================================================================
    st.header("📋 Endpoint Details")

    # Select columns to display
    display_cols = ["url", "risk_score", "risk_level"]
    if "is_ghost" in filtered.columns:
        display_cols.append("is_ghost")
    if "is_documented" in filtered.columns:
        display_cols.append("is_documented")
    if "sources" in filtered.columns:
        display_cols.append("sources")
    if "probe_status" in filtered.columns:
        display_cols.append("probe_status")

    available_cols = [c for c in display_cols if c in filtered.columns]

    if available_cols:
        # Color code by risk level
        def highlight_risk(row):
            if "risk_level" not in row.index:
                return [""] * len(row)
            level = row.get("risk_level", "")
            if level == "HIGH":
                return [f"background-color: rgba(243, 139, 168, 0.2)"] * len(row)
            elif level == "MEDIUM":
                return [f"background-color: rgba(250, 179, 135, 0.2)"] * len(row)
            return [""] * len(row)

        styled_df = filtered[available_cols].style.apply(highlight_risk, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=500)
    else:
        st.dataframe(filtered, use_container_width=True, height=500)

    # ======================================================================
    # Detailed View
    # ======================================================================
    st.header("🔍 Endpoint Inspector")

    if "url" in filtered.columns or "normalized_url" in filtered.columns:
        url_col = "url" if "url" in filtered.columns else "normalized_url"
        selected_url = st.selectbox(
            "Select an endpoint to inspect:",
            options=filtered[url_col].tolist(),
        )

        if selected_url:
            selected = filtered[filtered[url_col] == selected_url].iloc[0].to_dict()

            col_detail1, col_detail2 = st.columns(2)

            with col_detail1:
                st.subheader("📄 Endpoint Info")
                st.json({
                    "URL": selected.get("url", ""),
                    "Risk Score": selected.get("risk_score", "N/A"),
                    "Risk Level": selected.get("risk_level", "N/A"),
                    "Is Ghost": selected.get("is_ghost", "N/A"),
                    "Is Documented": selected.get("is_documented", "N/A"),
                    "Sources": selected.get("sources", []),
                    "Occurrence Count": selected.get("occurrence_count", 1),
                })

            with col_detail2:
                st.subheader("⚠️ Risk Factors")
                factors = selected.get("risk_factors", [])
                if factors:
                    for f in factors:
                        if isinstance(f, dict):
                            emoji = "🔴" if f.get("points", 0) >= 20 else "🟡" if f.get("points", 0) >= 10 else "🟢"
                            st.write(f"{emoji} **{f.get('factor', '')}** (+{f.get('points', 0)} pts)")
                            st.caption(f.get("detail", ""))
                else:
                    st.info("No specific risk factors identified.")

    # Footer
    st.markdown("---")
    st.markdown(
        f"👻 **GHOSTMAP** v{meta.get('version', '1.0.0')} | "
        f"Generated: {meta.get('timestamp', 'N/A')} | "
        f"Total: {len(endpoints)} endpoints"
    )


if __name__ == "__main__":
    main()
