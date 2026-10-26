import pytest
from services.page_ingestion_service import PageIngestionService, PageIngestionError


def test_ssrf_rejects_private_and_local_ips():
    """Verify SSRF protection rejects private, loopback, and metadata service IP addresses."""
    disallowed_urls = [
        "http://127.0.0.1/admin",
        "http://localhost:8000/internal",
        "http://10.0.0.1/secret",
        "http://192.168.1.1/router",
        "http://172.16.0.1/config",
        "http://169.254.169.254/latest/meta-data/",  # Cloud metadata IP
        "ftp://example.com/file.txt",
        "file:///etc/passwd",
    ]

    for url in disallowed_urls:
        with pytest.raises(PageIngestionError):
            PageIngestionService.validate_url_security(url)


def test_ssrf_allows_valid_public_schemes():
    """Verify that public HTTP/HTTPS URLs pass SSRF validation without error."""
    valid_urls = [
        "https://example.com",
        "https://demo.intentflow.ai/pricing",
    ]
    for url in valid_urls:
        # Should not raise PageIngestionError
        PageIngestionService.validate_url_security(url)


def test_page_elements_extraction():
    """Verify structured parsing of title, meta description, headings, value prop, benefits, and CTAs."""
    sample_html = """<!DOCTYPE html>
    <html>
    <head>
        <title>SaaS Product — High Velocity Marketing</title>
        <meta name="description" content="AI platform that boosts conversion rates by 35% on landing pages.">
    </head>
    <body>
        <h1>Transform Your Landing Pages With AI</h1>
        <p>Personalize every visitor touchpoint in real-time with automated experiments.</p>
        <a href="/trial">Start Free Trial</a>
        <button>Book Enterprise Demo</button>
        <ul>
            <li>Real-time visitor intent classification</li>
            <li>Zero-latency edge CDN variant rendering</li>
            <li>SOC-2 Type II enterprise security compliance</li>
        </ul>
    </body>
    </html>"""

    result = PageIngestionService.extract_page_elements(sample_html, source_url="https://example.com")

    assert result["title"] == "SaaS Product — High Velocity Marketing"
    assert "boosts conversion rates" in result["meta_description"]
    assert len(result["headings"]) >= 1
    assert result["headings"][0]["text"] == "Transform Your Landing Pages With AI"
    assert len(result["calls_to_action"]) >= 2
    assert any("Start Free Trial" in cta["text"] for cta in result["calls_to_action"])
    assert len(result["benefits"]) >= 3
    assert result["content_hash"] is not None
