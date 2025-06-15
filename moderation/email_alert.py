import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from string import Template

def send_email(user, comment, link, flagged):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    recipient = os.environ["EMAIL_RECIPIENTS"]

    # Context for the template
    context = {
        "user": user,
        "comment": comment,
        "link": link,
        "status": "Flagged" if flagged else "Safe",
        "status_icon": "❌" if flagged else "✅",
        "status_color": "#ff4d4d" if flagged else "#2ecc71",
    }

    # Load and substitute the template
    with open("moderation/email_template.html", "r") as f:
        template = Template(f.read())
    html_content = template.safe_substitute(context)

    subject = f"[{'FLAGGED' if flagged else 'OK'}] New GitHub Comment by {user}"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())
