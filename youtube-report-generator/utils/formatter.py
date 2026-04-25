from datetime import datetime

def format_report(topic: str, ai_output: str) -> str:
    """
    Formats the AI-generated report into a readable string format.
    """
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""## YOUR YOUTUBE VIDEO REPORT

Topic: {topic}
Generated: {time_str}

{ai_output}
"""
    return report
