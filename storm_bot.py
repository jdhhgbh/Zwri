import random
import string
import time
from playwright.sync_api import sync_playwright


# توليد سلسلة عشوائية تتكون من حروف صغيرة وأرقام
def generate_random_string(length=5):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )


def run():
    first_name = generate_random_string(6).capitalize()
    last_name = generate_random_string(6).capitalize()
    # 6 خانات عشوائية (حروف وأرقام) بعد الزائد
    email_tag = generate_random_string(6)
    email = f"zwri+{email_tag}@outlook.sa"
    phone_suffix = "".join(random.choices(string.digits, k=4))
    phone_number = f"205255{phone_suffix}"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # الخطوة 1: الدخول وضغط Free Trial 24h
        print("1. جاري فتح الموقع...")
        page.goto("https://stormiptv.co/tv/", timeout=60000)
        page.wait_for_selector("text=Free Trial 24h", timeout=60000)
        page.click("text=Free Trial 24h")

        # الخطوة 2: اختيار القوائم المنسدلة بناءً على الواجهة المحددة
        print("2. جاري اختيار No للقنوات الإباحية و ضبط Account Type...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        product_selects = page.locator(
            "form select:not([onchange*='selectChangeNavigate'])"
        )

        # القائمة الأولى: Adult Channels -> اختيار الخيار الثاني (No)
        if product_selects.count() >= 1:
            try:
                product_selects.nth(0).select_option(label="No", force=True)
            except Exception:
                product_selects.nth(0).select_option(index=1, force=True)

        # القائمة الثانية: Account Type -> اختيار M3U & Xtream Code
        if product_selects.count() >= 2:
            try:
                product_selects.nth(1).select_option(
                    label="M3U & Xtream Code", force=True
                )
            except Exception:
                # إذا كانت القائمة تحتوي على خيار آخر بالمنتصف
                options = product_selects.nth(1).locator("option").all()
                if len(options) > 1:
                    product_selects.nth(1).select_option(
                        index=len(options) - 1, force=True
                    )

        # الضغط على Continue
        print("3. الضغط على Continue...")
        time.sleep(1)
        continue_btn = page.locator(
            "#btnCompleteProductConfig, button[type='submit']:has-text('Continue'),"
            " button:has-text('Continue')"
        ).first
        continue_btn.click(force=True)

        # الخطوة 3: صفحة Checkout
        print("4. الانتقال لصفحة Checkout...")
        page.wait_for_selector(
            "a:has-text('Checkout'), button:has-text('Checkout'), #checkout",
            timeout=60000,
        )
        time.sleep(1)
        page.locator(
            "a:has-text('Checkout'), button:has-text('Checkout'), #checkout"
        ).first.click(force=True)

        # الخطوة 4: تعبئة البيانات Personal Information
        print("5. تعبئة بيانات الحساب...")
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
        if gen_btn.count() > 0 and gen_btn.first.is_visible():
            gen_btn.first.click(force=True)
            time.sleep(1)
            use_btn = page.locator(
                "#btnGeneratePasswordInsert, button:has-text('Use')"
            )
            if use_btn.count() > 0 and use_btn.first.is_visible():
                use_btn.first.click(force=True)
        else:
            pwd = generate_random_string(10) + "A1!"
            page.fill("input[name='password'], #inputNewPassword1", pwd)
            page.fill(
                "input[name='password_confirm'], #inputNewPassword2", pwd
            )

        # إتمام الطلب
        print("6. إتمام الطلب...")
        time.sleep(2)
        complete_btn = page.locator(
            "#btnCompleteOrder, button:has-text('Complete Order'),"
            " input[value='Complete Order']"
        ).first
        complete_btn.click(force=True)

        page.wait_for_timeout(5000)
        print(f"✅ تم إرسال الطلب بنجاح للإيميل: {email}")
        browser.close()


if __name__ == "__main__":
    run()
