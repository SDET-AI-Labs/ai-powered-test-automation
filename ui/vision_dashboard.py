"""
Vision Dashboard - Interactive UI for Visual Regression Testing

This Streamlit app provides:
- Side-by-side baseline vs current screenshot comparison
- Visual diff region overlays
- Vision LLM analysis display
- Historical data from logs
- HTML/PDF report exports

Author: Ram
Phase: 5 - Vision Dashboard & Visual Diff UI Reports
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import sys
import base64
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vision_analyzer import VisionAnalyzer

# Page configuration
st.set_page_config(
    page_title="Vision Dashboard - AI Test Automation",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
CACHE_PATH = project_root / "logs" / "vision_cache.json"
HEALING_LOG_PATH = project_root / "logs" / "healing_log.json"
REPORTS_DIR = project_root / "reports"

# Ensure reports directory exists
REPORTS_DIR.mkdir(exist_ok=True)

# Initialize session state
if 'vision_analyzer' not in st.session_state:
    st.session_state.vision_analyzer = None
if 'current_diff' not in st.session_state:
    st.session_state.current_diff = None
if 'cached_runs' not in st.session_state:
    st.session_state.cached_runs = []
if 'healing_logs' not in st.session_state:
    st.session_state.healing_logs = []


def load_vision_cache():
    """Load cached vision analysis runs."""
    if CACHE_PATH.exists():
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)
    return {}


def load_healing_logs():
    """Load healing logs with vision source."""
    if HEALING_LOG_PATH.exists():
        with open(HEALING_LOG_PATH, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            # Handle both single object and array formats
            try:
                logs = json.loads(content)
                if isinstance(logs, dict):
                    return [logs]
                return logs
            except json.JSONDecodeError:
                # Handle line-by-line JSON format
                logs = []
                for line in content.split('\n'):
                    if line.strip():
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                return logs
    return []


def calculate_metrics(cache_data, healing_logs):
    """Calculate dashboard metrics."""
    # Cache hit rate
    total_entries = len(cache_data)
    
    # Vision usage from healing logs
    vision_healings = [log for log in healing_logs if log.get('healing_source') == 'vision']
    vision_usage = len(vision_healings)
    total_healings = len(healing_logs)
    
    # Average similarity from cache
    similarities = []
    for entry in cache_data.values():
        if 'similarity' in entry:
            similarities.append(entry['similarity'])
    
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
    
    return {
        'cache_entries': total_entries,
        'vision_usage': vision_usage,
        'total_healings': total_healings,
        'vision_percentage': (vision_usage / total_healings * 100) if total_healings > 0 else 0,
        'avg_similarity': avg_similarity
    }


def draw_diff_overlay(image, regions):
    """Draw bounding boxes on image for changed regions."""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    for region in regions:
        # Expected format: {"bbox": [x, y, width, height], "severity": "high|medium|low"}
        if 'bbox' in region:
            bbox = region['bbox']
            x, y, w, h = bbox
            severity = region.get('severity', 'medium')
            
            # Color based on severity
            color_map = {
                'high': 'red',
                'medium': 'orange',
                'low': 'yellow'
            }
            color = color_map.get(severity, 'orange')
            
            # Draw rectangle
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
            
            # Draw severity label
            label = f"{severity.upper()}"
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Background for text
            text_bbox = draw.textbbox((x, y - 20), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text((x, y - 20), label, fill='white', font=font)
    
    return img


def image_to_base64(image):
    """Convert PIL Image to base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def render_sidebar():
    """Render sidebar with navigation and settings."""
    st.sidebar.title("👁️ Vision Dashboard")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📊 Compare Images", "📜 History", "🔧 Healing Logs", "📈 Metrics"]
    )
    
    st.sidebar.markdown("---")
    
    # Settings
    st.sidebar.subheader("⚙️ Settings")
    provider = st.sidebar.selectbox(
        "Vision Provider",
        ["gemini", "openai", "openrouter"],
        index=0
    )
    
    threshold = st.sidebar.slider(
        "Anomaly Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.01,
        help="Similarity threshold for detecting anomalies (lower = more sensitive)"
    )
    
    st.sidebar.markdown("---")
    
    # Cache management
    st.sidebar.subheader("🗄️ Cache Management")
    cache_data = load_vision_cache()
    st.sidebar.info(f"Cache entries: {len(cache_data)}")
    
    if st.sidebar.button("Clear Cache"):
        if st.session_state.vision_analyzer:
            st.session_state.vision_analyzer.clear_cache()
            st.sidebar.success("Cache cleared!")
            st.rerun()
    
    return page, provider, threshold


