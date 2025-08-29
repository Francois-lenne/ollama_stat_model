"""
Unit tests for ScrapFunction module.
"""
import pytest
import pandas as pd
import requests_mock
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the Python path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ScrapFunction import check_data_quality, scrap_ollama_models, run_scraping


class TestCheckDataQuality:
    """Tests for the check_data_quality function."""
    
    def test_check_data_quality_valid_data(self):
        """Test check_data_quality with valid DataFrame."""
        # Create a valid test DataFrame
        valid_data = {
            'name': ['model1', 'model2', 'model3'],
            'pulls': ['1K', '2M', '500'],
            'sizes': [['2B', '4B'], ['7B'], ['13B', '30B']],
            'capability': [['vision'], ['text'], ['code', 'math']],
            'updated': ['2 days ago', '1 week ago', '3 days ago'],
            'current_data': ['2024-01-15 10:30:00', '2024-01-15 10:30:00', '2024-01-15 10:30:00']
        }
        df = pd.DataFrame(valid_data)
        
        # This should not raise any exception
        try:
            check_data_quality(df)
        except Exception as e:
            pytest.fail(f"check_data_quality raised an unexpected exception: {e}")
    
    def test_check_data_quality_with_duplicates(self):
        """Test check_data_quality detects duplicate model names."""
        # Create a DataFrame with duplicate names
        duplicate_data = {
            'name': ['model1', 'model2', 'model1'],  # duplicate 'model1'
            'pulls': ['1K', '2M', '500'],
            'sizes': [['2B', '4B'], ['7B'], ['13B', '30B']],
            'capability': [['vision'], ['text'], ['code', 'math']],
            'updated': ['2 days ago', '1 week ago', '3 days ago'],
            'current_data': ['2024-01-15 10:30:00', '2024-01-15 10:30:00', '2024-01-15 10:30:00']
        }
        df = pd.DataFrame(duplicate_data)
        
        # Should raise ValueError for duplicates
        with pytest.raises(ValueError, match="Doublons trouvés dans la colonne 'name'"):
            check_data_quality(df)
    
    def test_check_data_quality_wrong_name_type(self):
        """Test check_data_quality detects wrong type for name column."""
        # Create a DataFrame with wrong type for name
        wrong_type_data = {
            'name': ['model1', 123, 'model3'],  # 123 is not a string
            'pulls': ['1K', '2M', '500'],
            'sizes': [['2B', '4B'], ['7B'], ['13B', '30B']],
            'capability': [['vision'], ['text'], ['code', 'math']],
            'updated': ['2 days ago', '1 week ago', '3 days ago'],
            'current_data': ['2024-01-15 10:30:00', '2024-01-15 10:30:00', '2024-01-15 10:30:00']
        }
        df = pd.DataFrame(wrong_type_data)
        
        # Should raise TypeError for wrong data type
        with pytest.raises(TypeError, match="Type de données incorrect pour la colonne 'name'"):
            check_data_quality(df)
    
    def test_check_data_quality_wrong_sizes_type(self):
        """Test check_data_quality detects wrong type for sizes column."""
        # Create a DataFrame with wrong type for sizes
        wrong_sizes_data = {
            'name': ['model1', 'model2', 'model3'],
            'pulls': ['1K', '2M', '500'],
            'sizes': [['2B', '4B'], 'not_a_list', ['13B', '30B']],  # 'not_a_list' is not a list
            'capability': [['vision'], ['text'], ['code', 'math']],
            'updated': ['2 days ago', '1 week ago', '3 days ago'],
            'current_data': ['2024-01-15 10:30:00', '2024-01-15 10:30:00', '2024-01-15 10:30:00']
        }
        df = pd.DataFrame(wrong_sizes_data)
        
        # Should raise TypeError for wrong data type
        with pytest.raises(TypeError, match="Type de données incorrect pour la colonne 'sizes'"):
            check_data_quality(df)
    
    def test_check_data_quality_empty_dataframe(self):
        """Test check_data_quality with empty DataFrame."""
        # Create an empty DataFrame with the correct columns
        empty_df = pd.DataFrame(columns=['name', 'pulls', 'sizes', 'capability', 'updated', 'current_data'])
        
        # This should not raise any exception (no duplicates in empty data)
        try:
            check_data_quality(empty_df)
        except Exception as e:
            pytest.fail(f"check_data_quality raised an unexpected exception with empty DataFrame: {e}")


