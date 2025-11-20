"""
E2E Testing with Playwright
"""
import pytest
from playwright.async_api import async_playwright, Page, Browser
import asyncio


@pytest.fixture(scope="session")
async def browser():
    """Create browser instance for tests"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser: Browser):
    """Create new page for each test"""
    page = await browser.new_page()
    yield page
    await page.close()


class TestAuthentication:
    """E2E tests for authentication flow"""
    
    @pytest.mark.asyncio
    async def test_login_flow(self, page: Page):
        """Test user login process"""
        # Navigate to login page
        await page.goto("http://localhost:3000/login")
        
        # Fill login form
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "testpassword123")
        
        # Click login button
        await page.click('button[type="submit"]')
        
        # Wait for navigation to dashboard
        await page.wait_for_url("**/dashboard")
        
        # Verify user is logged in
        assert await page.is_visible('text=Welcome')
    
    @pytest.mark.asyncio
    async def test_register_flow(self, page: Page):
        """Test user registration process"""
        await page.goto("http://localhost:3000/register")
        
        # Fill registration form
        await page.fill('input[name="username"]', f"testuser_{int(asyncio.get_event_loop().time())}")
        await page.fill('input[name="email"]', f"test_{int(asyncio.get_event_loop().time())}@example.com")
        await page.fill('input[name="password"]', "SecurePass123!")
        await page.fill('input[name="confirmPassword"]', "SecurePass123!")
        
        # Submit form
        await page.click('button[type="submit"]')
        
        # Wait for success message or redirect
        await page.wait_for_selector('text=Registration successful', timeout=5000)
    
    @pytest.mark.asyncio
    async def test_logout_flow(self, page: Page):
        """Test user logout"""
        # Login first
        await page.goto("http://localhost:3000/login")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "testpassword123")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard")
        
        # Click logout button
        await page.click('button:has-text("Logout")')
        
        # Verify redirected to login
        await page.wait_for_url("**/login")


class TestBugReporting:
    """E2E tests for bug reporting"""
    
    @pytest.mark.asyncio
    async def test_submit_bug_report(self, page: Page):
        """Test submitting a new bug report"""
        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "testpassword123")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard")
        
        # Navigate to bug submission
        await page.goto("http://localhost:3000/bugs/new")
        
        # Fill bug report form
        await page.fill('input[name="title"]', "Test SQL Injection Vulnerability")
        await page.fill('textarea[name="description"]', "Found SQL injection in login form")
        await page.select_option('select[name="severity"]', "high")
        await page.fill('input[name="targetUrl"]', "https://example.com/login")
        await page.fill('textarea[name="poc"]', "' OR '1'='1")
        
        # Submit
        await page.click('button[type="submit"]')
        
        # Verify success
        await page.wait_for_selector('text=Bug submitted successfully')
    
    @pytest.mark.asyncio
    async def test_view_bug_list(self, page: Page):
        """Test viewing bug list"""
        await page.goto("http://localhost:3000/bugs")
        
        # Wait for bugs to load
        await page.wait_for_selector('[data-testid="bug-list"]')
        
        # Verify bugs are displayed
        bug_items = await page.query_selector_all('[data-testid="bug-item"]')
        assert len(bug_items) > 0
    
    @pytest.mark.asyncio
    async def test_filter_bugs(self, page: Page):
        """Test filtering bugs by severity"""
        await page.goto("http://localhost:3000/bugs")
        
        # Select critical filter
        await page.select_option('select[name="severity"]', "critical")
        
        # Wait for filtered results
        await page.wait_for_timeout(1000)
        
        # Verify only critical bugs shown
        critical_badges = await page.query_selector_all('text=Critical')
        assert len(critical_badges) > 0


class TestScanning:
    """E2E tests for security scanning"""
    
    @pytest.mark.asyncio
    async def test_start_scan(self, page: Page):
        """Test starting a security scan"""
        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "testpassword123")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard")
        
        # Navigate to scans
        await page.goto("http://localhost:3000/scans/new")
        
        # Fill scan form
        await page.fill('input[name="targetUrl"]', "https://example.com")
        await page.select_option('select[name="scanType"]', "quick")
        
        # Start scan
        await page.click('button:has-text("Start Scan")')
        
        # Verify scan started
        await page.wait_for_selector('text=Scan started')
    
    @pytest.mark.asyncio
    async def test_view_scan_results(self, page: Page):
        """Test viewing scan results"""
        await page.goto("http://localhost:3000/scans")
        
        # Click on first scan
        await page.click('[data-testid="scan-item"]:first-child')
        
        # Wait for results page
        await page.wait_for_selector('[data-testid="scan-results"]')
        
        # Verify results displayed
        assert await page.is_visible('text=Vulnerabilities Found')


class TestMarketplace:
    """E2E tests for marketplace"""
    
    @pytest.mark.asyncio
    async def test_browse_tools(self, page: Page):
        """Test browsing marketplace tools"""
        await page.goto("http://localhost:3000/marketplace")
        
        # Wait for tools to load
        await page.wait_for_selector('[data-testid="tool-grid"]')
        
        # Verify tools are displayed
        tools = await page.query_selector_all('[data-testid="tool-card"]')
        assert len(tools) > 0
    
    @pytest.mark.asyncio
    async def test_search_tools(self, page: Page):
        """Test searching for tools"""
        await page.goto("http://localhost:3000/marketplace")
        
        # Search for scanner
        await page.fill('input[name="search"]', "scanner")
        await page.press('input[name="search"]', "Enter")
        
        # Wait for results
        await page.wait_for_timeout(1000)
        
        # Verify search results
        results = await page.query_selector_all('[data-testid="tool-card"]')
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_view_tool_details(self, page: Page):
        """Test viewing tool details"""
        await page.goto("http://localhost:3000/marketplace")
        
        # Click first tool
        await page.click('[data-testid="tool-card"]:first-child')
        
        # Wait for details page
        await page.wait_for_selector('[data-testid="tool-details"]')
        
        # Verify details displayed
        assert await page.is_visible('text=Description')
        assert await page.is_visible('text=Price')


class TestDashboard:
    """E2E tests for dashboard"""
    
    @pytest.mark.asyncio
    async def test_dashboard_loads(self, page: Page):
        """Test dashboard page loads correctly"""
        # Login
        await page.goto("http://localhost:3000/login")
        await page.fill('input[name="username"]', "testuser")
        await page.fill('input[name="password"]', "testpassword123")
        await page.click('button[type="submit"]')
        
        # Wait for dashboard
        await page.wait_for_url("**/dashboard")
        
        # Verify key elements
        assert await page.is_visible('text=Dashboard')
        assert await page.is_visible('[data-testid="stats-cards"]')
    
    @pytest.mark.asyncio
    async def test_navigation_menu(self, page: Page):
        """Test dashboard navigation"""
        await page.goto("http://localhost:3000/dashboard")
        
        # Test navigation to bugs
        await page.click('a[href="/bugs"]')
        await page.wait_for_url("**/bugs")
        
        # Back to dashboard
        await page.click('a[href="/dashboard"]')
        await page.wait_for_url("**/dashboard")
        
        # Test navigation to scans
        await page.click('a[href="/scans"]')
        await page.wait_for_url("**/scans")


class TestResponsiveness:
    """E2E tests for responsive design"""
    
    @pytest.mark.asyncio
    async def test_mobile_view(self, page: Page):
        """Test mobile responsiveness"""
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        
        await page.goto("http://localhost:3000")
        
        # Verify mobile menu
        assert await page.is_visible('[data-testid="mobile-menu-button"]')
    
    @pytest.mark.asyncio
    async def test_tablet_view(self, page: Page):
        """Test tablet responsiveness"""
        await page.set_viewport_size({"width": 768, "height": 1024})
        
        await page.goto("http://localhost:3000")
        
        # Verify layout adapts
        assert await page.is_visible('[data-testid="main-content"]')
