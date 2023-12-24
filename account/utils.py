from django.core.mail import send_mail
from django.conf import settings
import random


class SendCodeEmail:
    @staticmethod
    def send_email_code(code, to_email_address):
        try:
            success_sum = send_mail(
                subject='登录验证码',
                message=f'您的验证码是【{code}】。如非本人操作。请忽略',
                from_email=settings.EMAIL_FROM,
                recipient_list=[to_email_address],
                fail_silently=False
            )
            return success_sum
        except:
            return 0


def generate_code():
    """
    生成验证码
    :return:
    """
    seed = '0123456789'
    random_code = ''
    for i in range(6):
        random_code += random.choice(seed)
    return random_code