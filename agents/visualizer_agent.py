import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import pandas as pd
from typing import Dict, List

class VisualizerAgent:
    def __init__(self):
        # Updated style settings that work with modern Seaborn
        plt.style.use('seaborn-v0_8')  # Use compatible style name
        sns.set_theme(style="whitegrid", palette="husl")  # Modern theme setup

    def generate_visualizations(self, papers: List[Dict]) -> Dict[str, str]:
        """Generate visualizations from paper data"""
        viz_dict = {}
        
        try:
            # Create DataFrame with error handling
            plot_data = []
            for p in papers:
                if not isinstance(p, dict):
                    continue
                
                plot_data.append({
                    'title': (p.get('title', '')[:30] + '...') if len(p.get('title', '')) > 30 else p.get('title', ''),
                    'relevance': float(p.get('relevance_score', 0)),
                    'quality': float(p.get('quality_score', 0))
                })
            
            df = pd.DataFrame(plot_data)
            
            if len(df) > 1:  # Need at least 2 points for meaningful plots
                viz_dict['relevance_scores'] = self._create_barplot(
                    df, 
                    x='title', 
                    y='relevance', 
                    title="Paper Relevance Scores"
                )
                
                viz_dict['quality_vs_relevance'] = self._create_scatterplot(
                    df,
                    x='relevance',
                    y='quality',
                    title="Quality vs Relevance"
                )
            else:
                print("Insufficient data points for visualization")
                
        except Exception as e:
            print(f"Visualization error: {str(e)}")
        
        return viz_dict

    def _create_barplot(self, df, x: str, y: str, title: str) -> str:
        """Helper to create bar plot"""
        plt.figure(figsize=(10, 5))
        ax = sns.barplot(data=df, x=x, y=y)
        ax.set_title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return self._fig_to_base64()

    def _create_scatterplot(self, df, x: str, y: str, title: str) -> str:
        """Helper to create scatter plot"""
        plt.figure(figsize=(8, 6))
        ax = sns.scatterplot(
            data=df, 
            x=x, 
            y=y, 
            size=y, 
            hue=y, 
            sizes=(50, 200),
            legend=False
        )
        ax.set_title(title)
        plt.tight_layout()
        return self._fig_to_base64()

    def _fig_to_base64(self) -> str:
        """Convert matplotlib figure to base64"""
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')



# import matplotlib.pyplot as plt
# import seaborn as sns
# import base64
# from io import BytesIO
# import pandas as pd
# from typing import Dict, List

# class VisualizerAgent:
#     def __init__(self):
#         plt.style.use('seaborn')
#         sns.set_palette("husl")

#     def generate_visualizations(self, papers: List[Dict]) -> Dict[str, str]:
#         """Generate visualizations from paper data"""
#         viz_dict = {}
        
#         # Create DataFrame from paper data
#         df = pd.DataFrame([{
#             'title': p['title'][:30] + '...' if len(p['title']) > 30 else p['title'],
#             'relevance': p['relevance_score'],
#             'quality': p['quality_score']
#         } for p in papers if 'relevance_score' in p])
        
#         if len(df) > 0:
#             # Bar plot of relevance scores
#             viz_dict['relevance_scores'] = self._create_barplot(
#                 df, 
#                 x='title', 
#                 y='relevance', 
#                 title="Paper Relevance Scores"
#             )
            
#             # Quality vs Relevance scatter
#             viz_dict['quality_vs_relevance'] = self._create_scatterplot(
#                 df,
#                 x='relevance',
#                 y='quality',
#                 title="Quality vs Relevance"
#             )
        
#         return viz_dict

#     def _create_barplot(self, df, x: str, y: str, title: str) -> str:
#         """Helper to create bar plot"""
#         plt.figure(figsize=(10, 5))
#         sns.barplot(data=df, x=x, y=y)
#         plt.title(title)
#         plt.xticks(rotation=45, ha='right')
#         plt.tight_layout()
#         return self._fig_to_base64()

#     def _create_scatterplot(self, df, x: str, y: str, title: str) -> str:
#         """Helper to create scatter plot"""
#         plt.figure(figsize=(8, 6))
#         sns.scatterplot(data=df, x=x, y=y, size=y, hue=y, sizes=(50, 200))
#         plt.title(title)
#         plt.tight_layout()
#         return self._fig_to_base64()

#     def _fig_to_base64(self) -> str:
#         """Convert matplotlib figure to base64"""
#         buf = BytesIO()
#         plt.savefig(buf, format='png', bbox_inches='tight')
#         plt.close()
#         return base64.b64encode(buf.getvalue()).decode('utf-8')