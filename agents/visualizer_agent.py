import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict
import base64
from io import BytesIO

class VisualizerAgent:
    def __init__(self):
        sns.set_style("whitegrid")
        
    def generate_visualizations(self, data: List[Dict]) -> Dict[str, str]:
        """Generate multiple visualization types"""
        df = pd.DataFrame(data)
        
        # Convert date column to datetime if present
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return {
            "trend_plot": self._create_trend_plot(df),
            "distribution_plot": self._create_distribution_plot(df),
            "correlation_matrix": self._create_correlation_matrix(df)
        }
    
    def _create_trend_plot(self, df: pd.DataFrame) -> str:
        """Generate time series or trend visualization"""
        plt.figure(figsize=(10, 6))
        if 'date' in df.columns and 'value' in df.columns and not df[['date', 'value']].dropna().empty:
            df.sort_values('date', inplace=True)
            plt.plot(df['date'], df['value'], marker='o')
            plt.title("Trend Analysis")
            plt.xlabel("Date")
            plt.ylabel("Value")
        else:
            plt.text(0.5, 0.5, "Insufficient data for trend plot", ha='center', va='center')
        return self._plot_to_base64()
    
    def _create_distribution_plot(self, df: pd.DataFrame) -> str:
        """Generate distribution visualization"""
        plt.figure(figsize=(10, 6))
        if 'value' in df.columns and not df['value'].dropna().empty:
            sns.histplot(df['value'], kde=True)
            plt.title("Distribution Analysis")
        else:
            plt.text(0.5, 0.5, "No 'value' data for distribution plot", ha='center', va='center')
        return self._plot_to_base64()
    
    def _create_correlation_matrix(self, df: pd.DataFrame) -> str:
        """Generate correlation matrix"""
        plt.figure(figsize=(10, 6))
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
            plt.title("Correlation Matrix")
        else:
            plt.text(0.5, 0.5, "No numeric data for correlation matrix", ha='center', va='center')
        return self._plot_to_base64()
    
    def _plot_to_base64(self) -> str:
        """Convert matplotlib plot to base64 string"""
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    

# import base64

# if __name__ == "__main__":
#     agent = VisualizerAgent()
#     sample_data = [
#         {"date": "2025-01-01", "value": 10},
#         {"date": "2025-01-02", "value": 15},
#         {"date": "2025-01-03", "value": 7},
#         {"date": "2025-01-04", "value": 20},
#     ]
#     results = agent.generate_visualizations(sample_data)
    
#     for name, b64img in results.items():
#         filename = f"{name}.png"
#         with open(filename, "wb") as f:
#             f.write(base64.b64decode(b64img))
#         print(f"Saved {filename}")
