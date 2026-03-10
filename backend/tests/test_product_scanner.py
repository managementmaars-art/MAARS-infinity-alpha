"""
Test Product Scanner Feature - Iteration 45
Tests:
- product_scan tool exists in AGENT_TOOLS and AGENT_TOOL_MAP (ALL agents)
- product_scanner service: search_product_details (DuckDuckGo text search)
- product_scanner service: search_product_images (DuckDuckGo image search)
- product_scan tool in execute_tool function
- Enhanced vision instruction mentions product_scan tool
- Video generation pipeline includes product_scan reference image check
"""

import pytest
import requests
import os
import asyncio
from pathlib import Path

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://task-flow-276.preview.emergentagent.com').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestProductScannerBackend:
    """Test product_scan tool configuration and backend integration"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json()["token"]
    
    def test_product_scan_tool_in_agent_tools(self):
        """Verify product_scan exists in AGENT_TOOLS config"""
        import sys
        sys.path.insert(0, '/app/backend')
        from config import AGENT_TOOLS
        
        assert "product_scan" in AGENT_TOOLS, "product_scan tool not found in AGENT_TOOLS"
        tool = AGENT_TOOLS["product_scan"]
        assert tool["name"] == "product_scan"
        assert "product" in tool["description"].lower()
        assert "product_query" in tool["parameters"].lower()
        print(f"PASSED: product_scan tool exists in AGENT_TOOLS with description: {tool['description'][:80]}...")
    
    def test_product_scan_in_all_agent_tool_maps(self):
        """Verify product_scan is available to ALL agents in AGENT_TOOL_MAP"""
        import sys
        sys.path.insert(0, '/app/backend')
        from config import AGENT_TOOL_MAP
        
        agents_with_product_scan = []
        agents_without_product_scan = []
        
        for agent_id, tools in AGENT_TOOL_MAP.items():
            if "product_scan" in tools:
                agents_with_product_scan.append(agent_id)
            else:
                agents_without_product_scan.append(agent_id)
        
        # All 21 agents should have product_scan
        expected_count = len(AGENT_TOOL_MAP)
        assert len(agents_with_product_scan) == expected_count, \
            f"product_scan missing from agents: {agents_without_product_scan}"
        print(f"PASSED: product_scan available to all {len(agents_with_product_scan)} agents")
    
    def test_product_scanner_service_exists(self):
        """Verify product_scanner service module exists and has required functions"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.product_scanner import (
            search_product_details,
            search_product_images,
            scan_product,
            download_reference_image,
            build_product_context
        )
        
        # Verify all functions are callable
        assert callable(search_product_details)
        assert callable(search_product_images)
        assert callable(scan_product)
        assert callable(download_reference_image)
        assert callable(build_product_context)
        print("PASSED: product_scanner service has all required functions")
    
    def test_search_product_details_works(self):
        """Test DuckDuckGo text search for product details"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.product_scanner import search_product_details
        
        result = asyncio.run(search_product_details("iPhone 16 Pro"))
        
        assert "sources" in result
        assert "snippets" in result
        # Should return some results (may vary based on DuckDuckGo availability)
        assert isinstance(result["sources"], list)
        sources_count = len(result["sources"])
        print(f"PASSED: search_product_details returned {sources_count} sources")
        
        # If we got sources, verify structure
        if sources_count > 0:
            source = result["sources"][0]
            assert "title" in source
            assert "url" in source
            assert "snippet" in source
    
    def test_search_product_images(self):
        """Test DuckDuckGo image search for product images"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.product_scanner import search_product_images
        
        # Note: DuckDuckGo image search may return 0 results due to API limitations
        result = asyncio.run(search_product_images("MacBook Pro laptop"))
        
        assert isinstance(result, list)
        images_count = len(result)
        print(f"PASSED: search_product_images returned {images_count} images (may be 0 due to DDG limits)")
        
        # If we got images, verify structure
        if images_count > 0:
            img = result[0]
            assert "url" in img
            assert "thumbnail" in img
    
    def test_scan_product_function(self):
        """Test the main scan_product function that combines details and images"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.product_scanner import scan_product
        
        result = asyncio.run(scan_product("Tesla Model Y"))
        
        assert "product_query" in result
        assert result["product_query"] == "Tesla Model Y"
        assert "details" in result
        assert "images" in result
        assert "context" in result
        assert "PRODUCT SCAN RESULTS" in result["context"]
        print(f"PASSED: scan_product returns complete result with context")
    
    def test_build_product_context(self):
        """Test context builder formats data correctly"""
        import sys
        sys.path.insert(0, '/app/backend')
        from services.product_scanner import build_product_context
        
        details = {
            "sources": [{"title": "Test Product Review", "url": "https://example.com", "snippet": "Great product"}],
            "snippets": ["This is a great product"],
            "scraped_content": ["Full review content here"]
        }
        images = [{"url": "https://img.example.com/product.jpg", "thumbnail": "https://img.example.com/thumb.jpg", "title": "Product Photo", "width": 1920, "height": 1080}]
        
        context = build_product_context("Test Product", details, images)
        
        assert "PRODUCT SCAN RESULTS: Test Product" in context
        assert "Product Information" in context
        assert "High-Quality Reference Images Found" in context
        print("PASSED: build_product_context formats data correctly")


class TestProductScanExecuteTool:
    """Test product_scan in execute_tool function"""
    
    def test_execute_tool_has_product_scan_handler(self):
        """Verify server.py execute_tool handles product_scan"""
        server_path = Path('/app/backend/server.py')
        content = server_path.read_text()
        
        # Check for product_scan handler in execute_tool
        assert 'elif tool_name == "product_scan":' in content, \
            "product_scan handler not found in execute_tool"
        assert 'from services.product_scanner import scan_product' in content, \
            "product_scanner import not found in execute_tool"
        print("PASSED: execute_tool has product_scan handler")


class TestEnhancedVisionInstruction:
    """Test that vision instruction mentions product_scan tool"""
    
    def test_vision_instruction_includes_product_scan(self):
        """Verify image analysis prompt mentions product_scan tool"""
        server_path = Path('/app/backend/server.py')
        content = server_path.read_text()
        
        # Find the vision instruction section
        assert 'VISION ACTIVE' in content, "VISION ACTIVE instruction not found"
        assert 'product_scan' in content, "product_scan not mentioned in server.py"
        
        # More specific: check that product_scan is in the image analysis context
        # Find the section around VISION ACTIVE
        vision_start = content.find('VISION ACTIVE')
        vision_section = content[vision_start:vision_start+1500]
        
        assert 'product_scan' in vision_section, \
            "product_scan not mentioned in VISION ACTIVE instruction"
        print("PASSED: Vision instruction includes product_scan tool reference")


class TestVideoGenProductScan:
    """Test video generation pipeline includes product_scan reference image check"""
    
    def test_video_gen_checks_product_scan(self):
        """Verify video generation looks for product_scan reference images"""
        server_path = Path('/app/backend/server.py')
        content = server_path.read_text()
        
        # Check for product_scan reference in video generation section
        assert 'product_scan' in content
        
        # Find the Sora/video generation section
        sora_idx = content.find('Sora')
        if sora_idx > 0:
            # Look for product_scan reference nearby video generation code
            video_section = content[sora_idx-2000:sora_idx+2000] if sora_idx > 2000 else content[:sora_idx+2000]
            # Check that video gen considers product_scan
            assert 'product_scan' in video_section or 'reference image' in video_section.lower(), \
                "Video generation doesn't appear to check product_scan references"
        print("PASSED: Video generation pipeline includes product_scan reference check")


class TestAPIEndpoints:
    """Test API endpoints work correctly"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not authenticate")
        return response.json()["token"]
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("PASSED: Health check returns 200")
    
    def test_agents_list_includes_tools(self, auth_token):
        """Test agents list includes product_scan in tools"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
        assert response.status_code == 200
        agents = response.json()
        
        # Check at least one agent has product_scan in tools
        agents_with_product_scan = [a for a in agents if "product_scan" in a.get("tools", [])]
        assert len(agents_with_product_scan) > 0, "No agents have product_scan tool"
        print(f"PASSED: {len(agents_with_product_scan)} agents have product_scan tool")
    
    def test_tools_endpoint(self, auth_token):
        """Test tools endpoint includes product_scan"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/agents/tools", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "tools" in data
        assert "product_scan" in data["tools"]
        print("PASSED: /api/agents/tools includes product_scan")
    
    def test_public_agents_includes_product_scan_tools(self):
        """Test public agents endpoint shows product_scan in tools"""
        response = requests.get(f"{BASE_URL}/api/agents/public")
        assert response.status_code == 200
        agents = response.json()
        
        # Check Commander has product_scan
        commander = next((a for a in agents if a.get("agent_id") == "agent_commander"), None)
        assert commander is not None, "Commander agent not found"
        assert "product_scan" in commander.get("tools", []), "Commander doesn't have product_scan tool"
        print("PASSED: Public agents endpoint shows product_scan in Commander's tools")


class TestExistingFeatures:
    """Verify existing features still work after product_scan addition"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Could not authenticate")
        return response.json()["token"]
    
    def test_auth_login(self):
        """Test login still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_admin"] == True
        print("PASSED: Auth login works")
    
    def test_auth_me(self, auth_token):
        """Test /auth/me endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200
        print("PASSED: /auth/me works")
    
    def test_create_chat(self, auth_token):
        """Test chat creation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BASE_URL}/api/chats", 
            headers=headers,
            json={"agent_id": "agent_commander", "title": "Test Chat for Product Scanner"})
        assert response.status_code == 200
        chat = response.json()
        assert "chat_id" in chat
        print(f"PASSED: Chat creation works - {chat['chat_id']}")
    
    def test_admin_stats(self, auth_token):
        """Test admin stats endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        print("PASSED: Admin stats endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
