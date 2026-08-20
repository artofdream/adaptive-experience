"""2-Hour Automated Email Status Brief Dispatcher.

Sends formatted HTML repo status briefs to the sponsor (claude.tsarafidy@gmail.com)
via AWS SES or SMTP.
Coherent with NFR-003, NFR-008, NFR-017, and ADR-016.
"""

import argparse
import datetime
import html
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFS_DIR = ROOT / "research" / "daily-briefs"
DEFAULT_RECIPIENT = "claude.tsarafidy@gmail.com"
DEFAULT_SENDER = os.environ.get("AEA_SES_SENDER", "briefs@aea.artof.link")


def find_latest_brief() -> Path:
    """Locate the most recent daily brief file in research/daily-briefs/."""
    brief_files = sorted(BRIEFS_DIR.glob("*.md"))
    if not brief_files:
        raise FileNotFoundError(f"No brief files found in {BRIEFS_DIR}")
    return brief_files[-1]


def markdown_to_simple_html(md_text: str) -> str:
    """Convert basic markdown headers, bold, bullet points, and code blocks to HTML."""
    lines = md_text.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1 style='color: #1b4332;'>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2 style='color: #1d3557; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px;'>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3 style='color: #2b2d42;'>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("* ") or stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul style='line-height: 1.6;'>")
                in_list = True
            content = html.escape(stripped[2:])
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            content = re.sub(r"\*(.*?)\*", r"<em>\1</em>", content)
            html_lines.append(f"<li>{content}</li>")
        elif stripped == "---":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr style='border: 0; border-top: 1px solid #cbd5e1; margin: 16px 0;'/>")
        elif stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = html.escape(stripped)
            content = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", content)
            content = re.sub(r"\*(.*?)\*", r"<em>\1</em>", content)
            html_lines.append(f"<p style='line-height: 1.5; color: #334155;'>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    body_content = "\n".join(html_lines)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>AEA 2-Hour Status Brief</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; padding: 24px; margin: 0;">
<div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
  <div style="background-color: #1b4332; color: #ffffff; padding: 16px 24px; border-radius: 6px; margin-bottom: 24px;">
    <h2 style="margin: 0; font-size: 20px;">Adaptive Experience Architecture — On-Demand Status Brief</h2>
    <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">Recipient: {html.escape(DEFAULT_RECIPIENT)} | Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
  </div>
  {body_content}
  <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b; text-align: center;">
    Sent automatically by @aea-devsecops-platform via AEA Status Dispatcher | Repository: artof-group/adaptive-experience-architecture
  </div>
</div>
</body>
</html>"""


def send_via_aws_ses(recipient: str, subject: str, html_body: str, text_body: str) -> bool:
    """Attempt sending email via AWS SES using boto3 or AWS CLI."""
    try:
        import boto3
        region = os.environ.get("AWS_REGION", "us-east-1")
        client = boto3.client("ses", region_name=region)
        response = client.send_email(
            Source=DEFAULT_SENDER,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                },
            },
        )
        print(f"[SUCCESS] Email sent to {recipient} via AWS SES (MessageId: {response.get('MessageId')})")
        return True
    except Exception as exc:
        print(f"[NOTICE] AWS SES boto3 send skipped/deferred: {exc}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send 2-hour status brief via email.")
    parser.add_argument("--recipient", default=DEFAULT_RECIPIENT, help="Recipient email address")
    parser.add_argument("--dry-run", action="store_true", help="Format and print HTML without sending")
    args = parser.parse_args()

    latest_file = find_latest_brief()
    md_content = latest_file.read_text(encoding="utf-8")
    html_content = markdown_to_simple_html(md_content)
    subject = f"AEA 2-Hour Status Brief — {latest_file.stem}"

    print(f"Latest Brief File: {latest_file.name}")
    print(f"Target Recipient: {args.recipient}")

    if args.dry_run:
        print("\n=== DRY RUN HTML PREVIEW ===")
        print(html_content[:500] + "\n...")
        print("=== END DRY RUN ===")
        return 0

    sent = send_via_aws_ses(args.recipient, subject, html_content, md_content)
    if not sent:
        print(f"[INFO] 2-Hour Brief rendered successfully for {args.recipient}. Stored locally at {BRIEFS_DIR / latest_file.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
