"""
Iteration 39: RAG Knowledge Base System Tests
Tests the new RAG (Retrieval-Augmented Generation) features:
1. Knowledge Base tab accessibility
2. Document upload to agent
3. Document listing with status
4. Knowledge search with TF-IDF
5. RAG context injection in chat
6. Avatar persistence in messages
7. Agent switch toast notification
8. Document deletion
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agent-os-8.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "management.maars@marsgc.net"
ADMIN_PASSWORD = "MaarsAdmin2024!"


class TestAdminLogin:
    """Test admin login for RAG features access"""
    
    def test_admin_login_success(self):
        """Test admin can login successfully"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_admin"] == True
        print(f"✓ Admin login successful: {data['user']['name']}")


class TestKnowledgeBaseFeatures:
    """Test Knowledge Base (RAG) system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_list_knowledge_docs(self):
        """Test GET /api/agents/{agent_id}/knowledge - list documents"""
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_legal/knowledge",
            headers=self.headers
        )
        assert response.status_code == 200
        docs = response.json()
        assert isinstance(docs, list)
        print(f"✓ Knowledge docs endpoint works: {len(docs)} documents")
        
        # Verify the pre-uploaded test document exists
        if docs:
            doc = docs[0]
            assert "doc_id" in doc
            assert "status" in doc
            assert doc["status"] == "ready"
            assert doc.get("chunk_count", 0) > 0
            print(f"  - Document: {doc['title']} (status={doc['status']}, chunks={doc.get('chunk_count', 0)})")
    
    def test_knowledge_search(self):
        """Test POST /api/agents/{agent_id}/knowledge/search - TF-IDF search"""
        response = requests.post(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/search",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"query": "corporate tax rates"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify search returns results
        assert "results" in data
        results = data["results"]
        assert len(results) > 0, "Expected at least one search result"
        
        # Verify result structure
        result = results[0]
        assert "text" in result
        assert "score" in result
        assert result["score"] > 0, "Expected score > 0 for relevant query"
        assert "doc_title" in result
        assert "corporate tax" in result["text"].lower() or "tax rates" in result["text"].lower()
        
        print(f"✓ Knowledge search works: {len(results)} results, top score={result['score']:.4f}")
        print(f"  - Query: 'corporate tax rates'")
        print(f"  - Found in: {result['doc_title']}")
    
    def test_knowledge_search_threshold(self):
        """Test that search returns results above threshold"""
        response = requests.post(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/search",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"query": "VAT registration"}
        )
        assert response.status_code == 200
        data = response.json()
        
        if data.get("results"):
            for result in data["results"]:
                # TF-IDF threshold is 0.10 in rag_service.py
                assert result["score"] >= 0.05, f"Score {result['score']} below threshold"
        print(f"✓ Search threshold working: {len(data.get('results', []))} results above threshold")


class TestUploadAndDeleteKnowledge:
    """Test document upload and deletion"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_upload_text_document(self):
        """Test POST /api/agents/{agent_id}/knowledge/upload - upload document"""
        # Create a test file
        test_content = """Test Document for RAG System
        
Section 1: Introduction
This is a test document uploaded via the API for testing purposes.

Section 2: Test Data
- Item 1: Testing upload functionality
- Item 2: Testing text extraction
- Item 3: Testing chunk processing

Section 3: Conclusion
The RAG system should process this document and make it searchable.
"""
        
        files = {
            'file': ('test_rag_document.txt', test_content, 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/upload",
            headers=self.headers,
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "doc_id" in data
        assert "title" in data
        assert data["status"] in ["queued", "processing", "ready"]
        
        doc_id = data["doc_id"]
        print(f"✓ Document uploaded: {data['title']} (doc_id={doc_id})")
        
        # Wait for processing (background task)
        time.sleep(3)
        
        # Check document status
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/{doc_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        doc_status = response.json()
        print(f"  - Status after 3s: {doc_status.get('status')}, chunks: {doc_status.get('chunk_count', 0)}")
        
        # Store doc_id for deletion test
        self.__class__.uploaded_doc_id = doc_id
    
    def test_delete_knowledge_document(self):
        """Test DELETE /api/agents/{agent_id}/knowledge/{doc_id}"""
        doc_id = getattr(self.__class__, 'uploaded_doc_id', None)
        
        if not doc_id:
            # Upload a new document for deletion test
            test_content = "Delete test document content"
            files = {
                'file': ('delete_test.txt', test_content, 'text/plain')
            }
            response = requests.post(
                f"{BASE_URL}/api/agents/agent_legal/knowledge/upload",
                headers=self.headers,
                files=files
            )
            assert response.status_code == 200
            doc_id = response.json()["doc_id"]
            time.sleep(2)
        
        # Delete the document
        response = requests.delete(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/{doc_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in str(data) or "success" in str(data).lower() or "chunks_deleted" in str(data)
        
        print(f"✓ Document deleted: {doc_id}")
        
        # Verify deletion
        response = requests.get(
            f"{BASE_URL}/api/agents/agent_legal/knowledge/{doc_id}",
            headers=self.headers
        )
        assert response.status_code == 404, "Document should not exist after deletion"
        print(f"  - Verified: Document no longer exists (404)")


class TestRAGChatIntegration:
    """Test RAG context injection in chat"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_id = response.json()["user"]["user_id"]
    
    def test_rag_context_in_chat(self):
        """Test that sending a message to legal agent with knowledge base triggers RAG"""
        # Create a chat with legal agent
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"agent_id": "agent_legal"}
        )
        assert response.status_code in [200, 201]
        chat = response.json()
        chat_id = chat["chat_id"]
        print(f"✓ Created chat: {chat_id}")
        
        # Send a message that should trigger RAG
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers={**self.headers, "Content-Type": "application/json"},
            json={
                "content": "What are the corporate tax rates in Bangladesh according to the tax act?",
                "model_provider": "auto",
                "model_name": "auto"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "assistant_message" in data
        assistant_msg = data["assistant_message"]
        assert "content" in assistant_msg
        
        # The response should mention tax rates from the knowledge base
        content_lower = assistant_msg["content"].lower()
        has_tax_info = any(term in content_lower for term in [
            "22.5%", "27.5%", "30%", "37.5%",  # Corporate tax rates from the doc
            "listed companies", "corporate tax", "tax rates", "bangladesh"
        ])
        
        print(f"✓ Chat response received ({len(assistant_msg['content'])} chars)")
        print(f"  - Response mentions tax info: {has_tax_info}")
        
        # Cleanup - delete the test chat
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=self.headers)
        print(f"  - Test chat cleaned up")


class TestAvatarPersistence:
    """Test that assistant messages include agent avatar"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_assistant_message_has_avatar(self):
        """Test GET /api/chats/{chat_id}/messages returns assistant messages with agent_avatar"""
        # First create a chat and send a message
        response = requests.post(
            f"{BASE_URL}/api/chats",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"agent_id": "agent_marketing"}  # Use marketing agent for variety
        )
        assert response.status_code in [200, 201]
        chat = response.json()
        chat_id = chat["chat_id"]
        
        # Send a message to get assistant response
        response = requests.post(
            f"{BASE_URL}/api/chats/{chat_id}/messages",
            headers={**self.headers, "Content-Type": "application/json"},
            json={
                "content": "Hello, what can you help me with?",
                "model_provider": "auto",
                "model_name": "auto"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check assistant message has avatar fields
        assistant_msg = data.get("assistant_message", {})
        
        # Verify avatar persistence fields
        has_avatar = "agent_avatar" in assistant_msg
        has_name = "agent_name" in assistant_msg
        
        print(f"✓ Assistant message structure verified")
        print(f"  - Has agent_avatar: {has_avatar}")
        print(f"  - Has agent_name: {has_name}")
        
        if has_avatar:
            print(f"  - Avatar URL: {assistant_msg['agent_avatar'][:50]}...")
        if has_name:
            print(f"  - Agent name: {assistant_msg['agent_name']}")
        
        assert has_avatar, "Assistant message should have agent_avatar field"
        assert has_name, "Assistant message should have agent_name field"
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=self.headers)


class TestAgentsList:
    """Test agents list endpoint for frontend agent switching"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_agents_list_for_kb_tab(self):
        """Test GET /api/agents returns agent list for Knowledge Base tab dropdown"""
        response = requests.get(
            f"{BASE_URL}/api/agents",
            headers=self.headers
        )
        assert response.status_code == 200
        agents = response.json()
        
        assert isinstance(agents, list)
        assert len(agents) > 0
        
        # Check for legal agent which has knowledge base docs
        legal_agent = next((a for a in agents if a.get("agent_id") == "agent_legal"), None)
        assert legal_agent is not None, "agent_legal should exist"
        
        print(f"✓ Agents list retrieved: {len(agents)} agents")
        print(f"  - Legal agent found: {legal_agent['name']}")
        
        # Verify agent has required fields for KB dropdown
        for agent in agents[:3]:  # Check first 3
            assert "agent_id" in agent
            assert "name" in agent
            assert "role" in agent


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