class TestScrapOllamaModels:
    """Tests for the scrap_ollama_models function."""
    
    def test_scrap_ollama_models_success(self, requests_mock):
        """Test successful scraping of Ollama models."""
        # Mock HTML response that simulates Ollama website structure
        mock_html = '''
        <html>
            <body>
                <a class="group w-full">
                    <div title="llama2">llama2</div>
                    <span x-test-pull-count="true">1.2M</span>
                    <span x-test-size="true">7B</span>
                    <span x-test-size="true">13B</span>
                    <span x-test-capability="true">text</span>
                    <span x-test-updated="true">2 days ago</span>
                </a>
                <a class="group w-full">
                    <div title="codellama">codellama</div>
                    <span x-test-pull-count="true">800K</span>
                    <span x-test-size="true">7B</span>
                    <span x-test-capability="true">code</span>
                    <span x-test-updated="true">1 week ago</span>
                </a>
            </body>
        </html>
        '''
        
        # Mock the HTTP request
        requests_mock.get('https://ollama.com/search', text=mock_html)
        
        # Call the function
        result_df = scrap_ollama_models()
        
        # Verify the result
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 2
        assert 'name' in result_df.columns
        assert 'pulls' in result_df.columns
        assert 'sizes' in result_df.columns
        assert 'capability' in result_df.columns
        assert 'updated' in result_df.columns
        assert 'current_data' in result_df.columns
        
        # Check specific values
        assert result_df.iloc[0]['name'] == 'llama2'
        assert result_df.iloc[0]['pulls'] == '1.2M'
        assert result_df.iloc[0]['sizes'] == ['7B', '13B']
        assert result_df.iloc[0]['capability'] == ['text']
        assert result_df.iloc[0]['updated'] == '2 days ago'
        
        assert result_df.iloc[1]['name'] == 'codellama'
        assert result_df.iloc[1]['pulls'] == '800K'
        assert result_df.iloc[1]['sizes'] == ['7B']
        assert result_df.iloc[1]['capability'] == ['code']
        assert result_df.iloc[1]['updated'] == '1 week ago'
    
    def test_scrap_ollama_models_http_error(self, requests_mock):
        """Test handling of HTTP errors during scraping."""
        # Mock a 404 error
        requests_mock.get('https://ollama.com/search', status_code=404)
        
        # Should raise an exception for HTTP error
        with pytest.raises(Exception, match="Erreur de requête : 404"):
            scrap_ollama_models()
    
    def test_scrap_ollama_models_missing_elements(self, requests_mock):
        """Test scraping with missing HTML elements."""
        # Mock HTML with missing elements
        mock_html = '''
        <html>
            <body>
                <a class="group w-full">
                    <div title="testmodel">testmodel</div>
                    <!-- Missing pull count, sizes, etc. -->
                </a>
            </body>
        </html>
        '''
        
        requests_mock.get('https://ollama.com/search', text=mock_html)
        
        result_df = scrap_ollama_models()
        
        # Should still create a DataFrame with default values
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 1
        assert result_df.iloc[0]['name'] == 'testmodel'
        assert result_df.iloc[0]['pulls'] == 'N/A'
        assert result_df.iloc[0]['sizes'] == []
        assert result_df.iloc[0]['capability'] == ['N/A']
        assert result_df.iloc[0]['updated'] == 'N/A'


class TestRunScraping:
    """Tests for the run_scraping function."""
    
    @patch('ScrapFunction.scrap_ollama_models')
    @patch('ScrapFunction.check_data_quality')
    @patch('pandas.DataFrame.to_parquet')
    @patch('os.getenv')
    def test_run_scraping_success(self, mock_getenv, mock_to_parquet, mock_check_quality, mock_scrap):
        """Test successful execution of run_scraping."""
        # Setup mocks
        mock_df = pd.DataFrame({
            'name': ['test_model'],
            'pulls': ['1K'],
            'sizes': [['7B']],
            'capability': [['text']],
            'updated': ['1 day ago'],
            'current_data': ['2024-01-15 10:30:00']
        })
        mock_scrap.return_value = mock_df
        mock_getenv.side_effect = lambda key: {
            'AZURE_STORAGE_CONNECTION_STRING': 'test_connection_string',
            'AZURE_CONTAINER_NAME': 'test_container'
        }.get(key)
        
        # Call the function
        run_scraping()
        
        # Verify mocks were called
        mock_scrap.assert_called_once()
        mock_check_quality.assert_called_once_with(mock_df)
        mock_to_parquet.assert_called_once()
        
        # Check that to_parquet was called with correct parameters
        call_args = mock_to_parquet.call_args
        assert call_args[1]['engine'] == 'fastparquet'
        assert 'connection_string' in call_args[1]['storage_options']
        assert call_args[1]['storage_options']['connection_string'] == 'test_connection_string'
    
    @patch('ScrapFunction.scrap_ollama_models')
    @patch('ScrapFunction.check_data_quality')
    def test_run_scraping_data_quality_error(self, mock_check_quality, mock_scrap):
        """Test run_scraping when data quality check fails."""
        # Setup mocks
        mock_df = pd.DataFrame({'name': ['test']})
        mock_scrap.return_value = mock_df
        mock_check_quality.side_effect = ValueError("Data quality error")
        
        # Should re-raise the data quality error
        with pytest.raises(ValueError, match="Data quality error"):
            run_scraping()
        
        # Verify scraping was called but saving was not attempted
        mock_scrap.assert_called_once()
        mock_check_quality.assert_called_once_with(mock_df)


if __name__ == '__main__':
    pytest.main([__file__])