def render_home():
    """Render home page."""
    st.title("👁️ Vision Dashboard")
    st.markdown("### AI-Powered Visual Regression Testing")
    
    st.markdown("""
    Welcome to the Vision Dashboard! This tool helps you:
    
    - 🔍 **Compare Screenshots**: Upload baseline and current images to detect visual differences
    - 🤖 **AI Analysis**: Use Vision LLM (Gemini/GPT-4V) to analyze changes
    - 📊 **Visual Overlays**: See exactly where changes occurred with bounding boxes
    - 📜 **History Tracking**: Review past analyses from cache
    - 🔧 **Healing Integration**: View visual healing logs from AIHealer
    - 📈 **Metrics Dashboard**: Track cache performance and vision usage
    """)
    
    st.markdown("---")
    
    # Quick stats
    cache_data = load_vision_cache()
    healing_logs = load_healing_logs()
    metrics = calculate_metrics(cache_data, healing_logs)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cache Entries", metrics['cache_entries'])
    
    with col2:
        st.metric("Vision Healings", metrics['vision_usage'])
    
    with col3:
        st.metric("Vision Usage", f"{metrics['vision_percentage']:.1f}%")
    
    with col4:
        st.metric("Avg Similarity", f"{metrics['avg_similarity']:.2%}")
    
    st.markdown("---")
    
    st.info("👈 Use the sidebar to navigate to different sections")


