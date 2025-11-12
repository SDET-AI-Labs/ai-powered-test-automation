"""
vision_analyzer.py
-------------------------------------------------
AI-powered visual comparison and visual healing.
Detects UI differences that pure DOM healing misses.

Features:
  ✅ Local image comparison (PIL + NumPy)
  ✅ Vision LLM integration (Gemini Vision / GPT-4V)
  ✅ Visual diff detection and analysis
  ✅ Cache visual analysis results
  ✅ Suggest locators from visual differences
-------------------------------------------------
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
from PIL import Image, ImageChops, ImageDraw, ImageFont
import numpy as np


class VisionAnalyzer:
    """
    AI-powered vision analyzer for visual UI testing and healing.
    
    Uses multimodal LLMs (Gemini Vision, GPT-4V) to analyze screenshots,
    detect visual anomalies, and suggest locator fixes based on visual context.
    
    Features:
        - Image comparison with diff maps
        - Visual anomaly detection above threshold
        - LLM-powered visual analysis
        - Result caching for performance
        - Locator suggestion from visual context
    
    Example:
        >>> analyzer = VisionAnalyzer(provider="gemini")
        >>> diff = analyzer.compare_images("baseline.png", "current.png")
        >>> print(f"Similarity: {diff['similarity']}")
        >>> anomalies = analyzer.detect_visual_anomalies("baseline.png", "current.png")
    """
    
    def __init__(
        self,
        provider: str = "gemini",
        cache_dir: str = "logs/vision_cache",
        ai_gateway = None
    ):
        """
        Initialize Vision Analyzer with provider and cache directory.
        
        Args:
            provider (str): Vision LLM provider ('gemini' or 'openai')
            cache_dir (str): Directory for caching visual analysis results
            ai_gateway: Optional AIGateway instance for LLM communication
            
        Example:
            >>> analyzer = VisionAnalyzer(provider="gemini", cache_dir="logs/vision_cache")
        """
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.cache_dir / "vision_cache.json"
        self.cache: Dict[str, Any] = {}
        
        # Import AIGateway if not provided
        if ai_gateway is None:
            try:
                from services.locator_repair.ai_gateway import AIGateway
                self.ai_gateway = AIGateway()
            except ImportError:
                self.ai_gateway = None
                print("[Vision] Warning: AIGateway not available, LLM analysis disabled")
        else:
            self.ai_gateway = ai_gateway
        
        # Load cache
        self._load_cache()
    
    
    def _load_cache(self) -> None:
        """Load visual analysis cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"[Vision] 📦 Loaded {len(self.cache)} cached visual analyses")
            except Exception as e:
                print(f"[Vision] ⚠️ Cache load error: {e}")
                self.cache = {}
    
    
    def _save_cache(self) -> None:
        """Persist visual analysis cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"[Vision] ⚠️ Cache save error: {e}")
    
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    
    def _encode_image_base64(self, image_path: str) -> str:
        """
        Encode image to base64 for LLM API.
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Base64-encoded image string
        """
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode image {image_path}: {e}")
    
    
    def compare_images(
        self,
        baseline_path: str,
        current_path: str,
        save_diff: bool = True
    ) -> Dict[str, Any]:
        """
        Compare two images and return visual diff data.
        
        Performs pixel-by-pixel comparison using PIL and NumPy.
        Calculates similarity score and generates diff map.
        
        Args:
            baseline_path (str): Path to baseline/expected image
            current_path (str): Path to current/actual image
            save_diff (bool): Save diff map image to cache directory
            
        Returns:
            dict: Visual diff data:
                {
                    "similarity": 0.95,  # 0.0-1.0 score
                    "diff_pixels": 1234,
                    "diff_percentage": 5.2,
                    "regions": [...],  # Changed regions
                    "diff_map_path": "logs/vision_cache/diff_12345.png"
                }
                
        Example:
            >>> diff = analyzer.compare_images("baseline.png", "current.png")
            >>> if diff["similarity"] < 0.95:
            ...     print(f"Visual change detected: {diff['diff_percentage']}%")
        """
        try:
            # Load images
            baseline = Image.open(baseline_path).convert('RGB')
            current = Image.open(current_path).convert('RGB')
            
            # Ensure same size
            if baseline.size != current.size:
                current = current.resize(baseline.size, Image.Resampling.LANCZOS)
            
            # Calculate pixel difference
            diff_img = ImageChops.difference(baseline, current)
            diff_array = np.array(diff_img)
            
            # Calculate metrics
            total_pixels = diff_array.size // 3  # RGB channels
            diff_pixels = np.count_nonzero(diff_array)
            diff_percentage = (diff_pixels / (total_pixels * 3)) * 100
            similarity = 1.0 - (diff_percentage / 100.0)
            
            # Detect changed regions (simplified bounding boxes)
            regions = self._detect_changed_regions(diff_array)
            
            # Save diff map
            diff_map_path = None
            if save_diff:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                diff_map_path = str(self.cache_dir / f"diff_{timestamp}.png")
                
                # Enhance diff for visibility
                diff_enhanced = diff_img.point(lambda x: x * 5)  # Amplify differences
                diff_enhanced.save(diff_map_path)
            
            return {
                "similarity": round(similarity, 4),
                "diff_pixels": int(diff_pixels),
                "diff_percentage": round(diff_percentage, 2),
                "regions": regions,
                "diff_map_path": diff_map_path,
                "baseline_size": baseline.size,
                "current_size": current.size,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[Vision] ❌ Image comparison failed: {e}")
            return {
                "similarity": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    
    def _detect_changed_regions(
        self,
        diff_array: np.ndarray,
        threshold: int = 30
    ) -> List[Dict[str, int]]:
        """
        Detect bounding boxes of changed regions in diff array.
        
        Args:
            diff_array (np.ndarray): NumPy array of diff image
            threshold (int): Minimum pixel difference to consider
            
        Returns:
            list: List of region dicts with x, y, width, height
        """
        # Convert to grayscale for simpler processing
        if len(diff_array.shape) == 3:
            diff_gray = np.mean(diff_array, axis=2)
        else:
            diff_gray = diff_array
        
        # Find pixels above threshold
        changed_mask = diff_gray > threshold
        
        # Find bounding box of all changes (simplified)
        rows = np.any(changed_mask, axis=1)
        cols = np.any(changed_mask, axis=0)
        
        if not rows.any() or not cols.any():
            return []
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        return [{
            "x": int(cmin),
            "y": int(rmin),
            "width": int(cmax - cmin),
            "height": int(rmax - rmin),
            "area": "full_diff"
        }]
    
    
    def detect_visual_anomalies(
        self,
        baseline_path: str,
        current_path: str,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Detect significant visual changes above similarity threshold.
        
        Compares images and returns list of anomalies if similarity
        is below threshold (i.e., images are different enough).
        
        Args:
            baseline_path (str): Path to baseline image
            current_path (str): Path to current image
            threshold (float): Similarity threshold (0.0-1.0)
                              Below this = anomaly detected
            
        Returns:
            list: List of anomaly dicts:
                [
                    {
                        "region": {"x": 100, "y": 50, "width": 200, "height": 80},
                        "severity": "high",
                        "description": "Significant visual difference detected",
                        "confidence": 0.92
                    }
                ]
                
        Example:
            >>> anomalies = analyzer.detect_visual_anomalies("baseline.png", "current.png", 0.9)
            >>> if anomalies:
            ...     print(f"Found {len(anomalies)} visual anomalies")
        """
        # Compare images
        diff = self.compare_images(baseline_path, current_path, save_diff=True)
        
        # Check if similarity is below threshold
        if diff.get("similarity", 1.0) >= threshold:
            return []  # No anomalies (images are similar enough)
        
        # Build anomaly list
        anomalies = []
        regions = diff.get("regions", [])
        
        for region in regions:
            severity = self._calculate_severity(diff["diff_percentage"])
            
            anomalies.append({
                "region": region,
                "severity": severity,
                "description": f"Visual difference detected: {diff['diff_percentage']:.1f}% pixels changed",
                "confidence": round(1.0 - diff["similarity"], 2),
                "diff_map_path": diff.get("diff_map_path"),
                "timestamp": diff["timestamp"]
            })
        
        return anomalies
    
    
    def _calculate_severity(self, diff_percentage: float) -> str:
        """Calculate anomaly severity based on diff percentage."""
        if diff_percentage > 20:
            return "critical"
        elif diff_percentage > 10:
            return "high"
        elif diff_percentage > 5:
            return "medium"
        else:
            return "low"
    
    
    def analyze_with_llm(
        self,
        image_path: str,
        prompt: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Ask Vision LLM to analyze an image and describe differences.
        
        Sends image to multimodal LLM (Gemini Vision or GPT-4V)
        via ai_gateway.ask_vision() method.
        
        Args:
            image_path (str): Path to image (diff map or screenshot)
            prompt (str): Question/prompt for LLM
            use_cache (bool): Use cached results if available
            
        Returns:
            dict: LLM analysis result:
                {
                    "description": "The submit button has moved 20px to the left...",
                    "elements_affected": ["submit_button", "cancel_button"],
                    "suggested_action": "Update locator to new position",
                    "confidence": 0.93
                }
                
        Example:
            >>> result = analyzer.analyze_with_llm("diff_map.png", 
            ...     "What UI elements changed in this screenshot?")
            >>> print(result["description"])
        """
        if not self.ai_gateway:
            return {
                "error": "AIGateway not available",
                "description": "Vision LLM analysis disabled"
            }
        
        # Check cache
        cache_key = self._get_cache_key(image_path, prompt)
        if use_cache and cache_key in self.cache:
            print(f"[Vision] ✅ Cache hit for LLM analysis")
            return self.cache[cache_key]
        
        # Default prompt if not provided
        if not prompt:
            prompt = """Analyze this screenshot and describe any UI changes or visual differences.
Focus on:
- Elements that moved or changed position
- Elements that changed size or style
- Elements that appeared or disappeared
- Any other significant visual changes

Return your analysis in a structured format."""
        
        try:
            # Check if ai_gateway has ask_vision method
            if not hasattr(self.ai_gateway, 'ask_vision'):
                # Fallback: use regular ask method with encoded image
                print("[Vision] ⚠️ ask_vision() not available, using fallback")
                img_base64 = self._encode_image_base64(image_path)
                combined_prompt = f"{prompt}\n\n[Image: {os.path.basename(image_path)}]"
                response = self.ai_gateway.ask(combined_prompt)
            else:
                # Use Vision API
                response = self.ai_gateway.ask_vision([image_path], prompt)
            
            # Parse response
            result = {
                "description": response.strip(),
                "elements_affected": self._extract_elements(response),
                "suggested_action": self._extract_action(response),
                "confidence": 0.85,  # Default confidence
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "image_path": image_path
            }
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = result
                self._save_cache()
            
            return result
            
        except Exception as e:
            print(f"[Vision] ❌ LLM analysis failed: {e}")
            return {
                "error": str(e),
                "description": "Failed to analyze image with Vision LLM"
            }
    
    
    def _extract_elements(self, llm_response: str) -> List[str]:
        """Extract element names from LLM response."""
        # Simple heuristic: look for common element keywords
        keywords = ["button", "input", "link", "text", "image", "form", "menu", "nav"]
        elements = []
        
        response_lower = llm_response.lower()
        for keyword in keywords:
            if keyword in response_lower:
                elements.append(keyword)
        
        return list(set(elements))  # Unique elements
    
    
    def _extract_action(self, llm_response: str) -> str:
        """Extract suggested action from LLM response."""
        # Look for action keywords
        if "update locator" in llm_response.lower():
            return "update_locator"
        elif "no action" in llm_response.lower() or "no change" in llm_response.lower():
            return "no_action_needed"
        else:
            return "manual_review"
    
    
    def suggest_locator_from_visuals(
        self,
        visual_diffs: List[Dict[str, Any]],
        context_hint: str = "",
        engine: str = "Playwright"
    ) -> Optional[str]:
        """
        Suggest a new locator based on visual differences.
        
        Uses visual context and LLM analysis to suggest a locator
        that might work for the visually changed element.
        
        Args:
            visual_diffs (list): List of visual anomalies from detect_visual_anomalies()
            context_hint (str): Original context hint (e.g., "Submit button")
            engine (str): Framework engine (Playwright, Selenium, etc.)
            
        Returns:
            str: Suggested locator or None if unable to suggest
            
        Example:
            >>> anomalies = analyzer.detect_visual_anomalies("baseline.png", "current.png")
            >>> if anomalies:
            ...     locator = analyzer.suggest_locator_from_visuals(anomalies, "Submit", "Playwright")
        """
        if not visual_diffs:
            return None
        
        # Get first anomaly with diff map
        primary_diff = visual_diffs[0]
        diff_map_path = primary_diff.get("diff_map_path")
        
        if not diff_map_path or not os.path.exists(diff_map_path):
            return None
        
        # Analyze with LLM
        prompt = f"""Based on this visual diff, suggest a locator for: "{context_hint}"
        
The element appears to have changed position or appearance.
Framework: {engine}

Suggest a robust locator strategy (CSS, XPath, or text-based) that would work with the changed element."""
        
        analysis = self.analyze_with_llm(diff_map_path, prompt)
        
        # Extract locator from description (heuristic)
        description = analysis.get("description", "")
        
        # Simple heuristic: look for locator patterns
        if "text=" in description or "text:" in description:
            # Text-based locator
            return f"text={context_hint}"
        elif context_hint:
            # Fallback to role-based or text locator
            if engine == "Playwright":
                return f"role=button[name='{context_hint}']"
            else:
                return f"//button[contains(text(), '{context_hint}')]"
        
        return None
    
    
    def clear_cache(self) -> None:
        """Clear visual analysis cache."""
        self.cache = {}
        self._save_cache()
        print("[Vision] 🗑️ Cache cleared")
    
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "cache_file": str(self.cache_file),
            "cache_keys": list(self.cache.keys())[:10]  # First 10 keys
        }
