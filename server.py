import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

GMAIL_ADDRESS    = os.environ.get('GMAIL_ADDRESS')
GMAIL_PASSWORD   = os.environ.get('GMAIL_APP_PASSWORD')
NOTIFY_EMAIL     = os.environ.get('NOTIFY_EMAIL')


# ── Serve static files ───────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)


# ── Quote submission ─────────────────────────────────────────────────────────

@app.route('/submit-quote', methods=['POST'])
def submit_quote():
    data = request.get_json(force=True)

    first_name   = data.get('firstName', '').strip()
    last_name    = data.get('lastName', '').strip()
    email        = data.get('email', '').strip()
    phone        = data.get('phone', '').strip() or 'Not provided'
    biz_name     = data.get('bizName', '').strip() or 'Not provided'
    project_type = data.get('projectType', '').strip() or 'Not specified'
    features     = data.get('features', [])
    budget       = data.get('budget', '').strip() or 'Not specified'
    details      = data.get('details', '').strip() or 'Not provided'

    features_str = ', '.join(features) if features else 'None selected'
    subject      = f"New Quote Request — {first_name} {last_name}"

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f0f0;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:4px;overflow:hidden;max-width:600px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:#E8500A;padding:24px 32px;">
            <div style="font-size:20px;font-weight:700;color:#fff;letter-spacing:3px;text-transform:uppercase;">GR8 Web Design</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.8);margin-top:4px;letter-spacing:1px;">New Quote Request</div>
          </td>
        </tr>

        <!-- Client info -->
        <tr>
          <td style="padding:28px 32px 0;">
            <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Client</div>
            <div style="font-size:20px;font-weight:700;color:#fff;margin-bottom:4px;">{first_name} {last_name}</div>
            <div style="font-size:14px;color:#E8500A;margin-bottom:2px;">{email}</div>
            <div style="font-size:14px;color:#888;">{phone}</div>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:20px 32px 0;"><div style="height:1px;background:rgba(255,255,255,0.08);"></div></td></tr>

        <!-- Project details -->
        <tr>
          <td style="padding:24px 32px 0;">
            <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Project Details</div>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding-bottom:12px;width:40%;">
                  <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;">Business</div>
                  <div style="font-size:14px;color:#ccc;">{biz_name}</div>
                </td>
                <td style="padding-bottom:12px;">
                  <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;">Project Type</div>
                  <div style="font-size:14px;color:#fff;font-weight:600;">{project_type}</div>
                </td>
              </tr>
              <tr>
                <td style="padding-bottom:12px;">
                  <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;">Budget</div>
                  <div style="font-size:14px;color:#ccc;">{budget}</div>
                </td>
                <td style="padding-bottom:12px;">
                  <div style="font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px;">Features</div>
                  <div style="font-size:14px;color:#ccc;">{features_str}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- Divider -->
        <tr><td style="padding:4px 32px 0;"><div style="height:1px;background:rgba(255,255,255,0.08);"></div></td></tr>

        <!-- Project description -->
        <tr>
          <td style="padding:24px 32px;">
            <div style="font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Project Description</div>
            <div style="font-size:14px;color:#ccc;line-height:1.7;white-space:pre-wrap;">{details}</div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#111;padding:16px 32px;text-align:center;">
            <div style="font-size:11px;color:#555;letter-spacing:1px;">GR8 Web Design &middot; Northern Virginia &middot; gr8webdesign.com</div>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'GR8 Web Design <{GMAIL_ADDRESS}>'
    msg['To']      = NOTIFY_EMAIL
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, NOTIFY_EMAIL, msg.as_string())
        print(f'Email sent: {subject}')
        return jsonify({'success': True})
    except Exception as e:
        print(f'Email error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'GR8 Web Design server running at http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=False)
