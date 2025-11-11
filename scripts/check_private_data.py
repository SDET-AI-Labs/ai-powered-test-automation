"""
Security Scanner - Check for Private Data Before Git Push
===========================================================
Scans all tracked and staged files for sensitive data patterns:
- API keys (OpenAI, Groq, Gemini, OpenRouter, HuggingFace)
- Email addresses
- AWS credentials
- Private keys
- Tokens
- Passwords in plain text
- IP addresses (private ranges)
- Credit card numbers
- SSH keys

Usage:
    python scripts/check_private_data.py
    
Returns:
    Exit code 0: Safe to push (no sensitive data found)
    Exit code 1: DANGER! Sensitive data detected
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


# Patterns for sensitive data detection
SENSITIVE_PATTERNS = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48,}",
    "Groq API Key": r"gsk_[a-zA-Z0-9]{52,}",
    "Gemini API Key": r"AIzaSy[a-zA-Z0-9_-]{33,}",
    "OpenRouter API Key": r"sk-or-v1-[a-f0-9]{64,}",
    "HuggingFace Token": r"hf_[a-zA-Z0-9]{34,}",
    "Generic API Key": r"(?i)(api[_-]?key|apikey|api[_-]?secret)[\s]*[=:][\s]*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws[_-]?secret[_-]?access[_-]?key[\s]*[=:][\s]*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
    "Generic Secret": r"(?i)(secret|password|passwd|pwd)[\s]*[=:][\s]*['\"]([^'\"]{8,})['\"]",
    "Private Key": r"-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----",
    "SSH Key": r"ssh-rsa AAAA[0-9A-Za-z+/]+",
    "Bearer Token": r"(?i)bearer[\s]+[a-zA-Z0-9\-._~+/]+=*",
    "Email Address": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "Private IP": r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b",
    "Credit Card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
    "JWT Token": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9._-]{10,}",
}

# Files to always ignore (safe to have sensitive data or examples)
SAFE_FILES = {
    ".env",           # Protected by .gitignore
    ".env.local",
    ".env.development",
    ".env.production",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    "LEARNING_GUIDE.md",  # Contains examples and documentation
    "README.md",          # May contain example API keys
    "README_SECURITY.md", # Security documentation with examples
    "SECURITY_IMPLEMENTATION_COMPLETE.md",  # Summary with examples
    "check_private_data.py",  # Contains regex patterns that match itself
}

# Directories to skip
SKIP_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".vscode",
    ".idea",
}

# File extensions to check
CHECK_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".sh", ".bash",
    ".html", ".css", ".env.example",
}


def is_safe_file(file_path: Path) -> bool:
    """Check if file is in the safe list (should not be scanned)."""
    return any(file_path.match(pattern) for pattern in SAFE_FILES)


def should_skip_dir(dir_path: Path) -> bool:
    """Check if directory should be skipped."""
    return any(part in SKIP_DIRS for part in dir_path.parts)


def scan_file(file_path: Path) -> List[Tuple[str, int, str, str]]:
    """
    Scan a single file for sensitive patterns.
    
    Returns:
        List of (pattern_name, line_number, matched_text, line_content)
    """
    findings = []
    
    # Patterns to ignore (placeholders, examples, documentation)
    IGNORE_PATTERNS = [
        r"your_\w+_here",  # your_key_here, your_token_here
        r"your[-_]?\w*[-_]?key",  # your-api-key, yourkey
        r"example[_-]?\w*",  # example_key, example-token
        r"test[_-]?\w*",  # test_key, test-api
        r"demo[_-]?\w*",  # demo_key, demo-secret
        r"placeholder",
        r"xxx+",  # xxxx, xxxxxxx
        r"sk-proj-[Xx]+",  # Masked OpenAI keys in docs
        r"gsk_[Xx]+",  # Masked Groq keys
    ]
    
    def is_ignored(text: str) -> bool:
        """Check if matched text is a placeholder/example."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in IGNORE_PATTERNS)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        matched_text = match.group(0)
                        
                        # Skip if it's a placeholder/example
                        if is_ignored(matched_text):
                            continue
                        
                        # Mask the sensitive data in output
                        masked_text = matched_text[:8] + "..." + matched_text[-4:] if len(matched_text) > 12 else "***"
                        
                        findings.append((
                            pattern_name,
                            line_num,
                            masked_text,
                            line.strip()
                        ))
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}")
    
    return findings


def get_git_tracked_files(project_root: Path) -> List[Path]:
    """Get list of files tracked by git or staged for commit."""
    import subprocess
    
    try:
        # Get tracked files
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        tracked = result.stdout.strip().split('\n')
        
        # Get staged files (about to be committed)
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Combine and deduplicate
        all_files = set(tracked + staged)
        return [project_root / f for f in all_files if f]
        
    except subprocess.CalledProcessError:
        # Fallback: scan all files if git commands fail
        print("⚠️  Git commands failed, scanning all files in project...")
        return list(project_root.rglob('*'))


def main():
    """Main security scanning function."""
    project_root = Path(__file__).resolve().parents[1]
    
    print("=" * 80)
    print("🔒 SECURITY SCAN: Checking for Private/Sensitive Data")
    print("=" * 80)
    print()
    
    # Get files to scan
    all_files = get_git_tracked_files(project_root)
    files_to_scan = [
        f for f in all_files
        if f.is_file()
        and not is_safe_file(f)
        and not should_skip_dir(f)
        and f.suffix in CHECK_EXTENSIONS
    ]
    
    print(f"📁 Scanning {len(files_to_scan)} files...")
    print()
    
    total_findings = []
    files_with_issues = {}
    
    for file_path in files_to_scan:
        findings = scan_file(file_path)
        if findings:
            relative_path = file_path.relative_to(project_root)
            files_with_issues[relative_path] = findings
            total_findings.extend(findings)
    
    # Report results
    if not total_findings:
        print("✅ " + "=" * 78)
        print("✅ SAFE TO PUSH: No sensitive data detected!")
        print("✅ " + "=" * 78)
        print()
        print(f"Scanned {len(files_to_scan)} files across {len(CHECK_EXTENSIONS)} file types")
        print()
        return 0
    
    # Found sensitive data
    print("❌ " + "=" * 78)
    print("❌ DANGER! SENSITIVE DATA DETECTED - DO NOT PUSH!")
    print("❌ " + "=" * 78)
    print()
    print(f"Found {len(total_findings)} potential issue(s) in {len(files_with_issues)} file(s):")
    print()
    
    for file_path, findings in files_with_issues.items():
        print(f"📄 {file_path}")
        for pattern_name, line_num, masked_text, line_content in findings:
            print(f"   Line {line_num}: {pattern_name}")
            print(f"   └─ Matched: {masked_text}")
            print(f"   └─ Context: {line_content[:80]}...")
            print()
    
    print("=" * 80)
    print("🔧 RECOMMENDED ACTIONS:")
    print("=" * 80)
    print("1. Review each flagged file and line number above")
    print("2. Move sensitive data to .env file (protected by .gitignore)")
    print("3. Remove or mask sensitive values from tracked files")
    print("4. Use environment variables: os.getenv('API_KEY')")
    print("5. Check .gitignore includes: .env, *.key, *.pem, secrets/")
    print("6. Run this script again: python scripts/check_private_data.py")
    print()
    print("❌ BLOCKED: Please fix sensitive data issues before pushing!")
    print("=" * 80)
    print()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
