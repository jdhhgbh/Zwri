import random
import string
import time
from playwright.sync_api import sync_playwright


def generate_random_string(length=5):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )


def run():
    # توليد البيانات الديناميكية
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
            )
        )
        page = context.new_page()

        # Step 1: الصفحة الرئيسية واختيار التجربة
        page.goto("https://stormiptv.co/tv/", wait_until="networkidle")
        page.click("text=Free Trial 24h")

        # Step 2: تحديد خيارات الإعدادات (Adult Channels & Account Type)
        page.wait_for_selector("select")
        selects = page.locator("select").all()
        if len(selects) >= 2:
            selects[0].select_option(label="No")
            selects[1].select_option(label="M3U & Xtream Code")

        page.click("button:has-text('Continue'), a:has-text('Continue')")

        # Step 3: صفحة السلة والدفع
        page.wait_for_selector(
            "button:has-text('Checkout'), a:has-text('Checkout')"
        )
        page.click("button:has-text('Checkout'), a:has-text('Checkout')")

        # Step 4: تعبئة نموذج البيانات Personal Information
        page.wait_for_selector("input[name='firstname'], #inputFirstName")

        # تعبئة الاسم والأيميل والجوال
        page.fill(
            "input[name='firstname'], #inputFirstName", first_name
        )
        page.fill("input[name='lastname'], #inputLastName", last_name)
        page.fill("input[name='email'], #inputEmail", email)
        page.fill("input[name='phonenumber'], #inputPhone", phone_number)

        # توليد كلمة السر عبر الزر
        generate_btn = page.locator(
            "button:has-text('Generate Password'),"
            " #generatePasswordButton, .generate-password"
        )
        if generate_btn.is_visible():
            generate_btn.click()
            time.sleep(1)
            # النقر على زر التأكيد المنسدل للكلمة إن وجد
            use_pw_btn = page.locator(
                "#btnGeneratePasswordInsert, button:has-text('Use')"
            )
            if use_pw_btn.is_visible():
                use_pw_btn.click()
        else:
            # كلمة سر عشوائية احتياطية في حال لم يستجب الزر
            fallback_password = generate_random_string(10) + "A1!"
            page.fill(
                "input[name='password'], #inputNewPassword1", fallback_password
            )
            page.fill(
                "input[name='password_confirm'], #inputNewPassword2",
                fallback_password,
            )

        # إتمام الطلب
        page.click(
            "button:has-text('Complete Order'), #btnCompleteOrder,"
            " input[value='Complete Order']"
        )
        page.wait_for_timeout(5000)

        print(f"تم إرسال الطلب بنجاح للإيميل: {email}")
        browser.close()


if __name__ == "__main__":
    run()
