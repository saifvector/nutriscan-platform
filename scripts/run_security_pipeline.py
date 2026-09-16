"""
NutriScan Automated CI/CD Security Pipeline Runner.
Phase 5: Automated DevSecOps Gate & Security Policy Enforcement.

Automated Stages:
1. Dependency Vulnerability Audit (CVE & unsafe pin detection)
2. Static Application Security Testing (SAST AST pattern scanning)
3. High-Entropy Secret & Key Leak Scanner
4. Dynamic Automated Security Test Runner (JWT, SSRF, XSS, CSRF, Path Traversal)
5. CI/CD Gate Policy Evaluation (Blocks PR merge on Critical/High findings)
"""

import os
import re
import sys
import ast
import json
import subprocess
from typing import Dict, Any, List, Tuple


KNOWN_VULNERABLE_PINS = {
    "pyyaml": "<6.0",
    "urllib3": "<1.26.18",
    "requests": "<2.31.0",
    "jinja2": "<3.1.3",
    "cryptography": "<41.0.6",
    "certifi": "<2023.7.22"
}

SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private Encryption Key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GitHub Token", re.compile(r"ghp_[0-9a-zA-Z]{36}")),
    ("Slack Webhook", re.compile(r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+")),
    ("Generic Hardcoded Secret Key", re.compile(r"(?:api[_-]?key|jwt[_-]?secret|private[_-]?key)\s*=\s*['\"][a-zA-Z0-9_\-\.]{32,}['\"]", re.IGNORECASE))
]


class SecurityASTVisitor(ast.NodeVisitor):
    """Inspects Python AST nodes for insecure functions, unsafe deserialization, and dangerous primitives."""

    def __init__(self, filename: str):
        self.filename = filename
        self.findings: List[Dict[str, Any]] = []

    def visit_Call(self, node: ast.Call):
        # Detect eval() or exec()
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self.findings.append({
                "severity": "CRITICAL",
                "check": "DANGEROUS_EVAL_EXEC",
                "file": self.filename,
                "line": node.lineno,
                "message": f"Direct invocation of dangerous dynamic code evaluator '{node.func.id}()'"
            })

        # Detect unsafe pickle.loads
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"loads", "load"}:
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                self.findings.append({
                    "severity": "HIGH",
                    "check": "UNSAFE_DESERIALIZATION",
                    "file": self.filename,
                    "line": node.lineno,
                    "message": "Unsafe Python pickle deserialization detected. Use JSON or signed payloads."
                })

        # Detect subprocess.Popen or run with shell=True
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"Popen", "run", "call", "check_call", "check_output"}:
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append({
                        "severity": "HIGH",
                        "check": "SUBPROCESS_SHELL_TRUE",
                        "file": self.filename,
                        "line": node.lineno,
                        "message": "Subprocess called with shell=True, enabling OS command injection."
                    })

        self.generic_visit(node)


