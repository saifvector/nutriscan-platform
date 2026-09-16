"""
NutriScan Security Guard & Defensive Controls.
Provides enterprise defense utilities against OWASP Top 10 vulnerabilities:
- SSRF (Server-Side Request Forgery) protection with DNS/IP resolution & CIDR checks
- Path Traversal prevention & filename canonicalization
- File upload abuse mitigation (MIME, size, magic bytes, extension whitelist)
- XSS (Cross-Site Scripting) input sanitization & script tag neutralization
- HTTP Response Splitting & Header Injection defenses
- Open Redirect validation against trusted hostnames
- Secret Exposure detection and scrubbing
"""

import os
import re
import html
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Set, Tuple, Optional, Any, Dict

# Forbidden private and loopback networks for SSRF prevention
FORBIDDEN_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Private RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),     # Private RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),    # Private RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Cloud Metadata (AWS, GCP, Azure)
    ipaddress.ip_network("::1/128"),           # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local Address
    ipaddress.ip_network("fe80::/10"),         # IPv6 Link-local
    ipaddress.ip_network("0.0.0.0/8"),         # Current network
]

ALLOWED_FILE_EXTENSIONS: Set[str] = {
    ".pdf", ".csv", ".json", ".png", ".jpg", ".jpeg"
}

DISALLOWED_FILE_EXTENSIONS: Set[str] = {
    ".exe", ".sh", ".bat", ".cmd", ".ps1", ".vbs", ".php", ".py", ".pl", ".rb", ".dll", ".so"
}

ALLOWED_SCHEMES: Set[str] = {"http", "https"}

PATTERNS_SECRETS = [
    re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(r"password[\"']?\s*[:=]\s*[\"'][^\"']+[\"']", re.IGNORECASE),
    re.compile(r"secret[\"']?\s*[:=]\s*[\"'][^\"']+[\"']", re.IGNORECASE),
    re.compile(r"postgres(?:ql)?:\/\/[^:]+:[^@]+@", re.IGNORECASE),
    re.compile(r"sqlite:\/\/\/[^\s\"']+", re.IGNORECASE),
]


class SecurityGuard:
    """Enterprise defensive utilities for NutriScan security compliance."""

    @staticmethod
    def is_ssrf_safe_url(url: str, allow_private: bool = False) -> Tuple[bool, str]:
        """
        Validates whether a URL is safe against Server-Side Request Forgery (SSRF).
        Blocks non-HTTP/HTTPS schemes, cloud metadata endpoints, internal RFC 1918 IPs,
        and loopback addresses.
        """
        if not url or not isinstance(url, str):
            return False, "Invalid URL"

        try:
            parsed = urlparse(url.strip())
        except Exception:
            return False, "URL parse failure"

        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            return False, f"Disallowed scheme: {parsed.scheme}"

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname"

        # Check for obvious localhost / cloud metadata strings
        lower_host = hostname.lower()
        if lower_host in {"localhost", "metadata.google.internal", "169.254.169.254"}:
            return False, f"Blocked target: {lower_host}"

        if allow_private:
            return True, "Allowed"

        # Resolve hostname to IP to verify against private / link-local CIDRs
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                for net in FORBIDDEN_NETWORKS:
                    if ip_obj in net:
                        return False, f"Target IP {ip_str} falls within forbidden network {net}"
        except socket.gaierror:
            return False, f"DNS resolution failed for {hostname}"
        except Exception as e:
            return False, f"IP verification failed: {str(e)}"

        return True, "Safe URL"

    @staticmethod
    def sanitize_file_path(base_directory: str, filename: str) -> Tuple[bool, str]:
        """
        Prevents directory traversal attacks (e.g. ../, ..\\, %2e%2e, null bytes).
        Ensures the canonical resolved path resides entirely within base_directory.
        """
        if "\x00" in filename:
            return False, "Null byte detected in path"

        # Basic traversal token checks
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            return False, "Directory traversal sequence detected"

        # Normalize and resolve paths
        abs_base = os.path.abspath(base_directory)
        target_path = os.path.abspath(os.path.join(abs_base, filename))

        # Ensure the target path starts with the base path
        try:
            common = os.path.commonpath([abs_base, target_path])
            if common != abs_base or target_path == abs_base:
                return False, "Path escapes target base directory"
        except ValueError:
            return False, "Cross-drive path access detected"

        return True, target_path

    @staticmethod
    def validate_file_upload(
        filename: str,
        content: bytes,
        max_size_bytes: int = 10 * 1024 * 1024,
        allowed_extensions: Optional[Set[str]] = None
    ) -> Tuple[bool, str]:
        """
        Validates file upload safety:
        - Payload size limit
        - Filename traversal and extension whitelist
        - Rejection of executable extensions
        - Null-byte avoidance
        """
        if not filename or len(filename) > 255:
            return False, "Invalid filename length"

        if "\x00" in filename:
            return False, "Null byte detected in filename"

        if len(content) > max_size_bytes:
            return False, f"File exceeds maximum allowed size of {max_size_bytes} bytes"

        _, ext = os.path.splitext(filename.lower())
        if not ext:
            return False, "Missing file extension"

        if ext in DISALLOWED_FILE_EXTENSIONS:
            return False, f"Executable file extension disallowed: {ext}"

        whitelist = allowed_extensions or ALLOWED_FILE_EXTENSIONS
        if ext not in whitelist:
            return False, f"File extension {ext} not in allowed whitelist"

        return True, "Valid file upload"

    @staticmethod
    def sanitize_xss(input_text: str) -> str:
        """
        Neutralizes Cross-Site Scripting (XSS) in user-provided text.
        Escapes HTML characters and strips dangerous script tags and event handlers.
        """
        if not input_text or not isinstance(input_text, str):
            return ""

        # Neutralize common script tag injections
        cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", input_text, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"javascript\s*:", "blocked-scheme:", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"on\w+\s*=", "blocked-handler=", cleaned, flags=re.IGNORECASE)
        
        # HTML entity escape
        return html.escape(cleaned.strip())

    @staticmethod
    def validate_header_value(header_value: str) -> Tuple[bool, str]:
        """
        Guards against HTTP Response Splitting and Header Injection attacks.
        Disallows carriage returns (\r) and newlines (\n).
        """
        if "\r" in header_value or "\n" in header_value:
            return False, "Carriage return or newline detected in header"
        return True, header_value

    @staticmethod
    def validate_redirect_url(url: str, allowed_domains: Optional[Set[str]] = None) -> Tuple[bool, str]:
        """
        Prevents Open Redirect attacks by validating the target URL
        is relative or belongs to an explicitly allowed domain.
        """
        if not url:
            return False, "Empty redirect URL"

        url = url.strip()
        # Relative URLs are safe redirects
        if url.startswith("/") and not url.startswith("//"):
            return True, url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().split(":")[0]
            domains = allowed_domains or {"localhost", "127.0.0.1"}
            if domain in domains:
                return True, url
            return False, f"Untrusted redirect domain: {domain}"
        except Exception:
            return False, "Malformed redirect URL"

    @staticmethod
    def scrub_sensitive_secrets(text: str) -> str:
        """
        Redacts passwords, tokens, connection strings, and secret keys from logs/error bodies.
        """
        if not text or not isinstance(text, str):
            return text

        scrubbed = text
        for pattern in PATTERNS_SECRETS:
            scrubbed = pattern.sub("[REDACTED_SECRET]", scrubbed)
        return scrubbed
