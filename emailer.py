import resend
import os
from datetime import datetime


def send(public_url: str, issue_number: int):
    resend.api_key = os.environ["RESEND_API_KEY"]
    date_str = datetime.now().strftime("%B %d, %Y")

    resend.Emails.send({
        "from": os.environ["SENDER_EMAIL"],
        "to": os.environ["RECIPIENT_EMAIL"],
        "subject": f"Signal — {date_str}",
        "html": f"""
        <div style="font-family: 'Helvetica Neue', sans-serif; max-width:480px; margin:40px auto; color:#111;">
          <p style="font-size:0.75rem; letter-spacing:0.15em; text-transform:uppercase; color:#999;">
            Issue #{issue_number} &middot; {date_str}
          </p>
          <h1 style="font-size:2rem; font-weight:700; margin:8px 0;">Signal</h1>
          <p style="color:#444; font-size:0.95rem; line-height:1.6;">
            Your weekly brief is ready. ~35 min read.
          </p>
          <a href="{public_url}" style="display:inline-block; margin-top:24px; padding:12px 28px;
             background:#0a0a0a; color:#c9a84c; text-decoration:none;
             font-size:0.85rem; letter-spacing:0.08em; text-transform:uppercase; border-radius:3px;">
            Read Signal &rarr;
          </a>
          <p style="margin-top:40px; font-size:0.8rem; color:#aaa;">
            Reply to this email with feedback. It shapes next week's brief.
          </p>
        </div>
        """,
    })
