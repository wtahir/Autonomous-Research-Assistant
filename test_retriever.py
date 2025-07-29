from rag.retriever import Retriever
from agents.analyst_agent import AnalystAgent

def main():
    retriever = Retriever()
    analyst = AnalystAgent()
    query = "Gaming industry trends 2025"
    
    # Simulated SearchAgent output from provided search results
    context = {
        "documents": [
            {
                "title": "7 Huge Gaming Industry Trends (2025 & 2026)",
                "url": "https://explodingtopics.com/blog/gaming-trends",
                "authors": ["Exploding Topics Team"],
                "content": "This is a list of the most important and impactful gaming trends right now. Many Triple AAA titles have fell far short of expectations in 2023, 2024, and so far in 2025. Baldur's Gate 3 was a mega-hit with a reported 10 million players. There are currently 1.86 billion PC gamers worldwide. According to a recent report, PS5s outsold Xbox Series X by a 5:1 margin in Q1 2024. Approximately 15% of all games offered on Steam are Early Access, set to grow significantly in 2025.",
                "published": "2025-07-02",
                "source": "explodingtopics.com"
            },
            {
                "title": "What’s possible for the gaming industry in the next dimension?",
                "url": "https://www.ey.com/en_us/tmt/gaming-entertainment",
                "authors": ["EY Team"],
                "content": "The video gaming industry has grown with stunning speed. By 2025, the gaming industry is expected to generate an estimated $211 billion in revenue, with mobile gaming contributing $116 billion. The emergence of the metaverse provides new possibilities for gameplay. 5G will allow consumers to use virtual reality (VR) and augmented reality (AR) gear on the go, providing a far richer mobile experience.",
                "published": "2025-05-28",
                "source": "ey.com"
            },
            {
                "title": "US Gaming Industry Trends Market Report 2025-2030",
                "url": "https://store.mintel.com/report/us-gaming-industry-trends-market-report",
                "authors": ["Mintel Team"],
                "content": "Mobile gaming continues to lead in revenue share, with a recorded 2.1% year-on-year growth. The US gaming industry is poised for a major surge in engagement by 2025, with 27% of gamers expressing plans to dedicate more time to gaming. Sports video games are an integral part, with 70% of gamers playing a sports game weekly.",
                "published": "2025-02-14",
                "source": "mintel.com"
            }
        ]
    }
    
    # Retrieve and analyze
    results = retriever.retrieve_relevant_info(query, context)
    print(f"Retrieved: {results}")
    analysis = analyst.analyze(results, query)
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    main()