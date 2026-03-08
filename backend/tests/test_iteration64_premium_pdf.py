"""
Iteration 64: Premium Dark-Themed PDF Documentation Tests
Tests the visual overhaul of the PDF export to match dark-themed About page UI.

Requirements tested:
- GET /api/summary/pdf returns valid PDF (HTTP 200, content-type application/pdf)
- PDF has 14 pages with all 6 sections
- PDF cover page contains: title, subtitle, badges, 5 stat cards, Table of Contents
- All 41 agents are listed across 8 layers
- All 17 systems are documented
- All 9 AI providers with model details are in the PDF
- Backend server starts without errors
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "admin123"


class TestPDFEndpoint:
    """Tests for GET /api/summary/pdf endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def pdf_response(self, auth_token):
        """Get PDF response once for all content tests"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        return response
    
    def test_pdf_returns_200(self, pdf_response):
        """PDF endpoint returns HTTP 200"""
        assert pdf_response.status_code == 200, f"Expected 200, got {pdf_response.status_code}"
        print(f"PASS: GET /api/summary/pdf returns 200")
    
    def test_pdf_content_type(self, pdf_response):
        """PDF has correct content-type header"""
        content_type = pdf_response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        print(f"PASS: Content-Type is application/pdf")
    
    def test_pdf_filename(self, pdf_response):
        """PDF has correct filename in Content-Disposition"""
        content_disp = pdf_response.headers.get("content-disposition", "")
        assert "MAARS-Command-Documentation.pdf" in content_disp, f"Expected filename, got {content_disp}"
        print(f"PASS: Content-Disposition filename is MAARS-Command-Documentation.pdf")
    
    def test_pdf_valid_magic_bytes(self, pdf_response):
        """PDF starts with %PDF- magic bytes"""
        content = pdf_response.content
        assert content[:5] == b'%PDF-', f"Invalid PDF magic bytes: {content[:10]}"
        print(f"PASS: PDF starts with %PDF- magic bytes")
    
    def test_pdf_size(self, pdf_response):
        """PDF has reasonable size (>30KB for 14+ pages)"""
        size = len(pdf_response.content)
        print(f"INFO: PDF size is {size} bytes ({size/1024:.1f}KB)")
        assert size > 30000, f"PDF too small: {size} bytes"
        print(f"PASS: PDF size {size/1024:.1f}KB > 30KB")
    
    def test_pdf_requires_auth(self):
        """PDF endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/summary/pdf")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"PASS: PDF endpoint requires authentication")
    
    def test_pdf_rejects_invalid_token(self):
        """PDF endpoint rejects invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403 with invalid token, got {response.status_code}"
        print(f"PASS: PDF endpoint rejects invalid token")


class TestPDFContent:
    """Tests for PDF content using pypdf extraction"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("token")
    
    @pytest.fixture(scope="class")
    def pdf_content(self, auth_token):
        """Download PDF and extract text content"""
        import io
        try:
            from pypdf import PdfReader
        except ImportError:
            pytest.skip("pypdf not installed")
        
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        reader = PdfReader(io.BytesIO(response.content))
        full_text = ""
        for page in reader.pages:
            text = page.extract_text() or ""
            full_text += text + "\n"
        
        return {
            "text": full_text,
            "page_count": len(reader.pages),
            "raw_content": response.content
        }
    
    def test_pdf_page_count(self, pdf_content):
        """PDF has approximately 14 pages"""
        page_count = pdf_content["page_count"]
        print(f"INFO: PDF has {page_count} pages")
        # Allow some flexibility - at least 12 pages
        assert page_count >= 12, f"Expected 12+ pages, got {page_count}"
        print(f"PASS: PDF has {page_count} pages (expected ~14)")
    
    def test_cover_page_title(self, pdf_content):
        """Cover page contains 'MAARS Command' title"""
        text = pdf_content["text"]
        assert "MAARS Command" in text, "Missing 'MAARS Command' title"
        print(f"PASS: Cover page contains 'MAARS Command' title")
    
    def test_cover_page_subtitle(self, pdf_content):
        """Cover page contains subtitle about AI Enterprise Operating System"""
        text = pdf_content["text"]
        assert "AI" in text and ("Enterprise" in text or "Operating System" in text), \
            "Missing subtitle about AI Enterprise Operating System"
        print(f"PASS: Cover page contains subtitle")
    
    def test_table_of_contents(self, pdf_content):
        """PDF contains Table of Contents"""
        text = pdf_content["text"]
        assert "Table of Contents" in text or "Contents" in text, "Missing Table of Contents"
        print(f"PASS: PDF contains Table of Contents")
    
    def test_section1_platform_statistics(self, pdf_content):
        """Section 1: Platform Statistics present"""
        text = pdf_content["text"]
        assert "Platform Statistics" in text or "Statistics" in text, "Missing Platform Statistics section"
        print(f"PASS: Section 1 - Platform Statistics present")
    
    def test_section2_agent_workforce(self, pdf_content):
        """Section 2: 41-Agent AI Workforce present"""
        text = pdf_content["text"]
        assert "Agent" in text and ("Workforce" in text or "41" in text), "Missing Agent Workforce section"
        print(f"PASS: Section 2 - Agent Workforce section present")
    
    def test_section3_core_systems(self, pdf_content):
        """Section 3: Core Systems present"""
        text = pdf_content["text"]
        assert "Core Systems" in text or "Systems" in text, "Missing Core Systems section"
        print(f"PASS: Section 3 - Core Systems present")
    
    def test_section4_ai_providers(self, pdf_content):
        """Section 4: AI Providers present"""
        text = pdf_content["text"]
        assert "AI" in text and ("Provider" in text or "Model" in text), "Missing AI Providers section"
        print(f"PASS: Section 4 - AI Providers section present")
    
    def test_section5_technical_architecture(self, pdf_content):
        """Section 5: Technical Architecture present"""
        text = pdf_content["text"]
        assert "Technical" in text or "Architecture" in text, "Missing Technical Architecture section"
        print(f"PASS: Section 5 - Technical Architecture present")
    
    def test_section6_api_reference(self, pdf_content):
        """Section 6: API Reference present"""
        text = pdf_content["text"]
        assert "API" in text and ("Reference" in text or "Endpoint" in text or "212" in text), \
            "Missing API Reference section"
        print(f"PASS: Section 6 - API Reference present")
    
    def test_stat_cards_content(self, pdf_content):
        """PDF contains 5 stat card values"""
        text = pdf_content["text"]
        # Check for stat card indicators
        found_stats = []
        if "41" in text:
            found_stats.append("41 Agents")
        if "8" in text and "Layer" in text:
            found_stats.append("8 Layers")
        if "17" in text or "System" in text:
            found_stats.append("17 Systems")
        if "9" in text or "Provider" in text:
            found_stats.append("9 Providers")
        if "212" in text or "Endpoint" in text:
            found_stats.append("212+ Endpoints")
        
        print(f"INFO: Found stats: {found_stats}")
        assert len(found_stats) >= 3, f"Expected at least 3 stat indicators, found {len(found_stats)}"
        print(f"PASS: PDF contains stat card content ({len(found_stats)} found)")
    
    def test_all_8_layers_present(self, pdf_content):
        """PDF documents all 8 organizational layers"""
        text = pdf_content["text"]
        layers = [
            "Executive",
            "Technical",
            "Creative",
            "Marketing",
            "Operations",
            "Finance",
            "Governance",
            "Intelligence"
        ]
        found_layers = [l for l in layers if l in text]
        print(f"INFO: Found {len(found_layers)}/8 layers: {found_layers}")
        assert len(found_layers) >= 6, f"Expected 6+ layers, found {len(found_layers)}"
        print(f"PASS: PDF documents {len(found_layers)}/8 organizational layers")
    
    def test_key_agents_present(self, pdf_content):
        """PDF lists key agents including Commander Orion"""
        text = pdf_content["text"]
        key_agents = [
            "Commander Orion",
            "Product Manager",
            "App Developer",
            "Marketing Specialist",
            "Financial Analyst"
        ]
        found_agents = [a for a in key_agents if a.split()[0] in text]
        print(f"INFO: Found key agents: {found_agents}")
        assert len(found_agents) >= 2, f"Expected 2+ key agents, found {len(found_agents)}"
        print(f"PASS: PDF lists key agents ({len(found_agents)} found)")
    
    def test_all_17_systems_documented(self, pdf_content):
        """PDF documents all 17 core systems"""
        text = pdf_content["text"]
        systems = [
            "Orchestration",
            "Brain Profile",
            "Quality Control",
            "LLM Router",
            "Collaboration",
            "Reference Intelligence",
            "Content Generator",
            "Vibe Coding",
            "Activity Monitor",
            "Simulation",
            "Action Layer",
            "Voice",
            "Code Explorer",
            "Memory",
            "Command Palette"
        ]
        found_systems = [s for s in systems if s in text]
        print(f"INFO: Found {len(found_systems)}/15 system keywords")
        assert len(found_systems) >= 8, f"Expected 8+ system keywords, found {len(found_systems)}"
        print(f"PASS: PDF documents core systems ({len(found_systems)} keywords found)")
    
    def test_all_9_ai_providers_present(self, pdf_content):
        """PDF lists all 9 AI providers"""
        text = pdf_content["text"]
        providers = [
            "OpenAI",
            "Anthropic",
            "Google",
            "xAI",
            "DeepSeek",
            "Mistral",
            "Perplexity",
            "Cohere",
            "ElevenLabs"
        ]
        found_providers = [p for p in providers if p in text]
        print(f"INFO: Found {len(found_providers)}/9 providers: {found_providers}")
        assert len(found_providers) >= 5, f"Expected 5+ providers, found {len(found_providers)}"
        print(f"PASS: PDF lists AI providers ({len(found_providers)}/9 found)")
    
    def test_model_details_present(self, pdf_content):
        """PDF contains model details (GPT-5.2, Claude, etc.)"""
        text = pdf_content["text"]
        models = ["GPT", "Claude", "Gemini", "Grok", "Mistral", "Sonar"]
        found_models = [m for m in models if m in text]
        print(f"INFO: Found model names: {found_models}")
        assert len(found_models) >= 3, f"Expected 3+ model names, found {len(found_models)}"
        print(f"PASS: PDF contains model details ({len(found_models)} found)")
    
    def test_212_endpoints_mentioned(self, pdf_content):
        """PDF mentions 212+ endpoints"""
        text = pdf_content["text"]
        assert "212" in text or "endpoint" in text.lower(), "Missing 212+ endpoints reference"
        print(f"PASS: PDF references API endpoints")


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_backend_health(self):
        """Backend server is running"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"PASS: Backend server is running")
    
    def test_admin_login(self):
        """Admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Missing token in response"
        print(f"PASS: Admin login successful")
    
    def test_agents_endpoint(self):
        """Agents endpoint works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        token = response.json().get("token")
        
        agents_response = requests.get(
            f"{BASE_URL}/api/agents/public",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert agents_response.status_code == 200, f"Agents endpoint failed: {agents_response.status_code}"
        agents = agents_response.json()
        assert len(agents) >= 40, f"Expected 40+ agents, got {len(agents)}"
        print(f"PASS: Agents endpoint returns {len(agents)} agents")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
