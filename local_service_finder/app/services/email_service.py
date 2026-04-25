import smtplib
from email.message import EmailMessage
from app.config.settings import settings

def send_results_email(user_email: str, ai_data: dict):
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("SMTP Credentials not configured. Skipping email delivery.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"Top {ai_data.get('service').capitalize()} Providers in {ai_data.get('city').capitalize()}"
    msg['From'] = settings.SMTP_USER
    msg['To'] = user_email
    
    # Helper to generate Google Maps link
    def get_maps_link(name, lat, lon):
        if not lat or not lon:
            # Fallback to search query if no lat/lon
            query_str = name.replace(" ", "+")
            return f"https://www.google.com/maps/search/?api=1&query={query_str}"
        query_str = f"{name}+{lat},{lon}".replace(" ", "+")
        return f"https://www.google.com/maps/search/?api=1&query={query_str}"

    best_choice = ai_data.get('best_choice', {})
    
    recs_list = ""
    for rec in ai_data.get('top_recommendations', []):
        maps_link = get_maps_link(rec.get('name'), rec.get('lat'), rec.get('lon'))
        rating = rec.get('rating', 'N/A')
        reviews = rec.get('reviews_count', 0)
        
        # Add stars display
        stars = "⭐" * int(float(rating)) if rating != 'N/A' and rating > 0 else ""
        
        recs_list += f"""
        <li style="margin-bottom: 15px; list-style-type: none; border-left: 4px solid #4a90e2; padding-left: 15px;">
            <strong style="font-size: 1.1em; color: #2c3e50;">{rec.get('name')}</strong><br>
            <span style="color: #f39c12;">{stars} {rating}</span> ({reviews} reviews)<br>
            <span style="color: #7f8c8d;">Phone: {rec.get('phone', 'N/A')}</span><br>
            <a href="{maps_link}" target="_blank" style="color: #3498db; text-decoration: none;">View on Google Maps</a> | 
            <a href="{rec.get('website', '#')}" target="_blank" style="color: #3498db; text-decoration: none;">Website</a><br>
            <em style="color: #34495e;">Why: {rec.get('reasoning', 'Highly ranked based on local feedback.')}</em>
        </li>
        """
        
    insights = ai_data.get('insights', [])
    insights_html = "<ul style='padding-left: 20px; color: #2c3e50;'>" + "".join([f"<li>{i}</li>" for i in insights]) + "</ul>" if insights else "No specific insights."

    best_choice_maps = get_maps_link(best_choice.get('name'), best_choice.get('lat'), best_choice.get('lon'))

    html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee;">
            <h1 style="color: #2c3e50; border-bottom: 2px solid #4a90e2; padding-bottom: 10px;">Local Service Recommendations</h1>
            <p>We found the best <strong>{ai_data.get('service')}</strong> options in <strong>{ai_data.get('city')}</strong> for you.</p>
            
            <div style="background-color: #ebf5fb; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid #3498db;">
                <h3 style="margin-top: 0; color: #2980b9;">🏆 Best Choice: {best_choice.get('name', 'N/A')}</h3>
                <p style="font-weight: bold; margin-bottom: 5px;">AI Trust Score: {best_choice.get('trust_score', 'N/A')}/100</p>
                <p style="margin-top: 0;">{best_choice.get('reasoning', 'N/A')}</p>
                <a href="{best_choice_maps}" target="_blank" style="display: inline-block; background-color: #3498db; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; margin-top: 5px;">View Location</a>
            </div>
            
            <h3 style="color: #2c3e50;">Top 5 Rated Providers</h3>
            <div style="padding-left: 0;">
                {recs_list}
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 25px;">
                <h3 style="margin-top: 0; color: #2c3e50;">AI Analysis Summary</h3>
                <p style="font-style: italic; color: #7f8c8d;">{ai_data.get('summary', '')}</p>
                <h4 style="margin-bottom: 5px; color: #2c3e50;">Key Market Insights:</h4>
                {insights_html}
            </div>
            
            <br>
            <p style="font-size: 0.8em; color: #bdc3c7; text-align: center; border-top: 1px solid #eee; padding-top: 15px;">
                Generated automatically by <strong>Local Service Finder AI Automation</strong>.
            </p>
        </body>
    </html>
    """
    
    msg.set_content("Please enable HTML to view this email properly.")
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
            print(f"Email successfully sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {e}")
