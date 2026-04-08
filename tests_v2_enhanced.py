"""Comprehensive test suite for LUNAR v2 with enhanced efficiency metrics."""

import pytest
import json
from warehouse_env.warehouse_env.env import WarehouseEnv
from warehouse_env.warehouse_env.graders_enhanced import get_grader
from warehouse_env.warehouse_env.session_manager_hybrid import SessionManager
from warehouse_env.warehouse_env.sandbox import SandboxExecutor
from warehouse_env.warehouse_env.task_config import TASK_VARIANTS, get_task_info


class TestTaskExpansion:
    """Test 31 task variants (expanded from 21)."""
    
    def test_task_count(self):
        """Verify 31 total tasks."""
        assert len(TASK_VARIANTS) == 31, f"Expected 31 tasks, got {len(TASK_VARIANTS)}"
    
    def test_warehouse_tasks(self):
        """Verify 10 warehouse tasks."""
        warehouse_tasks = {k: v for k, v in TASK_VARIANTS.items() 
                          if v.get('domain') == 'warehouse'}
        assert len(warehouse_tasks) == 10
    
    def test_supply_chain_tasks(self):
        """Verify 7 supply chain tasks."""
        sc_tasks = {k: v for k, v in TASK_VARIANTS.items() 
                   if v.get('domain') == 'supply_chain'}
        assert len(sc_tasks) == 7
    
    def test_forecasting_tasks(self):
        """Verify 6 forecasting tasks."""
        fc_tasks = {k: v for k, v in TASK_VARIANTS.items() 
                   if v.get('domain') == 'forecasting'}
        assert len(fc_tasks) == 6
    
    def test_production_tasks(self):
        """Verify 6 production tasks."""
        prod_tasks = {k: v for k, v in TASK_VARIANTS.items() 
                     if v.get('domain') == 'production'}
        assert len(prod_tasks) == 6
    
    def test_resource_tasks(self):
        """Verify 5 resource tasks."""
        res_tasks = {k: v for k, v in TASK_VARIANTS.items() 
                    if v.get('domain') == 'resources'}
        assert len(res_tasks) == 5
    
    def test_difficulty_distribution(self):
        """Test proper difficulty distribution."""
        easy = sum(1 for v in TASK_VARIANTS.values() if v.get('difficulty') == 'easy')
        medium = sum(1 for v in TASK_VARIANTS.values() if v.get('difficulty') == 'medium')
        hard = sum(1 for v in TASK_VARIANTS.values() if v.get('difficulty') == 'hard')
        
        assert easy >= 7, "Should have at least 7 easy tasks"
        assert medium >= 10, "Should have at least 10 medium tasks"
        assert hard >= 10, "Should have at least 10 hard tasks"


class TestEnhancedRewardScale:
    """Test 0.1-1.0 never-binary reward system."""
    
    def test_reward_range(self):
        """Verify rewards never go below 0.1 (no binary zero)."""
        grader = get_grader('warehouse')
        
        # Create dummy state
        class DummyState:
            warehouse_levels = [100, 200, 300]
            shortage_penalty = 10000.0
            holding_costs = 5000.0
            last_action_error = None
        
        # Test with poor performance
        result = grader.grade(DummyState(), [0.1, 0.15, 0.2], 
                             {'num_warehouses': 3})
        
        assert result['score'] >= 0.1, "Score should never be below 0.1"
        assert result['score'] <= 1.0, "Score should never exceed 1.0"
    
    def test_domain_specific_grading(self):
        """Test that each domain has specialized grading."""
        for domain in ['warehouse', 'supply_chain', 'forecasting', 'production']:
            grader = get_grader(domain)
            assert grader is not None
            assert hasattr(grader, 'grade')
    
    def test_partial_credit_feedback(self):
        """Test detailed feedback generation."""
        grader = get_grader('warehouse')
        
        class DummyState:
            warehouse_levels = [500]
            shortage_penalty = 1000.0
            holding_costs = 2000.0
            last_action_error = None
        
        result = grader.grade(DummyState(), [0.5, 0.6, 0.7],
                             {'num_warehouses': 1})
        
        assert 'feedback' in result
        assert len(result['feedback']) > 0