def render_compare_images(provider, threshold):
    """Render image comparison page."""
    st.title("📊 Compare Images")
    st.markdown("Upload baseline and current screenshots to detect visual differences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 Baseline Image")
        baseline_file = st.file_uploader(
            "Upload baseline screenshot",
            type=['png', 'jpg', 'jpeg'],
            key='baseline'
        )
        
        if baseline_file:
            baseline_img = Image.open(baseline_file)
            st.image(baseline_img, use_container_width=True)
    
    with col2:
        st.subheader("📸 Current Image")
        current_file = st.file_uploader(
            "Upload current screenshot",
            type=['png', 'jpg', 'jpeg'],
            key='current'
        )
        
        if current_file:
            current_img = Image.open(current_file)
            st.image(current_img, use_container_width=True)
    
    # Analysis section
    if baseline_file and current_file:
        st.markdown("---")
        
        col_analyze, col_llm = st.columns(2)
        
        with col_analyze:
            analyze_btn = st.button("🔍 Analyze Differences", type="primary", use_container_width=True)
        
        with col_llm:
            use_llm = st.checkbox("Use Vision LLM Analysis", value=False)
        
        if analyze_btn:
            with st.spinner("Analyzing images..."):
                # Save temporary images
                temp_dir = project_root / "logs" / "temp"
                temp_dir.mkdir(exist_ok=True)
                
                baseline_path = temp_dir / "baseline_temp.png"
                current_path = temp_dir / "current_temp.png"
                
                baseline_img.save(baseline_path)
                current_img.save(current_path)
                
                # Initialize analyzer
                if not st.session_state.vision_analyzer:
                    st.session_state.vision_analyzer = VisionAnalyzer(
                        provider=provider,
                        cache_dir=str(project_root / "logs")
                    )
                
                # Compare images
                diff_result = st.session_state.vision_analyzer.compare_images(
                    str(baseline_path),
                    str(current_path),
                    save_diff=True
                )
                
                st.session_state.current_diff = diff_result
                
                # Detect anomalies
                anomalies = st.session_state.vision_analyzer.detect_visual_anomalies(
                    str(baseline_path),
                    str(current_path),
                    threshold=threshold
                )
                
                st.success("✅ Analysis complete!")
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Analysis Results")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Similarity",
                        f"{diff_result['similarity']:.2%}",
                        delta=f"{(diff_result['similarity'] - threshold):.2%}"
                    )
                
                with col2:
                    st.metric("Changed Pixels", f"{diff_result['diff_pixels']:,}")
                
                with col3:
                    st.metric("Changed Regions", len(diff_result.get('changed_regions', [])))
                
                with col4:
                    st.metric("Anomalies Detected", len(anomalies))
                
                # Visual diff overlay
                if diff_result.get('changed_regions'):
                    st.markdown("---")
                    st.subheader("🎯 Visual Diff Overlay")
                    
                    col_base, col_curr, col_diff = st.columns(3)
                    
                    with col_base:
                        st.markdown("**Baseline**")
                        baseline_overlay = draw_diff_overlay(
                            baseline_img,
                            diff_result['changed_regions']
                        )
                        st.image(baseline_overlay, use_container_width=True)
                    
                    with col_curr:
                        st.markdown("**Current**")
                        current_overlay = draw_diff_overlay(
                            current_img,
                            diff_result['changed_regions']
                        )
                        st.image(current_overlay, use_container_width=True)
                    
                    with col_diff:
                        st.markdown("**Diff Map**")
                        if diff_result.get('diff_map_path') and Path(diff_result['diff_map_path']).exists():
                            diff_img = Image.open(diff_result['diff_map_path'])
                            st.image(diff_img, use_container_width=True)
                
                # Anomalies table
                if anomalies:
                    st.markdown("---")
                    st.subheader("⚠️ Detected Anomalies")
                    
                    for i, anomaly in enumerate(anomalies, 1):
                        with st.expander(f"Anomaly #{i} - {anomaly.get('severity', 'unknown').upper()} severity"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Region:**", anomaly.get('region', 'N/A'))
                                st.write("**Severity:**", anomaly.get('severity', 'N/A'))
                            
                            with col2:
                                bbox = anomaly.get('bbox', [])
                                if bbox:
                                    st.write("**Position:**", f"({bbox[0]}, {bbox[1]})")
                                    st.write("**Size:**", f"{bbox[2]}x{bbox[3]} px")
                
                # LLM Analysis
                if use_llm and diff_result.get('diff_map_path'):
                    st.markdown("---")
                    st.subheader("🤖 Vision LLM Analysis")
                    
                    with st.spinner("Asking Vision LLM..."):
                        llm_result = st.session_state.vision_analyzer.analyze_with_llm(
                            diff_result['diff_map_path'],
                            prompt="Describe the visual differences between these images. Focus on UI elements that changed.",
                            use_cache=True
                        )
                        
                        if llm_result.get('description'):
                            st.info(f"**AI Description:** {llm_result['description']}")
                        
                        if llm_result.get('elements'):
                            st.write("**Changed Elements:**")
                            for element in llm_result['elements']:
                                st.write(f"- {element}")
                        
                        if llm_result.get('action'):
                            st.success(f"**Suggested Action:** {llm_result['action']}")


def render_history():
    """Render history page with cached runs."""
    st.title("📜 Analysis History")
    st.markdown("Review past vision analyses from cache")
    
    cache_data = load_vision_cache()
    
    if not cache_data:
        st.info("No cached analyses found. Run some image comparisons first!")
        return
    
    st.write(f"Total cached entries: **{len(cache_data)}**")
    st.markdown("---")
    
    # Convert to list for display
    cache_list = []
    for key, value in cache_data.items():
        entry = value.copy()
        entry['cache_key'] = key
        cache_list.append(entry)
    
    # Sort by timestamp if available
    cache_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Display entries
    for i, entry in enumerate(cache_list, 1):
        with st.expander(f"Entry #{i} - Similarity: {entry.get('similarity', 0):.2%}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Cache Key:**", entry.get('cache_key', 'N/A')[:50] + "...")
                st.write("**Timestamp:**", entry.get('timestamp', 'N/A'))
                st.write("**Similarity:**", f"{entry.get('similarity', 0):.2%}")
            
            with col2:
                st.write("**Diff Pixels:**", entry.get('diff_pixels', 'N/A'))
                st.write("**Changed Regions:**", len(entry.get('changed_regions', [])))
            
            if entry.get('description'):
                st.markdown("**AI Description:**")
                st.info(entry['description'])


def render_healing_logs():
    """Render healing logs page."""
    st.title("🔧 Healing Logs")
    st.markdown("View healing events that used vision analysis")
    
    healing_logs = load_healing_logs()
    
    if not healing_logs:
        st.info("No healing logs found. Run some tests with AIHealer first!")
        return
    
    # Filter for vision-based healings
    vision_logs = [log for log in healing_logs if log.get('healing_source') == 'vision']
    
    st.write(f"Total healing events: **{len(healing_logs)}**")
    st.write(f"Vision-based healings: **{len(vision_logs)}**")
    
    if vision_logs:
        st.markdown("---")
        
        for i, log in enumerate(vision_logs, 1):
            with st.expander(f"Healing #{i} - {log.get('timestamp', 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Old Locator:**", log.get('old_locator', 'N/A'))
                    st.write("**New Locator:**", log.get('new_locator', 'N/A'))
                    st.write("**Source:**", log.get('healing_source', 'N/A'))
                
                with col2:
                    st.write("**Timestamp:**", log.get('timestamp', 'N/A'))
                    st.write("**Latency:**", f"{log.get('latency_ms', 0)}ms")
                    if 'confidence' in log:
                        st.write("**Confidence:**", f"{log['confidence']:.2%}")
                
                if log.get('region'):
                    st.write("**Region:**", log['region'])
                
                if log.get('description'):
                    st.markdown("**Description:**")
                    st.info(log['description'])


def render_metrics():
    """Render metrics dashboard."""
    st.title("📈 Metrics Dashboard")
    st.markdown("Performance and usage statistics")
    
    cache_data = load_vision_cache()
    healing_logs = load_healing_logs()
    metrics = calculate_metrics(cache_data, healing_logs)
    
    # Overall metrics
    st.subheader("📊 Overall Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cache Entries", metrics['cache_entries'])
    
    with col2:
        st.metric("Total Healings", metrics['total_healings'])
    
    with col3:
        st.metric("Vision Healings", metrics['vision_usage'])
    
    with col4:
        st.metric("Vision Usage", f"{metrics['vision_percentage']:.1f}%")
    
    st.markdown("---")
    
    # Similarity distribution
    st.subheader("📊 Similarity Distribution")
    
    similarities = []
    for entry in cache_data.values():
        if 'similarity' in entry:
            similarities.append(entry['similarity'])
    
    if similarities:
        import pandas as pd
        
        df = pd.DataFrame({
            'Similarity': similarities
        })
        
        st.bar_chart(df['Similarity'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average", f"{metrics['avg_similarity']:.2%}")
        
        with col2:
            st.metric("Minimum", f"{min(similarities):.2%}")
        
        with col3:
            st.metric("Maximum", f"{max(similarities):.2%}")
    else:
        st.info("No similarity data available yet")
    
    st.markdown("---")
    
    # Cache statistics
    if st.session_state.vision_analyzer:
        st.subheader("🗄️ Cache Statistics")
        
        cache_stats = st.session_state.vision_analyzer.get_cache_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Entries", cache_stats.get('total_entries', 0))
            st.metric("Total Calls", cache_stats.get('total_calls', 0))
        
        with col2:
            st.metric("Cache Hits", cache_stats.get('cache_hits', 0))
            hit_rate = cache_stats.get('hit_rate', 0)
            st.metric("Hit Rate", f"{hit_rate:.1%}")


def main():
    """Main application entry point."""
    # Render sidebar and get settings
    page, provider, threshold = render_sidebar()
    
    # Route to appropriate page
    if page == "🏠 Home":
        render_home()
    elif page == "📊 Compare Images":
        render_compare_images(provider, threshold)
    elif page == "📜 History":
        render_history()
    elif page == "🔧 Healing Logs":
        render_healing_logs()
    elif page == "📈 Metrics":
        render_metrics()


if __name__ == "__main__":
    main()
