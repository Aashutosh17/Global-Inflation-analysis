"""
Data Preprocessing Module for World Bank Inflation Data
Handles cleaning, merging, and preparing data for analysis
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


class InflationDataPreprocessor:
    """Class to handle preprocessing of inflation datasets"""
    
    def __init__(self, data_dir='data'):
        """Initialize preprocessor with data directory"""
        self.data_dir = Path(data_dir)
        self.df = None
        
    def load_data(self, filename='merged_inflation_data_20251118.csv'):
        """Load inflation data from CSV"""
        filepath = self.data_dir / filename
        print(f"Loading data from {filepath}...")
        self.df = pd.read_csv(filepath)
        print(f"Data shape: {self.df.shape}")
        print(f"\nColumns: {self.df.columns.tolist()}")
        return self.df
    
    def clean_data(self):
        """Perform data cleaning operations"""
        print("\n--- Data Cleaning ---")
        
        # Check for missing values
        print(f"\nMissing values:\n{self.df.isnull().sum()}")
        
        # Remove any completely null rows
        initial_rows = len(self.df)
        self.df = self.df.dropna(how='all')
        print(f"Removed {initial_rows - len(self.df)} completely null rows")

        required_columns = ['country', 'country_code', 'year', 'inflation_rate']
        before_required_filter = len(self.df)
        self.df = self.df.dropna(subset=required_columns)
        print(
            f"Removed {before_required_filter - len(self.df)} rows missing "
            f"required values: {', '.join(required_columns)}"
        )
        
        # Data type conversions
        self.df['year'] = self.df['year'].astype('int64')
        self.df['inflation_rate'] = self.df['inflation_rate'].astype('float64')
        
        # Remove duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            self.df = self.df.drop_duplicates()
            print(f"Removed {duplicates} duplicate rows")
        
        # Check for outliers in inflation_rate
        Q1 = self.df['inflation_rate'].quantile(0.25)
        Q3 = self.df['inflation_rate'].quantile(0.75)
        IQR = Q3 - Q1
        print("\nInflation Rate Statistics:")
        print(f"  Q1: {Q1:.2f}, Q3: {Q3:.2f}, IQR: {IQR:.2f}")
        print(f"  Min: {self.df['inflation_rate'].min():.2f}")
        print(f"  Max: {self.df['inflation_rate'].max():.2f}")
        print(f"  Mean: {self.df['inflation_rate'].mean():.2f}")
        print(f"  Median: {self.df['inflation_rate'].median():.2f}")
        
        return self.df
    
    def add_features(self):
        """Add derived features for analysis"""
        print("\n--- Feature Engineering ---")
        
        # Sort by country and year for time-series features
        self.df = self.df.sort_values(['country', 'year']).reset_index(drop=True)
        
        # Add inflation category
        def categorize_inflation(rate):
            if rate < 2:
                return 'Low'
            elif rate < 5:
                return 'Moderate'
            elif rate < 10:
                return 'High'
            else:
                return 'Very High'
        
        self.df['inflation_category'] = self.df['inflation_rate'].apply(categorize_inflation)
        
        # Add year decade
        self.df['decade'] = (self.df['year'] // 10) * 10
        
        # Add year period
        def assign_period(year):
            if year < 2010:
                return '2000s'
            elif year < 2015:
                return '2010-2014'
            elif year < 2020:
                return '2015-2019'
            else:
                return '2020s'
        
        self.df['period'] = self.df['year'].apply(assign_period)
        
        # Add moving averages and rolling statistics (by country)
        self.df['inflation_3yr_ma'] = self.df.groupby('country')['inflation_rate'].transform(
            lambda x: x.rolling(window=3, min_periods=1, center=False).mean()
        )
        
        self.df['inflation_5yr_ma'] = self.df.groupby('country')['inflation_rate'].transform(
            lambda x: x.rolling(window=5, min_periods=1, center=False).mean()
        )
        
        self.df['inflation_rolling_std'] = self.df.groupby('country')['inflation_rate'].transform(
            lambda x: x.rolling(window=3, min_periods=1, center=False).std()
        )
        
        # Add year-over-year change
        self.df['yoy_change'] = self.df.groupby('country')['inflation_rate'].transform(
            lambda x: x.diff()
        )
        
        # Add z-score for anomaly detection
        self.df['z_score'] = self.df.groupby('country')['inflation_rate'].transform(
            lambda x: np.abs((x - x.mean()) / (x.std() + 1e-8))
        )
        
        self.df['is_anomaly'] = self.df['z_score'] > 2.5
        
        print("Added features: inflation_category, decade, period")
        
        return self.df
    
    def get_summary_stats(self):
        """Generate summary statistics by country"""
        print("\n--- Summary Statistics ---")
        
        summary = self.df.groupby('country').agg({
            'inflation_rate': ['count', 'mean', 'min', 'max', 'std'],
            'year': ['min', 'max']
        }).round(2)
        
        return summary
    
    def save_processed_data(self, filename='processed_inflation_data.csv'):
        """Save processed data to CSV"""
        filepath = self.data_dir / filename
        self.df.to_csv(filepath, index=False)
        print(f"\nProcessed data saved to {filepath}")
        print(f"Final shape: {self.df.shape}")
        return filepath
    
    def get_data(self):
        """Return processed dataframe"""
        return self.df


def preprocess_pipeline():
    """Run complete preprocessing pipeline"""
    
    preprocessor = InflationDataPreprocessor()
    
    # Load data
    preprocessor.load_data()
    
    # Clean data
    preprocessor.clean_data()
    
    # Add features
    preprocessor.add_features()
    
    # Save processed data
    preprocessor.save_processed_data()
    
    # Display summary
    preprocessor.get_summary_stats()
    print("\n" + "="*60)
    print(f"Total countries: {preprocessor.df['country'].nunique()}")
    print(f"Year range: {preprocessor.df['year'].min()} - {preprocessor.df['year'].max()}")
    print(f"Total records: {len(preprocessor.df)}")
    print("="*60)
    
    return preprocessor.get_data()


if __name__ == "__main__":
    df = preprocess_pipeline()
    print("\n" + df.head(10).to_string())
