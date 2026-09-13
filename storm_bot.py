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

        # Step 1: الانتقال ورابط التجربة
        page.goto("https://stormiptv.co/tv/", timeout=60000)
        page.click("text=Free Trial 24h")

        # Step 2: التعامل مع القوائم المنسدلة مع الانتظار الصريح
        page.wait_for_selector(
            "select", state="attached", timeout=60000
        )  # زيادة المهلة لـ 60 ثانية
        time.sleep(3)  # انتظار إضافي لضمان اكتمال تحميل عناصر DOM

        # اختيار خيار القنوات الإباحية وتحديد M3U
        selects = page.locator("select")
        count = selects.count()

        if count >= 2:
            # استخدام الاختيار بالـ value أو Index لضمان عدم التعليق
            selects.nth(0).select_option(index=1)
            selects.nth(1).select_option(index=1)

        # الضغط على زر Continue
        continue_btn = page.locator(
            "#btnCompleteProductConfig, button:has-text('Continue'),"
            " a:has-text('Continue')"
        )
        continue_btn.first.click()

        # Step 3: صفحة Checkout
        page.wait_for_selector(
            "button:has-text('Checkout'), a:has-text('Checkout')", timeout=60000
        )
        page.locator(
            "button:has-text('Checkout'), a:has-text('Checkout')"
        ).first.click()

        # Step 4: تعبئة البيانات
        page.wait_for_selector(
            "input[name='firstname'], #inputFirstName", timeout=60000
        )

        page.fill("input[name='firstname'], #inputFirstName", first_name)
        page.fill("input[name='lastname'], #inputLastName", last_name)
        page.fill("input[name='email'], #inputEmail", email)
        page.fill("input[name='phonenumber'], #inputPhone", phone_number)

        # توليد كلمة السر
        gen_btn = page.locator(
            "#generatePasswordButton, .generate-password,"
            " button:has-text('Generate Password')"
        )
        if gen_btn.is_visible():
            gen_btn.first.click()
            time.sleep(1)
            use_btn = page.locator(
                "#btnGeneratePasswordInsert, button:has-text('Use')"
            )
            if use_btn.is_visible():
                use_btn.first.click()
        else:
            pwd = generate_random_string(10) + "A1!"
            page.fill("input[name='password'], #inputNewPassword1", pwd)
            page.fill(
                "input[name='password_confirm'], #inputNewPassword2", pwd
            )

        # إتمام الطلب
        complete_btn = page.locator(
            "#btnCompleteOrder, button:has-text('Complete Order'),"
            " input[value='Complete Order']"
        )
        complete_btn.first.click()
        page.wait_for_timeout(5000)

        print(f"تم تنفيذ الطلب بنجاح للإيميل: {email}")
        browser.close()


if __name__ == "__main__":
    run()
