#!/usr/bin/env python3
# services/engine-python/tests/test_processor.py
"""Tests for the Processor class."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from server import Processor


class TestProcessor:
    """Test cases for Processor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = Processor()

    def test_process_default_mode(self):
        """Test processing with default mode."""
        result = self.processor.process('hello world', {})
        assert 'output' in result
        assert 'metadata' in result
        assert result['output'] == 'Processed: hello world'

    def test_process_uppercase_mode(self):
        """Test processing with uppercase mode."""
        result = self.processor.process('hello world', {'mode': 'uppercase'})
        assert result['output'] == 'HELLO WORLD'

    def test_process_lowercase_mode(self):
        """Test processing with lowercase mode."""
        result = self.processor.process('HELLO WORLD', {'mode': 'lowercase'})
        assert result['output'] == 'hello world'

    def test_process_reverse_mode(self):
        """Test processing with reverse mode."""
        result = self.processor.process('hello', {'mode': 'reverse'})
        assert result['output'] == 'olleh'

    def test_metadata_contains_required_fields(self):
        """Test that metadata contains required fields."""
        result = self.processor.process('test', {})
        metadata = result['metadata']

        assert 'version' in metadata
        assert 'processed_at' in metadata
        assert 'input_length' in metadata
        assert 'output_length' in metadata

    def test_metadata_input_length(self):
        """Test that input length is correctly recorded."""
        input_data = 'test input'
        result = self.processor.process(input_data, {})
        assert result['metadata']['input_length'] == str(len(input_data))

    def test_empty_input(self):
        """Test processing empty input."""
        result = self.processor.process('', {})
        assert result['output'] == 'Processed: '

    def test_unicode_input(self):
        """Test processing unicode input."""
        result = self.processor.process('測試中文', {'mode': 'reverse'})
        assert result['output'] == '文中試測'
