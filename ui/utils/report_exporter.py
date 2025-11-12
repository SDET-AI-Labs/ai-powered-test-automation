"""
Report Exporter - Generate HTML/PDF reports for visual regression testing

This module provides utilities to export visual diff analysis results
into shareable HTML and PDF formats.

Author: Ram
Phase: 5 - Vision Dashboard & Visual Diff UI Reports
"""

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO
from PIL import Image


def image_to_base64(image_path: str) -> str:
    """
    Convert image file to base64 string for embedding in HTML.
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        str: Base64 encoded image string
    """
    try:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.getvalue()).decode()
    except Exception:
        # If file read fails, try PIL
        try:
            img = Image.open(image_path)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            return ""


def pil_image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string.
    
    Args:
        image (PIL.Image): PIL Image object
        
    Returns:
        str: Base64 encoded image string
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def generate_html_report(
    diff_data: Dict,
    llm_data: Optional[Dict] = None,
    baseline_path: Optional[str] = None,
    current_path: Optional[str] = None,
    diff_map_path: Optional[str] = None,
    output_path: str = "reports/vision_report.html"
) -> str:
    """
    Generate HTML report from visual diff analysis.
    
    Args:
        diff_data (dict): Diff analysis data with similarity, regions, etc.
        llm_data (dict, optional): Vision LLM analysis results
        baseline_path (str, optional): Path to baseline image
        current_path (str, optional): Path to current image
        diff_map_path (str, optional): Path to diff map image
        output_path (str): Output file path for HTML report
        
    Returns:
        str: Path to generated HTML file
    """
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert images to base64
    baseline_b64 = image_to_base64(baseline_path) if baseline_path else ""
    current_b64 = image_to_base64(current_path) if current_path else ""
    diff_b64 = image_to_base64(diff_map_path) if diff_map_path else ""
    
    # Extract data
    similarity = diff_data.get('similarity', 0)
    diff_pixels = diff_data.get('diff_pixels', 0)
    changed_regions = diff_data.get('changed_regions', [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Regression Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .metric-card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-card.success .value {{
            color: #10b981;
        }}
        
        .metric-card.warning .value {{
            color: #f59e0b;
        }}
        
        .metric-card.danger .value {{
            color: #ef4444;
        }}
        
        .images {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .image-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .image-box h3 {{
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }}
        
        .image-box img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .regions {{
            padding: 30px;
        }}
        
        .regions h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .region-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .region-table thead {{
            background: #667eea;
            color: white;
        }}
        
        .region-table th,
        .region-table td {{
            padding: 12px 15px;
            text-align: left;
        }}
        
        .region-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .region-table tbody tr:hover {{
            background: #e9ecef;
        }}
        
        .severity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .severity.high {{
            background: #fee2e2;
            color: #dc2626;
        }}
        
        .severity.medium {{
            background: #fed7aa;
            color: #ea580c;
        }}
        
        .severity.low {{
            background: #fef3c7;
            color: #ca8a04;
        }}
        
        .llm-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .llm-section h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .llm-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .llm-box h3 {{
            font-size: 16px;
            margin-bottom: 10px;
            color: #667eea;
        }}
        
        .llm-box p {{
            line-height: 1.6;
            color: #555;
        }}
        
        .llm-box ul {{
            margin-top: 10px;
            margin-left: 20px;
        }}
        
        .llm-box li {{
            margin: 5px 0;
            color: #555;
        }}
        
        footer {{
            padding: 20px 30px;
            background: #f8f9fa;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>👁️ Visual Regression Report</h1>
            <p>Generated on {timestamp}</p>
        </header>
        
        <div class="metrics">
            <div class="metric-card {'success' if similarity >= 0.95 else 'warning' if similarity >= 0.85 else 'danger'}">
                <h3>Similarity</h3>
                <div class="value">{similarity:.2%}</div>
            </div>
            
            <div class="metric-card">
                <h3>Changed Pixels</h3>
                <div class="value">{diff_pixels:,}</div>
            </div>
            
            <div class="metric-card">
                <h3>Changed Regions</h3>
                <div class="value">{len(changed_regions)}</div>
            </div>
            
            <div class="metric-card {'success' if len(changed_regions) == 0 else 'warning'}">
                <h3>Status</h3>
                <div class="value">{'✓' if len(changed_regions) == 0 else '⚠'}</div>
            </div>
        </div>
"""
    
    # Images section
    if baseline_b64 or current_b64 or diff_b64:
        html_content += """
        <div class="images">
"""
        if baseline_b64:
            html_content += f"""
            <div class="image-box">
                <h3>📸 Baseline</h3>
                <img src="data:image/png;base64,{baseline_b64}" alt="Baseline">
            </div>
"""
        
        if current_b64:
            html_content += f"""
            <div class="image-box">
                <h3>📸 Current</h3>
                <img src="data:image/png;base64,{current_b64}" alt="Current">
            </div>
"""
        
        if diff_b64:
            html_content += f"""
            <div class="image-box">
                <h3>🔍 Diff Map</h3>
                <img src="data:image/png;base64,{diff_b64}" alt="Diff Map">
            </div>
"""
        
        html_content += """
        </div>
"""
    
    # Changed regions table
    if changed_regions:
        html_content += """
        <div class="regions">
            <h2>⚠️ Changed Regions</h2>
            <table class="region-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Region</th>
                        <th>Position (x, y)</th>
                        <th>Size (w × h)</th>
                        <th>Severity</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for i, region in enumerate(changed_regions, 1):
            bbox = region.get('bbox', [0, 0, 0, 0])
            severity = region.get('severity', 'medium')
            region_name = region.get('region', f'Region {i}')
            
            html_content += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{region_name}</td>
                        <td>({bbox[0]}, {bbox[1]})</td>
                        <td>{bbox[2]} × {bbox[3]} px</td>
                        <td><span class="severity {severity}">{severity}</span></td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
    
    # LLM Analysis section
    if llm_data:
        html_content += """
        <div class="llm-section">
            <h2>🤖 AI Vision Analysis</h2>
"""
        
        if llm_data.get('description'):
            html_content += f"""
            <div class="llm-box">
                <h3>Description</h3>
                <p>{llm_data['description']}</p>
            </div>
            <br>
"""
        
        if llm_data.get('elements'):
            elements_list = ''.join([f'<li>{elem}</li>' for elem in llm_data['elements']])
            html_content += f"""
            <div class="llm-box">
                <h3>Changed Elements</h3>
                <ul>
                    {elements_list}
                </ul>
            </div>
            <br>
"""
        
        if llm_data.get('action'):
            html_content += f"""
            <div class="llm-box">
                <h3>Suggested Action</h3>
                <p>{llm_data['action']}</p>
            </div>
"""
        
        html_content += """
        </div>
"""
    
    # Footer
    html_content += """
        <footer>
            <p>Generated by Vision Dashboard - AI Test Automation Framework</p>
            <p>© 2025 SDET-AI-Labs | Powered by Vision LLM</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(output_file)


def export_visual_report(
    diff_data: Dict,
    llm_data: Optional[Dict] = None,
    baseline_path: Optional[str] = None,
    current_path: Optional[str] = None,
    diff_map_path: Optional[str] = None,
    output_path: str = "reports/vision_report.html",
    format: str = "html"
) -> str:
    """
    Export visual diff analysis to HTML or PDF report.
    
    Args:
        diff_data (dict): Diff analysis data
        llm_data (dict, optional): Vision LLM analysis
        baseline_path (str, optional): Baseline image path
        current_path (str, optional): Current image path
        diff_map_path (str, optional): Diff map image path
        output_path (str): Output file path
        format (str): Export format ('html' or 'pdf')
        
    Returns:
        str: Path to generated report file
        
    Example:
        >>> diff_data = {
        ...     'similarity': 0.92,
        ...     'diff_pixels': 1234,
        ...     'changed_regions': [
        ...         {'bbox': [100, 50, 200, 100], 'severity': 'medium'}
        ...     ]
        ... }
        >>> report_path = export_visual_report(
        ...     diff_data,
        ...     baseline_path='baseline.png',
        ...     current_path='current.png'
        ... )
        >>> print(f"Report saved to: {report_path}")
    """
    if format.lower() == 'html':
        return generate_html_report(
            diff_data,
            llm_data,
            baseline_path,
            current_path,
            diff_map_path,
            output_path
        )
    elif format.lower() == 'pdf':
        # Generate HTML first
        html_path = output_path.replace('.pdf', '.html')
        html_file = generate_html_report(
            diff_data,
            llm_data,
            baseline_path,
            current_path,
            diff_map_path,
            html_path
        )
        
        # Try to convert to PDF using pdfkit (requires wkhtmltopdf)
        try:
            import pdfkit
            pdfkit.from_file(html_file, output_path)
            return output_path
        except ImportError:
            print("Warning: pdfkit not installed. Install with: pip install pdfkit")
            print("Also install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
            return html_file
        except Exception as e:
            print(f"Warning: PDF conversion failed: {e}")
            print(f"HTML report available at: {html_file}")
            return html_file
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'html' or 'pdf'")
