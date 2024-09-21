# myapp/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.templatetags.static import static

@shared_task
def send_otp_email(otp, email):
    image_url = static('UserSide/img/mymail.jpeg')
    subject = 'Greetings from GlowGear'
    from_email = 'yadhupaikkattu3232@gmail.com'
    to_email = [email]
    text_content = f'Your Registration OTP Code is {otp}'
    html_content = f'''
        <html>
            <body>
                <h1>Welcome to GlowGear!</h1>
                <h5>The Right Time TO Purchase</h5>
                <h4>Your Registration OTP Code is: <strong>{otp}</strong></h4>
                <h4>Thank You For Choosing Us</h4>
                <img src="{image_url}" alt="Company Logo">
            </body>
        </html>
    '''      
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
