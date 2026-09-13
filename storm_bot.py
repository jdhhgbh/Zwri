import random
import string
import time
from playwright.sync_api import sync_playwright


def generate_random_string(length=5):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )


def run():
    first_name = generate_random_string(6).capitalize()
    last_name = generate_random_string(6).capitalize()
    email_tag = generate_random_string(4)
    email = f"zwri+{email_tag}@outlook.sa"
    phone_suffix = "".join(random.choices(string.digits, k=4))
    phone_number = f"205255{phone_suffix}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # Step 1: الانتقال لصفحة تجربة الـ 24 ساعة
        page.goto("https://stormiptv.co/tv/", timeout=60000)
        page.click("text=Free Trial 24h")

        # Step 2: ضبط القوائم المنسدلة
        page.wait_for_selector("form", timeout=60000)
        time.sleep(2)

        # تحديد الخيارات في جميع القوائم المنسدلة الموجودة بالصفحة
        selects = page.locator("select").all()
        for sel in selects:
            try:
                options = sel.locator("option").all()
                if len(options) > 1:
                    val = options[1].get_attribute("value")
                    sel.select_option(value=val, force=True)
            except Exception:
                pass

        # إرسال نموذج إعدادات التجربة تلقائياً (تجاوز البحث عن الزر)
        page.evaluate(
            "document.querySelector('form').submit() ||"
            " document.forms[0].submit()"
        )

        # Step 3: الانتقال إلى صفحة الـ Checkout
        page.wait_for_timeout(3000)
        page.goto(
            "https://stormiptv.co/tv/cart.php?a=checkout",
            wait_until="networkidle",
            timeout=60000,
        )

        # Step 4: تعبئة البيانات الشخصية
        page.wait_for_selector(
            "input[name='firstname'], #inputFirstName", timeout=60000
        )

        page.fill("input[name='firstname'], #inputFirstName", first_name)
        page.fill("input[name='lastname'], #inputLastName", last_name)
        page.fill("input[name='email'], #inputEmail", email)
        page.fill("input[name='phonenumber'], #inputPhone", phone_number)

        # إنشاء وتعبئة كلمة المرور
        pwd = generate_random_string(10) + "A1!"
        pwd_inputs = page.locator(
            "input[type='password'], input[name='password'],"
            " #inputNewPassword1, #inputNewPassword2"
        ).all()
        for inp in pwd_inputs:
            try:
                inp.fill(pwd)
            except Exception:
                pass

        # إتمام الطلب من خلال إرسال نموذج الدفع النهائي
        time.sleep(1)
        checkout_form = page.locator(
            "form#frmCheckout, form[action*='checkout']"
        )
        if checkout_form.count() > 0:
            page.evaluate(
                "document.querySelector('form#frmCheckout').submit()"
            )
        else:
            page.locator(
                "#btnCompleteOrder, button:has-text('Complete Order'),"
                " input[value='Complete Order']"
            ).first.click(force=True)

        page.wait_for_timeout(5000)

        print(f"تم إرسال الطلب بنجاح للإيميل: {email}")
        browser.close()


if __name__ == "__main__":
    run()