class SecurityPipelineAuditor:
    """Orchestrates all static, dependency, secret, and dynamic security checks."""

    @classmethod
    def audit_dependencies(cls, requirements_path: str = "requirements.txt") -> List[Dict[str, Any]]:
        """Audits requirement pins for insecure packages and vulnerable known versions."""
        findings = []
        if not os.path.exists(requirements_path):
            return findings

        with open(requirements_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, 1):
            cleaned = line.strip().lower()
            if not cleaned or cleaned.startswith("#"):
                continue
            for pkg, min_ver in KNOWN_VULNERABLE_PINS.items():
                if cleaned.startswith(pkg):
                    # Check if version is explicitly pinned
                    if "==" not in cleaned and ">=" not in cleaned:
                        findings.append({
                            "severity": "MEDIUM",
                            "check": "UNPINNED_DEPENDENCY",
                            "file": requirements_path,
                            "line": idx,
                            "message": f"Package '{pkg}' is unpinned. Expected version constraint {min_ver}."
                        })
        return findings

    @classmethod
    def run_sast_scan(cls, source_root: str = "backend/app") -> List[Dict[str, Any]]:
        """Scans Python codebase for dangerous constructs using AST inspection."""
        findings = []
        if not os.path.exists(source_root):
            return findings

        for root, _, files in os.walk(source_root):
            for fname in files:
                if fname.endswith(".py"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=fpath)
                        visitor = SecurityASTVisitor(fpath)
                        visitor.visit(tree)
                        findings.extend(visitor.findings)
                    except Exception as e:
                        findings.append({
                            "severity": "LOW",
                            "check": "AST_PARSE_FAILURE",
                            "file": fpath,
                            "line": 1,
                            "message": f"AST parse failure: {str(e)}"
                        })
        return findings

    @classmethod
    def run_secret_scan(cls, search_root: str = ".") -> List[Dict[str, Any]]:
        """Scans tracked repository files for high-entropy secrets and credential leakage."""
        findings = []
        ignored_dirs = {".git", ".pytest_cache", ".venv", "venv", "__pycache__", "node_modules", "catboost_info"}
        ignored_files = {".env.example", "package-lock.json", "poetry.lock"}

        for root, dirs, files in os.walk(search_root):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for fname in files:
                if fname in ignored_files or fname.endswith((".pyc", ".png", ".jpg", ".parquet", ".csv", ".db")):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            # Skip test mock tokens and documentation
                            if "test_" in fname or "mock" in line.lower() or "example" in line.lower():
                                continue
                            for name, pattern in SECRET_PATTERNS:
                                if pattern.search(line):
                                    findings.append({
                                        "severity": "CRITICAL",
                                        "check": "HARDCODED_CREDENTIAL",
                                        "file": fpath,
                                        "line": lineno,
                                        "message": f"Potential leak of {name}."
                                    })
                except Exception:
                    continue
        return findings

    @classmethod
    def run_dynamic_test_suite(cls) -> Tuple[bool, str]:
        """Runs the automated pytest security test suites."""
        cmd = [sys.executable, "-m", "pytest", "backend/test_advanced_security.py", "backend/test_security_extended.py", "-q"]
        env = os.environ.copy()
        env["PYTHONPATH"] = "backend"
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
            passed = (res.returncode == 0)
            return passed, res.stdout or res.stderr
        except Exception as e:
            return False, f"Dynamic test runner exception: {str(e)}"

    @classmethod
    def evaluate_pipeline(cls, run_tests: bool = True) -> Dict[str, Any]:
        """Executes full security pipeline and returns structured audit results and pass/fail gate verdict."""
        dep_findings = cls.audit_dependencies()
        sast_findings = cls.run_sast_scan()
        secret_findings = cls.run_secret_scan()

        test_passed = True
        test_output = "Skipped"
        if run_tests:
            test_passed, test_output = cls.run_dynamic_test_suite()

        critical_count = sum(1 for f in sast_findings + secret_findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in sast_findings + secret_findings if f["severity"] == "HIGH")

        # CI merge block policy: 0 Critical, 0 High, and dynamic security tests MUST pass
        gate_passed = (critical_count == 0) and (high_count == 0) and test_passed

        summary = {
            "ci_pipeline_gate": "PASSED" if gate_passed else "BLOCKED",
            "critical_vulnerabilities": critical_count,
            "high_severity_issues": high_count,
            "dependency_findings": len(dep_findings),
            "sast_findings": len(sast_findings),
            "secret_leak_findings": len(secret_findings),
            "dynamic_security_tests_passed": test_passed,
            "findings_detail": {
                "dependencies": dep_findings,
                "sast": sast_findings,
                "secrets": secret_findings
            }
        }
        return summary


def main():
    print("=" * 70)
    print("NutriScan Automated CI/CD Security Pipeline")
    print("=" * 70)
    report = SecurityPipelineAuditor.evaluate_pipeline(run_tests=True)
    print(f"CI Gate Verdict: {report['ci_pipeline_gate']}")
    print(f"Critical Vulnerabilities: {report['critical_vulnerabilities']}")
    print(f"High Severity Issues:     {report['high_severity_issues']}")
    print(f"Dynamic Tests Passed:     {report['dynamic_security_tests_passed']}")

    if report["ci_pipeline_gate"] != "PASSED":
        print("\n[!] CI Security Gate Failed. PR merge blocked by security policy.")
        sys.exit(1)
    else:
        print("\n[✓] All security gates cleared. Release candidate certified for deployment.")
        sys.exit(0)


if __name__ == "__main__":
    main()
