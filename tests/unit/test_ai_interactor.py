"""
Unit Tests for AIInteractor
============================

Tests the AIInteractor fallback hierarchy with mocked Playwright page.

Test Coverage:
- safe_fill() with all fallback methods
- safe_click() with all fallback methods  
- Interaction logging and statistics
- Error handling and degraded mode

Author: Ram
Date: November 12, 2025
Phase: 7 - Universal Interactor
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from core.ai_interactor import AIInteractor, create_interactor


class TestAIInteractorFill:
    """Test safe_fill() method with various scenarios."""
    
    def test_fill_direct_success(self):
        """Test successful fill using direct method (page.fill)."""
        # Arrange
        page = Mock()
        page.fill = Mock()  # Direct fill succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_fill("#username", "testuser", "username field")
        
        # Assert
        assert result is True
        page.fill.assert_called_once_with("#username", "testuser", timeout=5000)
        
        stats = interactor.get_interaction_stats()
        assert stats['direct'] == 1
        assert stats['js_inject'] == 0
        assert stats['human_typing'] == 0
        assert stats['degraded'] == 0
    
    def test_fill_fallback_to_js_inject(self):
        """Test fill falling back to JS injection when direct fails."""
        # Arrange
        page = Mock()
        page.fill = Mock(side_effect=Exception("Direct fill blocked"))
        page.evaluate = Mock(return_value=True)  # JS injection succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_fill("#username", "testuser")
        
        # Assert
        assert result is True
        page.fill.assert_called_once()  # Attempted direct
        page.evaluate.assert_called_once()  # Fell back to JS
        
        stats = interactor.get_interaction_stats()
        assert stats['js_inject'] == 1
        assert stats['direct'] == 0
    
    def test_fill_fallback_to_human_typing(self):
        """Test fill falling back to human typing when JS fails."""
        # Arrange
        page = Mock()
        page.fill = Mock(side_effect=Exception("Direct fill blocked"))
        page.evaluate = Mock(return_value=False)  # JS injection fails
        page.focus = Mock()
        page.type = Mock()  # Human typing succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_fill("#username", "test")
        
        # Assert
        assert result is True
        page.fill.assert_called()  # Attempted direct and clear
        page.evaluate.assert_called_once()  # Attempted JS
        page.focus.assert_called()
        assert page.type.call_count == 4  # 4 characters typed
        
        stats = interactor.get_interaction_stats()
        assert stats['human_typing'] == 1
    
    def test_fill_degraded_all_methods_fail(self):
        """Test degraded mode when all fill methods fail."""
        # Arrange
        page = Mock()
        page.fill = Mock(side_effect=Exception("Blocked"))
        page.evaluate = Mock(return_value=False)
        page.focus = Mock(side_effect=Exception("Focus blocked"))
        page.type = Mock(side_effect=Exception("Type blocked"))
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_fill("#username", "testuser")
        
        # Assert
        assert result is False
        
        stats = interactor.get_interaction_stats()
        assert stats['degraded'] == 1
        
        # Check interaction log
        log = interactor.get_interaction_log()
        assert len(log) == 1
        assert log[0]['interaction_method'] == 'degraded'
        assert log[0]['failed'] is True


class TestAIInteractorClick:
    """Test safe_click() method with various scenarios."""
    
    def test_click_direct_success(self):
        """Test successful click using direct method (page.click)."""
        # Arrange
        page = Mock()
        page.click = Mock()  # Direct click succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_click("button[type='submit']", "login button")
        
        # Assert
        assert result is True
        page.click.assert_called_once()
        
        stats = interactor.get_interaction_stats()
        assert stats['direct'] == 1
    
    def test_click_fallback_to_js_click(self):
        """Test click falling back to JS click when direct fails."""
        # Arrange
        page = Mock()
        page.click = Mock(side_effect=Exception("Click blocked"))
        page.evaluate = Mock(return_value=True)  # JS click succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_click("button")
        
        # Assert
        assert result is True
        page.click.assert_called_once()
        page.evaluate.assert_called_once()
        
        stats = interactor.get_interaction_stats()
        assert stats['js_inject'] == 1
    
    def test_click_fallback_to_enter_key(self):
        """Test click falling back to Enter key when JS fails."""
        # Arrange
        page = Mock()
        page.click = Mock(side_effect=Exception("Click blocked"))
        page.evaluate = Mock(return_value=False)  # JS click fails
        page.focus = Mock()
        page.keyboard = Mock()
        page.keyboard.press = Mock()  # Enter key succeeds
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_click("button")
        
        # Assert
        assert result is True
        page.focus.assert_called_once()
        page.keyboard.press.assert_called_with("Enter")
        
        stats = interactor.get_interaction_stats()
        assert stats['human_typing'] == 1
    
    def test_click_degraded_all_methods_fail(self):
        """Test degraded mode when all click methods fail."""
        # Arrange
        page = Mock()
        page.click = Mock(side_effect=Exception("Blocked"))
        page.evaluate = Mock(side_effect=Exception("JS blocked"))
        page.focus = Mock(side_effect=Exception("Focus blocked"))
        page.keyboard = Mock()
        page.keyboard.press = Mock(side_effect=Exception("Key blocked"))
        
        interactor = AIInteractor(page, timeout=5000)
        
        # Act
        result = interactor.safe_click("button")
        
        # Assert
        assert result is False
        
        stats = interactor.get_interaction_stats()
        assert stats['degraded'] == 1


class TestAIInteractorLogging:
    """Test interaction logging and statistics."""
    
    def test_interaction_log_contains_all_fields(self):
        """Test that interaction log contains all required fields."""
        # Arrange
        page = Mock()
        page.fill = Mock()
        
        interactor = AIInteractor(page)
        
        # Act
        interactor.safe_fill("#test", "value", "test field")
        
        # Assert
        log = interactor.get_interaction_log()
        assert len(log) == 1
        
        entry = log[0]
        assert 'interaction_method' in entry
        assert 'interaction_latency_ms' in entry
        assert 'selector' in entry
        assert 'context' in entry
        assert 'timestamp' in entry
        assert 'failed' in entry
        
        assert entry['interaction_method'] == 'direct'
        assert entry['selector'] == '#test'
        assert entry['context'] == 'test field'
        assert entry['failed'] is False
    
    def test_get_interaction_stats_multiple_methods(self):
        """Test interaction statistics with multiple method types."""
        # Arrange
        page = Mock()
        page.fill = Mock()  # Direct succeeds
        page.click = Mock(side_effect=Exception("Blocked"))
        page.evaluate = Mock(return_value=True)  # JS succeeds
        
        interactor = AIInteractor(page)
        
        # Act
        interactor.safe_fill("#field1", "value1")  # direct
        interactor.safe_fill("#field2", "value2")  # direct
        interactor.safe_click("#button1")  # js_inject
        
        # Assert
        stats = interactor.get_interaction_stats()
        assert stats['direct'] == 2
        assert stats['js_inject'] == 1
        assert stats['human_typing'] == 0
        assert stats['degraded'] == 0
    
    def test_clear_log(self):
        """Test clearing interaction log."""
        # Arrange
        page = Mock()
        page.fill = Mock()
        
        interactor = AIInteractor(page)
        interactor.safe_fill("#test", "value")
        
        assert len(interactor.get_interaction_log()) == 1
        
        # Act
        interactor.clear_log()
        
        # Assert
        assert len(interactor.get_interaction_log()) == 0
        
        stats = interactor.get_interaction_stats()
        assert all(count == 0 for count in stats.values())


class TestAIInteractorNavigation:
    """Test safe_navigate() method."""
    
    def test_navigate_success(self):
        """Test successful navigation."""
        # Arrange
        page = Mock()
        page.goto = Mock()
        
        interactor = AIInteractor(page)
        
        # Act
        result = interactor.safe_navigate("https://example.com")
        
        # Assert
        assert result is True
        page.goto.assert_called_once()
        
        stats = interactor.get_interaction_stats()
        assert stats['direct'] == 1
    
    def test_navigate_failure(self):
        """Test navigation failure."""
        # Arrange
        page = Mock()
        page.goto = Mock(side_effect=Exception("Network error"))
        
        interactor = AIInteractor(page)
        
        # Act
        result = interactor.safe_navigate("https://example.com")
        
        # Assert
        assert result is False
        
        stats = interactor.get_interaction_stats()
        assert stats['degraded'] == 1


class TestAIInteractorFactory:
    """Test factory function."""
    
    def test_create_interactor(self):
        """Test creating interactor with factory function."""
        # Arrange
        page = Mock()
        
        # Act
        interactor = create_interactor(page, timeout=3000)
        
        # Assert
        assert isinstance(interactor, AIInteractor)
        assert interactor.page is page
        assert interactor.timeout == 3.0  # Converted to seconds


# Run tests with: pytest -q tests/unit/test_ai_interactor.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
