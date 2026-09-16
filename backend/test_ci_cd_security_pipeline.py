"""
CI/CD Security Pipeline Validation Tests.
Phase 5: Automated DevSecOps Pipeline Verification.

Validates:
1. Dependency CVE audit scanner operation
2. Static Application Security Testing (SAST) AST scanner on backend/app
3. Secret & Credential Leak Scanner across codebase
4. Synthetic vulnerability detection (confirming pipeline catches security defects)
5. CI/CD Gate Policy evaluation verdict logic
"""

import ast
import tempfile
import pytest

from scripts.run_security_pipeline import SecurityPipelineAuditor, SecurityASTVisitor


class TestSecurityPipelineAuditor:
    """Validates the static, dependency, and secret audit capabilities of the CI/CD pipeline."""

    def test_dependency_audit_execution(self):
        findings = SecurityPipelineAuditor.audit_dependencies("requirements.txt")
        assert isinstance(findings, list)
        # Any findings must contain check and file keys
        for f in findings:
            assert "check" in f
            assert "severity" in f

    def test_production_app_has_zero_critical_sast_findings(self):
        """Verifies backend/app contains zero eval, exec, or unvalidated deserialization calls."""
        sast_findings = SecurityPipelineAuditor.run_sast_scan("backend/app")
        critical_issues = [f for f in sast_findings if f["severity"] == "CRITICAL"]
        assert len(critical_issues) == 0, f"Discovered critical SAST vulnerabilities: {critical_issues}"

    def test_production_app_has_zero_hardcoded_secrets(self):
        """Verifies backend/app contains zero leaked AWS keys, private RSA keys, or GitHub tokens."""
        secret_findings = SecurityPipelineAuditor.run_secret_scan("backend/app")
        assert len(secret_findings) == 0, f"Discovered leaked secrets in backend/app: {secret_findings}"

    def test_sast_scanner_detects_synthetic_eval(self):
        """Validates that the AST visitor catches insecure dynamic eval() usage."""
        malicious_code = """
def execute_dynamic_calculation(expr):
    return eval(expr)
"""
        tree = ast.parse(malicious_code)
        visitor = SecurityASTVisitor("test_malicious.py")
        visitor.visit(tree)
        assert len(visitor.findings) == 1
        assert visitor.findings[0]["severity"] == "CRITICAL"
        assert visitor.findings[0]["check"] == "DANGEROUS_EVAL_EXEC"

    def test_sast_scanner_detects_synthetic_shell_true(self):
        """Validates that the AST visitor catches subprocess.run with shell=True."""
        malicious_code = """
import subprocess
def run_command(user_input):
    subprocess.run(user_input, shell=True)
"""
        tree = ast.parse(malicious_code)
        visitor = SecurityASTVisitor("test_shell.py")
        visitor.visit(tree)
        assert len(visitor.findings) == 1
        assert visitor.findings[0]["severity"] == "HIGH"
        assert visitor.findings[0]["check"] == "SUBPROCESS_SHELL_TRUE"

    def test_secret_scanner_detects_synthetic_leaked_key(self):
        """Validates that the secret scanner catches hardcoded AWS credentials."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            leak_file = os.path.join(tmpdir, "aws_config.py")
            with open(leak_file, "w", encoding="utf-8") as f:
                f.write('AWS_KEY = "AKIA1234567890ABCDEF"\n')

            findings = SecurityPipelineAuditor.run_secret_scan(tmpdir)
            assert len(findings) == 1
            assert findings[0]["severity"] == "CRITICAL"
            assert "AWS" in findings[0]["message"]

    def test_pipeline_gate_policy_evaluation(self):
        """Verifies that the overall gate evaluation returns PASSED on clean codebase."""
        summary = SecurityPipelineAuditor.evaluate_pipeline(run_tests=False)
        assert summary["critical_vulnerabilities"] == 0
        assert summary["high_severity_issues"] == 0
        assert summary["ci_pipeline_gate"] == "PASSED"
