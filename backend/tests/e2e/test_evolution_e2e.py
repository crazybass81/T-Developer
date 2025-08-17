"""End-to-end tests for Evolution system using Python."""

import asyncio
import json
import time
from typing import Any, Dict, Optional

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestEvolutionE2E:
    """E2E tests for Evolution system."""

    @classmethod
    def setup_class(cls):
        """Set up browser driver."""
        # Use headless Chrome for CI
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://localhost:3000"
        cls.api_url = "http://localhost:8000/api"

    @classmethod
    def teardown_class(cls):
        """Clean up browser driver."""
        cls.driver.quit()

    def test_evolution_page_loads(self):
        """Test that evolution page loads correctly."""
        self.driver.get(f"{self.base_url}/evolution")
        
        # Wait for page to load
        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Self-Evolution System')]"))
        )
        assert title is not None
        
        # Check for control panel
        control_panel = self.driver.find_element(By.ID, "evolution-control")
        assert control_panel is not None

    def test_start_evolution_cycle(self):
        """Test starting an evolution cycle."""
        self.driver.get(f"{self.base_url}/evolution")
        
        # Fill in configuration
        target_path = self.driver.find_element(By.NAME, "targetPath")
        target_path.clear()
        target_path.send_keys("/backend/packages")
        
        max_cycles = self.driver.find_element(By.NAME, "maxCycles")
        max_cycles.clear()
        max_cycles.send_keys("5")
        
        # Click start button
        start_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Start Evolution')]")
        start_button.click()
        
        # Wait for success message
        time.sleep(2)
        
        # Check status
        status = self.driver.find_element(By.ID, "evolution-status")
        assert "running" in status.text.lower()

    def test_stop_evolution_cycle(self):
        """Test stopping an evolution cycle."""
        # First start an evolution
        self.test_start_evolution_cycle()
        
        # Click stop button
        stop_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Stop Evolution')]"))
        )
        stop_button.click()
        
        # Wait for status change
        time.sleep(2)
        
        # Check status
        status = self.driver.find_element(By.ID, "evolution-status")
        assert "stopped" in status.text.lower()

    def test_evolution_history_display(self):
        """Test that evolution history is displayed."""
        self.driver.get(f"{self.base_url}/evolution")
        
        # Check for history section
        history = self.driver.find_element(By.ID, "evolution-history")
        assert history is not None
        
        # Check for history title
        history_title = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Evolution History')]")
        assert history_title is not None


class TestAgentsE2E:
    """E2E tests for Agent management."""

    @classmethod
    def setup_class(cls):
        """Set up browser driver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://localhost:3000"

    @classmethod
    def teardown_class(cls):
        """Clean up browser driver."""
        cls.driver.quit()

    def test_agents_page_loads(self):
        """Test that agents page loads correctly."""
        self.driver.get(f"{self.base_url}/agents")
        
        # Wait for page title
        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Agents Management')]"))
        )
        assert title is not None

    def test_create_agent(self):
        """Test creating a new agent."""
        self.driver.get(f"{self.base_url}/agents")
        
        # Click create button
        create_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Agent')]")
        create_button.click()
        
        # Wait for dialog
        time.sleep(1)
        
        # Fill form
        agent_name = self.driver.find_element(By.NAME, "agentName")
        agent_name.send_keys("TestAgent")
        
        # Select type
        agent_type = self.driver.find_element(By.NAME, "agentType")
        agent_type.send_keys("planner")
        
        # Submit
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
        submit_button.click()
        
        # Wait for success
        time.sleep(2)
        
        # Check if agent appears in list
        agent_card = self.driver.find_element(By.XPATH, "//*[contains(text(), 'TestAgent')]")
        assert agent_card is not None

    def test_start_agent(self):
        """Test starting an agent."""
        self.driver.get(f"{self.base_url}/agents")
        
        # Find first agent card
        agent_cards = self.driver.find_elements(By.CLASS_NAME, "agent-card")
        if agent_cards:
            # Click start button
            start_button = agent_cards[0].find_element(By.XPATH, ".//button[@aria-label='Start']")
            start_button.click()
            
            # Wait for status change
            time.sleep(2)
            
            # Check status
            status = agent_cards[0].find_element(By.CLASS_NAME, "agent-status")
            assert "running" in status.text.lower()


class TestAPIEndpoints:
    """E2E tests for API endpoints."""

    def setup_method(self):
        """Set up API client."""
        self.base_url = "http://localhost:8000/api"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test-api-key"
        }

    def test_evolution_start_endpoint(self):
        """Test evolution start endpoint."""
        payload = {
            "target_path": "/backend/packages",
            "max_cycles": 3,
            "min_improvement": 0.05,
            "safety_checks": True,
            "dry_run": True
        }
        
        response = requests.post(
            f"{self.base_url}/evolution/start",
            json=payload,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "evolution_id" in data
        assert data["status"] == "running"

    def test_agents_list_endpoint(self):
        """Test agents list endpoint."""
        response = requests.get(
            f"{self.base_url}/agents",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_metrics_summary_endpoint(self):
        """Test metrics summary endpoint."""
        response = requests.get(
            f"{self.base_url}/metrics/summary",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data
        assert "health" in data

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        import websockets
        
        uri = "ws://localhost:8000/ws"
        
        async with websockets.connect(uri) as websocket:
            # Send test message
            await websocket.send(json.dumps({
                "type": "ping",
                "timestamp": time.time()
            }))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            assert data is not None


class TestFullWorkflow:
    """E2E tests for complete workflow."""

    def setup_method(self):
        """Set up test environment."""
        self.api_url = "http://localhost:8000/api"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test-api-key"
        }

    def test_complete_evolution_workflow(self):
        """Test complete evolution workflow from start to finish."""
        # 1. Create agent
        agent_response = requests.post(
            f"{self.api_url}/agents/create",
            json={
                "name": "E2ETestAgent",
                "type": "research",
                "config": {}
            },
            headers=self.headers
        )
        assert agent_response.status_code == 201
        agent_id = agent_response.json()["agent_id"]
        
        # 2. Start evolution
        evolution_response = requests.post(
            f"{self.api_url}/evolution/start",
            json={
                "target_path": "/test/path",
                "max_cycles": 1,
                "dry_run": True
            },
            headers=self.headers
        )
        assert evolution_response.status_code == 200
        evolution_id = evolution_response.json()["evolution_id"]
        
        # 3. Check evolution status
        time.sleep(2)
        status_response = requests.get(
            f"{self.api_url}/evolution/{evolution_id}",
            headers=self.headers
        )
        assert status_response.status_code == 200
        
        # 4. Get metrics
        metrics_response = requests.get(
            f"{self.api_url}/metrics",
            headers=self.headers
        )
        assert metrics_response.status_code == 200
        
        # 5. Stop evolution
        stop_response = requests.post(
            f"{self.api_url}/evolution/stop",
            json={"evolution_id": evolution_id},
            headers=self.headers
        )
        assert stop_response.status_code == 200
        
        # 6. Clean up - disable agent
        cleanup_response = requests.delete(
            f"{self.api_url}/agents/{agent_id}",
            headers=self.headers
        )
        assert cleanup_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])