import random
import string
import time
import re
import requests
from playwright.sync_api import sync_playwright


# توليد اسم/معرف عشوائي للإيميل المؤقت
def generate_random_string(length=8):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )


# دالة لإنشاء بريد مؤقت وسحب الرسائل منه عبر 1secmail API
def get_temp_email():
    username = generate_random_string(10)
    domain = "1secmail.com"  # النطاقات المتاحة: 1secmail.com, 1secmail.org, 1secmail.net
    email = f"{username}@{domain}"
    return username, domain, email


def fetch_m3u_from_temp_email(username, domain, max_retries=15, delay=10):
    print(f"📧 جاري الانتظار وفحص صندوق الوارد للبريد: {username}@{domain}...")

    for i in range(max_retries):
        try:
            # استعلام الـ API لمعرفة الرسائل القادمة
            url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                messages = response.json()

                for msg in messages:
                    msg_id = msg.get("id")
                    # جلب تفاصيل الرسالة كاملة
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
                    msg_res = requests.get(msg_url, timeout=10)

                    if msg_res.status_code == 200:
                        msg_data = msg_res.json()
                        body = msg_data.get("body", "") + msg_data.get(
                            "textBody", ""
                        )

                        # البحث عن رابط M3U داخل محتوى الرسالة باستعمال Regex
                        m3u_match = re.search(
                            r'https?://[^\s<>"]+?\.m3u8?', body
                        ) or re.search(
                            r'https?://[^\s<>"]+type=m3u[^\s<>"]*', body
                        )

                        if m3u_match:
                            m3u_url = m3u_match.group(0)
                            print(
                                f"\n✨ ========================================"
                            )
                            print(f"🎯 تم العثور على رابط M3U بنجاح!")
                            print(f"🔗 الرابط: {m3u_url}")
                            print(
                                f"========================================\n"
                            )
                            return m3u_url
        except Exception as e:
            print(f"حدث خطأ أثناء فحص البريد: {e}")

        print(
            f"محاولة ({i+1}/{max_retries}) - لم تصل الرسالة بعد، الانتظار {delay} ثوانٍ..."
        )
        time.sleep(delay)

    print("❌ لم يتم العثور على رابط M3U في البريد المؤقت.")
    return None


def run():
    first_name = generate_random_string(6).capitalize()
    last_name = generate_random_string(6).capitalize()

    # إنشاء البريد المؤقت
    email_user, email_domain, email = get_temp_email()
    print(f"📧 البريد المؤقت المستخدم للطلب: {email}")

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

        # الخطوة 2: اختيار None لحذف باقة القنوات تماماً
        print("2. جاري اختيار None لإلغاء القنوات الإباحية نهائياً...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        product_selects = page.locator(
            "form select:not([onchange*='selectChangeNavigate'])"
        )

        # 1. اختيار None من قائمة Adult Channels
        if product_selects.count() >= 1:
            try:
                product_selects.nth(0).select_option(label="None", force=True)
            except Exception:
                try:
                    product_selects.nth(0).select_option(
                        value="None", force=True
                    )
                except Exception:
                    product_selects.nth(0).select_option(index=0, force=True)

        # 2. اختيار M3U & Xtream Code من القائمة الثانية
        if product_selects.count() >= 2:
            try:
                product_selects.nth(1).select_option(
                    label="M3U & Xtream Code", force=True
                )
            except Exception:
                product_selects.nth(1).select_option(index=1, force=True)

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

    # البحث عن الرابط في البريد المؤقت بعد الإرسال
    m3u_link = fetch_m3u_from_temp_email(email_user, email_domain)
    return m3u_link


if __name__ == "__main__":
    run()
