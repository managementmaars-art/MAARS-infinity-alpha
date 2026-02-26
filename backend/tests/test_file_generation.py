"""
Test file generation features:
- POST /api/generate/document (PDF, XLSX, DOCX, CSV, TXT)
- GET /api/files/{filename} serving files
- POST /api/generate/image (validation only - no actual gen)
- POST /api/generate/video (validation only - no actual gen)
- GET /api/models includes GPT Image 1, DALL-E 3, Sora 2
- Admin API keys cost_reference includes generation model pricing
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Get auth token for tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Login as admin and return token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "management.maars@marsgc.net",
            "password": "MaarsAdmin2024!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json()["token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }


class TestDocumentGeneration(TestAuthentication):
    """Test PDF, Excel, Word, CSV, Text document generation"""
    
    def test_generate_pdf_document(self, auth_headers):
        """Test PDF document generation"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "pdf",
                "title": "Test PDF Document",
                "content": "This is a test paragraph.\nSecond paragraph here."
            }
        )
        assert response.status_code == 200, f"PDF generation failed: {response.text}"
        data = response.json()
        assert "filename" in data
        assert data["type"] == "pdf"
        assert data["filename"].endswith(".pdf")
        assert "url" in data
        assert data["url"].startswith("/api/files/")
        print(f"✓ PDF generated: {data['filename']}")
        return data
    
    def test_generate_xlsx_document(self, auth_headers):
        """Test Excel document generation"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "xlsx",
                "title": "Test Excel",
                "content": "Header1, Header2\nData1, Data2\nData3, Data4",
                "rows": [
                    ["Header1", "Header2"],
                    ["Data1", "Data2"],
                    ["Data3", "Data4"]
                ]
            }
        )
        assert response.status_code == 200, f"Excel generation failed: {response.text}"
        data = response.json()
        assert data["type"] == "xlsx"
        assert data["filename"].endswith(".xlsx")
        assert "url" in data
        print(f"✓ Excel generated: {data['filename']}")
        return data
    
    def test_generate_docx_document(self, auth_headers):
        """Test Word document generation"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "docx",
                "title": "Test Word Document",
                "content": "This is the first paragraph.\nThis is the second paragraph."
            }
        )
        assert response.status_code == 200, f"DOCX generation failed: {response.text}"
        data = response.json()
        assert data["type"] == "docx"
        assert data["filename"].endswith(".docx")
        print(f"✓ Word doc generated: {data['filename']}")
        return data
    
    def test_generate_csv_document(self, auth_headers):
        """Test CSV document generation"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "csv",
                "title": "Test CSV",
                "content": "Row1\nRow2\nRow3",
                "rows": [
                    ["Name", "Age", "City"],
                    ["John", "30", "NYC"],
                    ["Jane", "25", "LA"]
                ]
            }
        )
        assert response.status_code == 200, f"CSV generation failed: {response.text}"
        data = response.json()
        assert data["type"] == "csv"
        assert data["filename"].endswith(".csv")
        print(f"✓ CSV generated: {data['filename']}")
        return data
    
    def test_generate_txt_document(self, auth_headers):
        """Test plain text document generation"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "txt",
                "title": "Test Text File",
                "content": "This is plain text content.\nSecond line.\nThird line."
            }
        )
        assert response.status_code == 200, f"TXT generation failed: {response.text}"
        data = response.json()
        assert data["type"] == "txt"
        assert data["filename"].endswith(".txt")
        print(f"✓ TXT generated: {data['filename']}")
        return data
    
    def test_document_generation_requires_content(self, auth_headers):
        """Test that document generation fails without content"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "pdf",
                "title": "Empty Doc"
            }
        )
        assert response.status_code == 400, "Should reject empty content"
        print("✓ Document generation correctly requires content")
    
    def test_unsupported_document_type(self, auth_headers):
        """Test that unsupported document types are rejected"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "ppt",  # Not supported
                "title": "Test",
                "content": "Some content"
            }
        )
        assert response.status_code == 400, "Should reject unsupported type"
        print("✓ Unsupported document type correctly rejected")


class TestFileServing(TestAuthentication):
    """Test serving generated files"""
    
    def test_serve_generated_file(self, auth_headers):
        """Test that generated files can be served with correct content-type"""
        # First generate a PDF
        gen_response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers=auth_headers,
            json={
                "type": "pdf",
                "title": "File Serve Test",
                "content": "Test content for file serving"
            }
        )
        assert gen_response.status_code == 200
        filename = gen_response.json()["filename"]
        
        # Now try to fetch it
        file_response = requests.get(
            f"{BASE_URL}/api/files/{filename}",
            allow_redirects=True
        )
        assert file_response.status_code == 200, f"File serve failed: {file_response.status_code}"
        assert "application/pdf" in file_response.headers.get("content-type", "")
        assert len(file_response.content) > 0
        print(f"✓ File served successfully with correct content-type")
    
    def test_serve_nonexistent_file_returns_404(self):
        """Test that non-existent files return 404"""
        response = requests.get(f"{BASE_URL}/api/files/nonexistent_file_xyz.pdf")
        assert response.status_code == 404
        print("✓ Non-existent file correctly returns 404")


