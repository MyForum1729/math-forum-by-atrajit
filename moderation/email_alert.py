import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from string import Template

def send_email(user, content, link, flagged, type_name, type_icon):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    recipient = sender

    context = {
        "user": user,
        "comment": content,
        "link": link,
        "status": "Flagged" if flagged else "Safe",
        "status_icon": "❌" if flagged else "✅",
        "status_color": "#ff4d4d" if flagged else "#2ecc71",
        "type": type_name,
        "type_icon": type_icon,
    }

    with open("moderation/email_template.html", "r") as f:
        template = Template(f.read())
    html_content = template.safe_substitute(context)

    subject = f"[{'FLAGGED' if flagged else 'OK'}] New {type_name} by {user}"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())
