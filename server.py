from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        user_email = data.get('email')
        user_message = data.get('message')

        if not user_email or not user_message:
            return jsonify({"success": False, "message": "Email and message are required"}), 400

        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            return jsonify({"success": False, "message": "Email server not configured"}), 500

        recipient_emails = [
            "onlinecourse0402@gmail.com",
            "sandhiyakavin18@gmail.com",
            "varshinis270@gmail.com",
            "akashcanand71100@gmail.com"
        ]

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_emails)
        msg['Subject'] = "Helpdesk Request from Course System 🆘💬"

        body = f"""
New helpdesk message received:

From: {user_email}
Message:
{user_message}

Sent from Course Database System
"""
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return jsonify({"success": True, "message": "Email sent successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
