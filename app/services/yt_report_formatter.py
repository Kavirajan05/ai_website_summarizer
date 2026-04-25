from datetime import datetime

def format_youtube_report(topic: str, ai_analysis: list) -> str:
    """
    Formats the AI-generated YouTube analysis into a readable report.
    """
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    formatted_ai_text = "\n\n".join([
        f"{item.get('rank')}. {item.get('title')} ({item.get('url')})\nExplanation: {item.get('explanation')}" 
        for item in ai_analysis
    ])
    
    report = f"""## AI YOUTUBE LEARNING REPORT

Topic: {topic}
Generated: {time_str}

{formatted_ai_text}
"""
    return report