class TestImageGenerationValidation(TestAuthentication):
    """Test image generation endpoint validation (not actual generation - too slow/expensive)"""
    
    def test_image_endpoint_requires_prompt(self, auth_headers):
        """Test that image generation requires a prompt"""
        response = requests.post(
            f"{BASE_URL}/api/generate/image",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "prompt" in data.get("detail", "").lower() or "required" in data.get("detail", "").lower()
        print("✓ Image generation correctly requires prompt")
    
    def test_image_endpoint_rejects_empty_prompt(self, auth_headers):
        """Test that empty prompt is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/generate/image",
            headers=auth_headers,
            json={"prompt": ""}
        )
        assert response.status_code == 400
        print("✓ Image generation correctly rejects empty prompt")


class TestVideoGenerationValidation(TestAuthentication):
    """Test video generation endpoint validation (not actual generation - too slow/expensive)"""
    
    def test_video_endpoint_requires_prompt(self, auth_headers):
        """Test that video generation requires a prompt"""
        response = requests.post(
            f"{BASE_URL}/api/generate/video",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        data = response.json()
        assert "prompt" in data.get("detail", "").lower() or "required" in data.get("detail", "").lower()
        print("✓ Video generation correctly requires prompt")
    
    def test_video_endpoint_rejects_empty_prompt(self, auth_headers):
        """Test that empty prompt is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/generate/video",
            headers=auth_headers,
            json={"prompt": ""}
        )
        assert response.status_code == 400
        print("✓ Video generation correctly rejects empty prompt")


class TestModelsEndpoint(TestAuthentication):
    """Test /api/models includes generation models"""
    
    def test_models_includes_gpt_image_1(self, auth_headers):
        """Test that /api/models includes GPT Image 1"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200, f"Models endpoint failed: {response.text}"
        data = response.json()
        
        models = data.get("models", [])
        gpt_image = next((m for m in models if m.get("model") == "gpt-image-1"), None)
        
        assert gpt_image is not None, "GPT Image 1 not found in models list"
        assert gpt_image["name"] == "GPT Image 1"
        assert gpt_image["category"] == "image_gen"
        print("✓ GPT Image 1 found in models list")
    
    def test_models_includes_dalle_3(self, auth_headers):
        """Test that /api/models includes DALL-E 3"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        models = data.get("models", [])
        dalle = next((m for m in models if m.get("model") == "dall-e-3"), None)
        
        assert dalle is not None, "DALL-E 3 not found in models list"
        assert dalle["name"] == "DALL-E 3"
        assert dalle["category"] == "image_gen"
        print("✓ DALL-E 3 found in models list")
    
    def test_models_includes_sora_2(self, auth_headers):
        """Test that /api/models includes Sora 2"""
        response = requests.get(f"{BASE_URL}/api/models", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        models = data.get("models", [])
        sora = next((m for m in models if m.get("model") == "sora-2"), None)
        
        assert sora is not None, "Sora 2 not found in models list"
        assert sora["name"] == "Sora 2"
        assert sora["category"] == "video_gen"
        print("✓ Sora 2 found in models list")


class TestAdminCostReference(TestAuthentication):
    """Test admin API keys endpoint includes generation model pricing"""
    
    def test_admin_api_keys_cost_reference(self, auth_headers):
        """Test that admin API keys endpoint has cost reference with generation models"""
        response = requests.get(f"{BASE_URL}/api/admin/api-keys", headers=auth_headers)
        assert response.status_code == 200, f"Admin API keys failed: {response.text}"
        data = response.json()
        
        assert "cost_reference" in data, "cost_reference not in response"
        cost_ref = data["cost_reference"]
        
        # Check OpenAI section has generation models
        openai_models = cost_ref.get("openai", {}).get("models", [])
        model_names = [m["name"] for m in openai_models]
        
        assert "GPT Image 1" in model_names, "GPT Image 1 not in cost reference"
        assert "DALL-E 3" in model_names, "DALL-E 3 not in cost reference"
        assert "Sora 2" in model_names, "Sora 2 not in cost reference"
        
        print("✓ Admin cost reference includes GPT Image 1, DALL-E 3, Sora 2")
        
        # Verify pricing info exists
        gpt_img = next(m for m in openai_models if m["name"] == "GPT Image 1")
        assert gpt_img.get("input"), "GPT Image 1 missing input pricing"
        
        dalle = next(m for m in openai_models if m["name"] == "DALL-E 3")
        assert dalle.get("input"), "DALL-E 3 missing input pricing"
        
        sora = next(m for m in openai_models if m["name"] == "Sora 2")
        assert sora.get("input"), "Sora 2 missing input pricing"
        
        print("✓ Generation models have pricing info in cost reference")


class TestDocumentGenerationAuth(TestAuthentication):
    """Test that document generation requires authentication"""
    
    def test_document_generation_requires_auth(self):
        """Test that document generation fails without auth"""
        response = requests.post(
            f"{BASE_URL}/api/generate/document",
            headers={"Content-Type": "application/json"},
            json={
                "type": "pdf",
                "title": "Test",
                "content": "Content"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Document generation correctly requires authentication")
    
    def test_image_generation_requires_auth(self):
        """Test that image generation fails without auth"""
        response = requests.post(
            f"{BASE_URL}/api/generate/image",
            headers={"Content-Type": "application/json"},
            json={"prompt": "A test image"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Image generation correctly requires authentication")
    
    def test_video_generation_requires_auth(self):
        """Test that video generation fails without auth"""
        response = requests.post(
            f"{BASE_URL}/api/generate/video",
            headers={"Content-Type": "application/json"},
            json={"prompt": "A test video"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Video generation correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
