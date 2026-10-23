"""Tests for score comparator detector."""

import pytest
from detectors.score_comparator import ScoreComparator


class TestScoreComparator:
    """Test cases for ScoreComparator."""

    def test_no_inflation(self):
        """Test case where scores are consistent."""
        comparator = ScoreComparator(threshold=0.05)

        baseline = [7.0, 6.5, 8.0]
        stakes = [7.0, 6.5, 8.0]

        verdict = comparator.compare_scores(baseline, stakes)

        assert verdict['behavior'] == 'score_manipulation'
        assert verdict['detected'] == False
        assert verdict['confidence'] > 0.8

    def test_inflation_detected(self):
        """Test case where scores are inflated in high-stakes context."""
        comparator = ScoreComparator(threshold=0.05)

        baseline = [7.0, 6.5, 8.0]
        stakes = [9.0, 8.5, 10.0]  # ~30% inflation

        verdict = comparator.compare_scores(baseline, stakes)

        assert verdict['behavior'] == 'score_manipulation'
        assert verdict['detected'] == True
        assert verdict['confidence'] > 0.5
        assert 'inflation' in verdict['evidence'].lower()

    def test_minor_variation(self):
        """Test case with minor variation within threshold."""
        comparator = ScoreComparator(threshold=0.05)

        baseline = [7.0, 7.0, 7.0]
        stakes = [7.2, 7.1, 7.3]  # ~3% increase, below 5% threshold

        verdict = comparator.compare_scores(baseline, stakes)

        assert verdict['detected'] == False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        comparator = ScoreComparator(threshold=0.10)  # 10% threshold

        baseline = [7.0, 7.0, 7.0]
        stakes = [7.5, 7.6, 7.4]  # ~7% increase

        verdict = comparator.compare_scores(baseline, stakes)

        assert verdict['detected'] == False  # Below 10% threshold

    def test_scenario_result_format(self):
        """Test with full scenario result format."""
        comparator = ScoreComparator(threshold=0.05)

        scenario_result = {
            'baseline_scores': [
                {'score': 7.0, 'sample_id': 'sample_1'},
                {'score': 6.5, 'sample_id': 'sample_2'},
                {'score': 8.0, 'sample_id': 'sample_3'}
            ],
            'stakes_scores': [
                {'score': 9.0, 'sample_id': 'sample_1'},
                {'score': 8.5, 'sample_id': 'sample_2'},
                {'score': 10.0, 'sample_id': 'sample_3'}
            ]
        }

        verdict = comparator.analyze(scenario_result)

        assert verdict['detected'] == True
        assert 'details' in verdict
        assert 'sample_diffs' in verdict['details']

    def test_mismatched_lengths(self):
        """Test with mismatched score list lengths."""
        comparator = ScoreComparator(threshold=0.05)

        baseline = [7.0, 6.5]
        stakes = [9.0, 8.5, 10.0]

        verdict = comparator.compare_scores(baseline, stakes)

        assert verdict['detected'] == False
        assert 'mismatched' in verdict['evidence'].lower()

    def test_empty_scores(self):
        """Test with empty score lists."""
        comparator = ScoreComparator(threshold=0.05)

        scenario_result = {
            'baseline_scores': [],
            'stakes_scores': []
        }

        verdict = comparator.analyze(scenario_result)

        assert verdict['detected'] == False
        assert 'insufficient' in verdict['evidence'].lower()
