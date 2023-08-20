from fastapi import APIRouter, HTTPException
import random
import smtplib
from email.mime.text import MIMEText

from .. import schemas

router = APIRouter(prefix='/otp')

# Endpoint to simulate sending OTP (for demonstration purposes)
@router.post("/send")
def send_otp(username: schemas.EmailData):
    # Generate a random OTP and store it in the "database"
    otp = ''.join(random.choices('0123456789', k=6))
    subject = "Your OTP"
    message = f"Your OTP is: {otp}"

    # Set up Gmail SMTP server and credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "ryy3490@gmail.com"
    smtp_password = "vfupfvfnrvkosnzv"
#     smtp_password = "Jahan@1024"

     # Create email message
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = "ryy3490@gmail.com"  # This should be your Gmail address
    msg["To"] = username.email

    # Connect to Gmail SMTP server and send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        
        return {"otp": otp}
    except Exception as e:
        return {"error": str(e)}