class TestSessionPersistence:
    """Test SQLite-based multi-worker session persistence."""
    
    def test_session_creation(self):
        """Test session creation and persistence."""
        manager = SessionManager(db_path=":memory:")  # Use in-memory DB for testing
        
        session_id = manager.create_session('warehouse_easy')
        assert session_id is not None
        assert len(session_id) == 36  # UUID format
    
    def test_session_persistence(self):
        """Test data persists to database."""
        manager = SessionManager(db_path=":memory:")
        
        session_id = manager.create_session('warehouse_medium')
        manager.record_reward(session_id, 0.75)
        manager.record_reward(session_id, 0.80)
        
        # Verify rewards persisted
        meta = manager.get_metadata(session_id)
        assert meta['steps'] == 2
        assert meta['best_reward'] == 0.80
    
    def test_leaderboard(self):
        """Test leaderboard functionality."""
        manager = SessionManager(db_path=":memory:")
        
        sid1 = manager.create_session('warehouse_easy')
        sid2 = manager.create_session('warehouse_medium')
        
        manager.record_reward(sid1, 0.8)
        manager.record_reward(sid2, 0.9)
        
        leaderboard = manager.get_leaderboard(limit=10)
        assert len(leaderboard) == 2
        assert leaderboard[0]['best_reward'] == 0.9


class TestSandboxExecution:
    """Test safe code execution sandbox."""
    
    def test_safe_execution(self):
        """Test safe code executes without error."""
        executor = SandboxExecutor(timeout_sec=5)
        
        code = """
result = sum([1, 2, 3, 4, 5])
"""
        success, output, error = executor.execute_action(code)
        assert success
        assert error is None
    
    def test_timeout_protection(self):
        """Test execution timeout protection."""
        executor = SandboxExecutor(timeout_sec=1)
        
        code = """
import time
time.sleep(10)
result = 42
"""
        success, output, error = executor.execute_action(code)
        # Should fail due to import restrictions or timeout
        assert not success
    
    def test_restricted_operations(self):
        """Test that dangerous operations are blocked."""
        executor = SandboxExecutor()
        
        code = "open('/etc/passwd')"
        is_safe, reason = executor.validate_action(code)
        assert not is_safe


class TestDifficultyProgression:
    """Test difficulty progression across tasks."""
    
    def test_episode_length_progression(self):
        """Easy < Medium < Hard episode lengths."""
        easy_max_steps = []
        med_max_steps = []
        hard_max_steps = []
        
        for task_id, config in TASK_VARIANTS.items():
            max_steps = config.get('max_steps', 0)
            difficulty = config.get('difficulty', '')
            
            if difficulty == 'easy':
                easy_max_steps.append(max_steps)
            elif difficulty == 'medium':
                med_max_steps.append(max_steps)
            elif difficulty == 'hard':
                hard_max_steps.append(max_steps)
        
        avg_easy = sum(easy_max_steps) / len(easy_max_steps)
        avg_med = sum(med_max_steps) / len(med_max_steps)
        avg_hard = sum(hard_max_steps) / len(hard_max_steps)
        
        assert avg_easy < avg_med < avg_hard


class TestMultiDomainCoverage:
    """Test coverage across all domains."""
    
    def test_all_domains_present(self):
        """Verify all 5 domains are covered."""
        domains = set(v.get('domain') for v in TASK_VARIANTS.values())
        required_domains = {'warehouse', 'supply_chain', 'forecasting', 
                           'production', 'resources'}
        assert required_domains.issubset(domains)
    
    def test_domain_variety(self):
        """Test within-domain variety."""
        for domain in ['warehouse', 'supply_chain', 'forecasting', 'production']:
            domain_tasks = [v for v in TASK_VARIANTS.values() 
                           if v.get('domain') == domain]
            difficulties = set(v.get('difficulty') for v in domain_tasks)
            
            # Each domain should have easy, medium, or hard
            assert len(difficulties) >= 2, f"{domain} lacks difficulty variety"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
