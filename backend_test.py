#!/usr/bin/env python3

import requests
import json
import sys
import time
from datetime import datetime

class NexusAIBackendTester:
    def __init__(self, base_url="https://agent-os-8.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = self.session.patch(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return success, response.json() if response.text else {}
                except:
                    return success, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'No detail')
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Network Error: {str(e)}")
            return False, {}

    def test_auth_flow(self):
        """Test authentication flow"""
        self.log("\n=== AUTHENTICATION TESTS ===")
        
        # Test user registration
        test_email = f"test_user_{int(time.time())}@example.com"
        test_password = "TestPassword123!"
        test_name = "Test User"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": test_password,
                "name": test_name
            }
        )
        
        if not success:
            # Try with existing test user
            success, response = self.run_test(
                "User Login (Fallback)",
                "POST", 
                "auth/login",
                200,
                data={"email": "test@example.com", "password": "test123"}
            )
        
        if success and 'token' in response:
            self.token = response['token']
            self.user_id = response['user']['user_id']
            self.log(f"   🔑 Got auth token for user: {response['user']['email']}")
            
            # Test /auth/me endpoint
            self.run_test("Get Current User", "GET", "auth/me", 200)
            return True
        
        return False

    def test_agents_endpoints(self):
        """Test agent management endpoints"""
        self.log("\n=== AGENTS TESTS ===")
        
        # Get all agents
        success, agents_data = self.run_test("Get All Agents", "GET", "agents", 200)
        if not success:
            return False
            
        agents = agents_data if isinstance(agents_data, list) else []
        self.log(f"   📋 Found {len(agents)} agents")
        
        if agents:
            # Test get specific agent
            first_agent = agents[0]
            self.run_test(
                f"Get Agent Details",
                "GET", 
                f"agents/{first_agent['agent_id']}", 
                200
            )
        
        # Test creating custom agent
        custom_agent_data = {
            "name": "Test Agent",
            "description": "A test agent for API testing",
            "role": "Tester",
            "system_prompt": "You are a helpful test agent.",
            "model_provider": "openai",
            "model_name": "gpt-5.2",
            "capabilities": ["Testing", "API Validation"]
        }
        
        success, created_agent = self.run_test(
            "Create Custom Agent",
            "POST",
            "agents",
            200,
            data=custom_agent_data
        )
        
        if success and 'agent_id' in created_agent:
            agent_id = created_agent['agent_id']
            self.log(f"   🤖 Created agent: {agent_id}")
            
            # Test deleting the custom agent
            self.run_test(
                "Delete Custom Agent",
                "DELETE",
                f"agents/{agent_id}",
                200
            )
        
        return True

    def test_chat_endpoints(self):
        """Test chat functionality"""
        self.log("\n=== CHAT TESTS ===")
        
        # Get agents first
        success, agents_data = self.run_test("Get Agents for Chat", "GET", "agents", 200)
        if not success or not agents_data:
            return False
            
        agents = agents_data if isinstance(agents_data, list) else []
        if not agents:
            self.log("❌ No agents available for chat testing")
            return False
            
        agent_id = agents[0]['agent_id']
        
        # Create a chat
        success, chat_data = self.run_test(
            "Create Chat",
            "POST",
            "chats",
            200,
            data={"agent_id": agent_id, "title": "Test Chat"}
        )
        
        if not success or 'chat_id' not in chat_data:
            return False
            
        chat_id = chat_data['chat_id']
        self.log(f"   💬 Created chat: {chat_id}")
        
        # Get all chats
        self.run_test("Get All Chats", "GET", "chats", 200)
        
        # Get specific chat
        self.run_test("Get Chat Details", "GET", f"chats/{chat_id}", 200)
        
        # Send a message (this tests LLM integration)
        self.log("   🤖 Testing AI message generation...")
        success, message_response = self.run_test(
            "Send Message to Agent",
            "POST",
            f"chats/{chat_id}/messages",
            200,
            data={"content": "Hello, this is a test message. Please respond briefly."}
        )
        
        if success:
            self.log("   ✨ AI response generated successfully")
        else:
            self.log("   ⚠️  AI integration may have issues")
        
        # Delete the chat
        self.run_test("Delete Chat", "DELETE", f"chats/{chat_id}", 200)
        
        return True

    def test_tasks_endpoints(self):
        """Test task management endpoints"""
        self.log("\n=== TASKS TESTS ===")
        
        # Get agents for task assignment
        success, agents_data = self.run_test("Get Agents for Tasks", "GET", "agents", 200)
        if not success:
            return False
            
        agents = agents_data if isinstance(agents_data, list) else []
        agent_ids = [a['agent_id'] for a in agents[:2]]  # Use first 2 agents
        
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "This is a test task to validate the API functionality.",
            "priority": "medium",
            "assigned_agents": agent_ids
        }
        
        success, created_task = self.run_test(
            "Create Task",
            "POST",
            "tasks",
            200,
            data=task_data
        )
        
        if not success or 'task_id' not in created_task:
            return False
            
        task_id = created_task['task_id']
        self.log(f"   📝 Created task: {task_id}")
        
        # Get all tasks
        self.run_test("Get All Tasks", "GET", "tasks", 200)
        
        # Update task
        self.run_test(
            "Update Task",
            "PATCH",
            f"tasks/{task_id}",
            200,
            data={"status": "in_progress"}
        )
        
        # Test task execution (this tests LLM integration)
        if agent_ids:
            self.log("   🚀 Testing task execution with AI agents...")
            success, execution_result = self.run_test(
                "Execute Task",
                "POST",
                f"tasks/{task_id}/execute",
                200
            )
            
            if success:
                self.log("   ✨ Task execution completed successfully")
            else:
                self.log("   ⚠️  Task execution may have issues")
        
        # Delete task
        self.run_test("Delete Task", "DELETE", f"tasks/{task_id}", 200)
        
        return True

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        self.log("\n=== STATS TESTS ===")
        
        success, stats_data = self.run_test("Get User Stats", "GET", "stats", 200)
        
        if success:
            expected_keys = ['total_chats', 'total_tasks', 'completed_tasks', 'custom_agents', 'total_messages']
            missing_keys = [key for key in expected_keys if key not in stats_data]
            
            if missing_keys:
                self.log(f"   ⚠️  Missing stats keys: {missing_keys}")
            else:
                self.log(f"   📊 Stats: {stats_data}")
        
        return success

    def test_logout(self):
        """Test logout"""
        self.log("\n=== LOGOUT TEST ===")
        return self.run_test("User Logout", "POST", "auth/logout", 200)[0]

    def run_all_tests(self):
        """Run comprehensive API tests"""
        self.log("🚀 Starting Nexus AI Backend API Tests")
        self.log(f"🌐 Testing against: {self.base_url}")
        
        start_time = time.time()
        
        # Test authentication first
        if not self.test_auth_flow():
            self.log("❌ Authentication failed - stopping tests")
            return False
        
        # Run all other tests
        test_results = [
            self.test_agents_endpoints(),
            self.test_chat_endpoints(), 
            self.test_tasks_endpoints(),
            self.test_stats_endpoint(),
            self.test_logout()
        ]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        self.log(f"\n{'='*50}")
        self.log(f"📊 TEST SUMMARY")
        self.log(f"{'='*50}")
        self.log(f"⏱️  Total time: {duration:.2f}s")
        self.log(f"✅ Tests passed: {self.tests_passed}/{self.tests_run}")
        self.log(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed!")
            return True
        else:
            self.log("⚠️  Some tests failed - check logs above")
            return False

def main():
    tester = NexusAIBackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())