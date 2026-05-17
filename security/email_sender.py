import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPConfigError(Exception):
    pass


def get_smtp_config() -> dict:
    host = os.environ.get('SMTP_HOST', '').strip()
    user = os.environ.get('SMTP_USER', '').strip()
    password = os.environ.get('SMTP_PASS', '').strip()

    missing = [v for v, k in [('SMTP_HOST', host), ('SMTP_USER', user), ('SMTP_PASS', password)] if not k]
    if missing:
        raise SMTPConfigError(f"SMTP NOT CONFIGURED ({', '.join(missing)})")

    return {
        'host':      host,
        'port':      int(os.environ.get('SMTP_PORT', 587)),
        'user':      user,
        'password':  password,
        'from_addr': os.environ.get('SMTP_FROM', user).strip() or user,
    }


def send_magic_link(to_email: str, token: str, auth_port: int = 8765) -> None:
    cfg = get_smtp_config()
    link = f"http://localhost:{auth_port}/auth?token={token}"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your Snake Game sign-in link'
    msg['From']    = cfg['from_addr']
    msg['To']      = to_email

    plain = f"Click this link to sign in to Snake Game:\n\n{link}\n\nThis link expires in 15 minutes."
    html  = f"""<html><body>
<p>Click the link below to sign in to <strong>Snake - Retro Edition</strong>:</p>
<p><a href="{link}" style="font-size:18px">Sign in to Snake Game</a></p>
<p style="color:#888;font-size:12px">This link expires in 15 minutes. If you didn't request this, ignore this email.</p>
</body></html>"""

    msg.attach(MIMEText(plain, 'plain'))
    msg.attach(MIMEText(html,  'html'))

    port = cfg['port']
    if port == 465:
        with smtplib.SMTP_SSL(cfg['host'], port) as server:
            server.login(cfg['user'], cfg['password'])
            server.sendmail(cfg['from_addr'], to_email, msg.as_string())
    else:
        with smtplib.SMTP(cfg['host'], port) as server:
            if port == 587:
                server.starttls()
            server.login(cfg['user'], cfg['password'])
            server.sendmail(cfg['from_addr'], to_email, msg.as_string())
