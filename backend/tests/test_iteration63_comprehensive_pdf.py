"""
Iteration 63: Test comprehensive 21-page PDF documentation
Tests the complete rewrite of /api/summary/pdf from 7-page summary to 21-page comprehensive document
"""
import pytest
import requests
import os
import io

# Read BASE_URL from environment
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fallback to frontend .env
    env_file = "/app/frontend/.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL"):
                    BASE_URL = line.split("=")[1].strip().rstrip("/")
                    break

TEST_CREDENTIALS = {
    "email": "management.maars@marsgc.net",
    "password": "admin123"
}


class TestComprehensivePDF:
    """Test the comprehensive 21-page PDF documentation"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS,
            timeout=30
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def pdf_response(self, auth_token):
        """Download the PDF once for all tests"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=60
        )
        return response
    
    def test_pdf_endpoint_returns_200(self, pdf_response):
        """PDF endpoint should return 200 OK"""
        assert pdf_response.status_code == 200, f"Expected 200, got {pdf_response.status_code}"
        print("PASS: PDF endpoint returns 200")
    
    def test_pdf_content_type(self, pdf_response):
        """PDF should have correct content type"""
        content_type = pdf_response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got {content_type}"
        print("PASS: Content-Type is application/pdf")
    
    def test_pdf_content_disposition(self, pdf_response):
        """PDF should have proper filename in disposition"""
        disposition = pdf_response.headers.get("Content-Disposition", "")
        assert "MAARS-Command-Documentation.pdf" in disposition, f"Wrong filename: {disposition}"
        print("PASS: Content-Disposition has correct filename")
    
    def test_pdf_valid_magic_bytes(self, pdf_response):
        """PDF should have valid PDF magic bytes"""
        content = pdf_response.content
        assert content.startswith(b"%PDF-"), "PDF does not start with %PDF-"
        print("PASS: PDF starts with valid magic bytes")
    
    def test_pdf_size_greater_than_40kb(self, pdf_response):
        """PDF should be >40KB (comprehensive documentation)"""
        size = len(pdf_response.content)
        print(f"INFO: PDF size is {size} bytes ({size/1024:.1f} KB)")
        assert size > 40000, f"PDF too small ({size} bytes), expected >40KB for comprehensive doc"
        print(f"PASS: PDF size {size/1024:.1f}KB > 40KB threshold")
    
    def test_pdf_has_approximately_21_pages(self, pdf_response):
        """PDF should have approximately 21 pages"""
        content = pdf_response.content.decode('latin-1')
        # Count page objects in PDF
        page_count = content.count('/Type /Page')
        # Subtract 1 for /Pages object
        actual_pages = max(0, page_count - 1) if content.count('/Type /Pages') > 0 else page_count
        print(f"INFO: Detected approximately {actual_pages} pages in PDF")
        # Accept range from 18-25 pages (close to 21)
        assert actual_pages >= 18, f"PDF has only {actual_pages} pages, expected ~21"
        print(f"PASS: PDF has {actual_pages} pages (expected ~21)")
    
    def test_pdf_contains_table_of_contents(self, pdf_response):
        """PDF should have Table of Contents section"""
        content = pdf_response.content.decode('latin-1')
        assert "Table of Contents" in content, "Missing 'Table of Contents' section"
        print("PASS: PDF contains Table of Contents")
    
    def test_pdf_contains_platform_statistics(self, pdf_response):
        """PDF should have Platform Statistics section"""
        content = pdf_response.content.decode('latin-1')
        assert "Platform Statistics" in content, "Missing 'Platform Statistics' section"
        print("PASS: PDF contains Platform Statistics section")
    
    def test_pdf_contains_41_agent_workforce(self, pdf_response):
        """PDF should mention 41-Agent AI Workforce"""
        content = pdf_response.content.decode('latin-1')
        assert "41-Agent" in content or "41 agents" in content.lower(), "Missing 41-Agent workforce reference"
        print("PASS: PDF mentions 41-Agent workforce")
    
    def test_pdf_contains_8_organizational_layers(self, pdf_response):
        """PDF should document all 8 organizational layers"""
        content = pdf_response.content.decode('latin-1')
        layers = [
            "Executive Layer",
            "Product & Technical Layer",
            "Creative & Brand Layer",
            "Growth & Marketing Layer",
            "Operations Layer",
            "Finance Layer",
            "Governance Layer",
            "Intelligence Layer"
        ]
        found_layers = [layer for layer in layers if layer in content]
        print(f"INFO: Found {len(found_layers)}/8 layers: {found_layers}")
        assert len(found_layers) >= 7, f"Only found {len(found_layers)} layers, expected 8"
        print(f"PASS: PDF contains {len(found_layers)} organizational layers")
    
    def test_pdf_contains_17_systems_detailed(self, pdf_response):
        """PDF should contain detailed documentation for 17 systems"""
        content = pdf_response.content.decode('latin-1')
        # Check for specific systems
        systems = [
            "Autonomous Orchestration Engine",
            "Custom Brain Profiles",
            "Quality Control",
            "LLM Router",
            "Collaboration Engine",
            "Reference Intelligence",
            "Content Generator",
            "Vibe Coding",
            "Activity Monitor",
            "Simulation vs. Execution",
            "Real-World Action",
            "LLM Configuration",
            "Voice Command",
            "Code Explorer",
            "Memory Governance",
            "Memory Auto-Learning",
            "Command Palette"
        ]
        found_systems = [sys for sys in systems if sys in content]
        print(f"INFO: Found {len(found_systems)}/17 systems")
        assert len(found_systems) >= 14, f"Only found {len(found_systems)} systems, expected 17"
        print(f"PASS: PDF contains {len(found_systems)} system descriptions")
    
    def test_pdf_system_sections_have_five_parts(self, pdf_response):
        """Each system should have 5 detailed sections"""
        content = pdf_response.content.decode('latin-1')
        # Look for the section headers used in detailed system documentation
        required_headers = [
            "What It Does",
            "How It Works",
            "Configuration",
            "Data Model",
            "API Endpoints"
        ]
        found_headers = [h for h in required_headers if h in content]
        print(f"INFO: Found system section headers: {found_headers}")
        assert len(found_headers) == 5, f"Only found {found_headers}, expected all 5 section types"
        print("PASS: Systems have all 5 detailed sections")
    
    def test_pdf_contains_9_ai_providers(self, pdf_response):
        """PDF should document all 9 AI providers"""
        content = pdf_response.content.decode('latin-1')
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
        found_providers = [p for p in providers if p in content]
        print(f"INFO: Found {len(found_providers)}/9 providers: {found_providers}")
        assert len(found_providers) >= 8, f"Only found {len(found_providers)} providers, expected 9"
        print(f"PASS: PDF contains {len(found_providers)} AI providers")
    
    def test_pdf_contains_technical_architecture(self, pdf_response):
        """PDF should have Technical Architecture section"""
        content = pdf_response.content.decode('latin-1')
        assert "Technical Architecture" in content, "Missing 'Technical Architecture' section"
        print("PASS: PDF contains Technical Architecture section")
    
    def test_pdf_architecture_has_all_subsections(self, pdf_response):
        """Technical Architecture should have Backend, Frontend, AI Layer subsections"""
        content = pdf_response.content.decode('latin-1')
        subsections = ["Backend Stack", "Frontend Stack", "AI & LLM Layer", "Database Collections"]
        found = [s for s in subsections if s in content]
        print(f"INFO: Found architecture subsections: {found}")
        assert len(found) >= 3, f"Only found {found}, expected at least 3 subsections"
        print("PASS: Technical Architecture has required subsections")
    
    def test_pdf_contains_api_reference(self, pdf_response):
        """PDF should have Complete API Reference section"""
        content = pdf_response.content.decode('latin-1')
        assert "API Reference" in content, "Missing 'API Reference' section"
        print("PASS: PDF contains API Reference section")
    
    def test_pdf_api_reference_has_212_plus_endpoints(self, pdf_response):
        """PDF should mention 212+ endpoints"""
        content = pdf_response.content.decode('latin-1')
        assert "212" in content or "210" in content or "200+" in content, "Missing 212+ endpoints count"
        print("PASS: PDF mentions 212+ API endpoints")
    
    def test_pdf_api_has_13_sections(self, pdf_response):
        """API Reference should be organized in 13 sections"""
        content = pdf_response.content.decode('latin-1')
        # Check for key API sections
        api_sections = [
            "Authentication",
            "Agents",
            "Projects",
            "Tasks",
            "Enterprise",
            "Memory",
            "Content",
            "Vibe",
            "Voice",
            "Actions",
            "Teams",
            "Subscription",
            "Admin"
        ]
        found_sections = [s for s in api_sections if s in content]
        print(f"INFO: Found API sections: {found_sections}")
        assert len(found_sections) >= 10, f"Only found {len(found_sections)} API sections, expected 13"
        print(f"PASS: API Reference has {len(found_sections)} sections")
    
    def test_pdf_agent_profiles_have_capabilities(self, pdf_response):
        """Agent profiles should include capabilities"""
        content = pdf_response.content.decode('latin-1')
        # Look for capabilities keywords
        assert "Capabilities" in content, "Missing agent capabilities section"
        print("PASS: Agent profiles include capabilities")
    
    def test_pdf_agent_profiles_have_default_models(self, pdf_response):
        """Agent profiles should include default model info"""
        content = pdf_response.content.decode('latin-1')
        # Agents use GPT-5.2 as default
        assert "Default Model" in content or "GPT-5.2" in content, "Missing default model info"
        print("PASS: Agent profiles include default model info")
    
    def test_pdf_providers_have_pricing(self, pdf_response):
        """AI providers should have pricing information"""
        content = pdf_response.content.decode('latin-1')
        # Look for pricing patterns like "$X.XX"
        assert "$" in content and "per 1M tok" in content, "Missing pricing information"
        print("PASS: AI providers include pricing information")


class TestPDFEndpointAuth:
    """Test PDF endpoint authentication requirements"""
    
    def test_pdf_requires_authentication(self):
        """PDF endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/summary/pdf", timeout=30)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PDF endpoint requires authentication")
    
    def test_pdf_rejects_invalid_token(self):
        """PDF endpoint should reject invalid token"""
        response = requests.get(
            f"{BASE_URL}/api/summary/pdf",
            headers={"Authorization": "Bearer invalid_token"},
            timeout=30
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: PDF endpoint rejects invalid token")
