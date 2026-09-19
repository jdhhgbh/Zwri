import os
import random
import string
import time
import re
import imaplib
import email
from email.header import decode_header
from playwright.sync_api import sync_playwright

# توليد سلسلة عشوائية من حروف وأرقام
def generate_random_string(length=5):
    return "".join(
        random.choices(string.ascii_lowercase + string.digits, k=length)
    )

def fetch_m3u_link_from_email(target_email, max_retries=12, delay=10):
    """
    الاتصال بـ Outlook عبر IMAP وقراءة رابط M3U
    """
    outlook_user = os.getenv("OUTLOOK_USER")
    outlook_pass = os.getenv("OUTLOOK_PASS")

    if not outlook_user or not outlook_pass:
        print("⚠️ لم يتم ضبط OUTLOOK_USER أو OUTLOOK_PASS في Secrets.")
        return None

    print(f"📧 جاري الانتظار للتحقق من وصول الرسالة إلى {target_email}...")

    # الانتظار حتى تصل الرسالة (يحاول لمدة دقيقتين تقريباً)
    for i in range(max_retries):
        try:
            # الاتصال بـ Outlook IMAP
            mail = imaplib.IMAP4_SSL("outlook.office365.com")
            mail.login(outlook_user, outlook_pass)
            mail.select("inbox")

            # البحث عن جميع الرسائل
            status, messages = mail.search(None, "ALL")
            mail_ids = messages[0].split()

            # فحص الرسائل من الأحدث للأقدم
            for mail_id in reversed(mail_ids):
                status, data = mail.fetch(mail_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # استخراج نص الرسالة
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type in ["text/plain", "text/html"]:
                                    body += part.get_payload(decode=True).decode(errors="ignore")
                        else:
                            body = msg.get_payload(decode=True).decode(errors="ignore")

                        # التأكد من أن الرسالة موجهة لهذا الإيميل المخصص (zwri+xxx@outlook.sa)
                        if target_email.lower() in body.lower() or target_email.lower() in str(msg.get("To")).lower():
                            # البحث عن رابط M3U باستعمال Regex
                            m3u_match = re.search(r'https?://[^\s<>"]+?\.m3u8?', body) or re.search(r'https?://[^\s<>"]+type=m3u[^\s<>"]*', body)
                            if m3u_match:
                                m3u_url = m3u_match.group(0)
                                print(f"🎯 تم العثور على رابط M3U بنجاح: {m3u_url}")
                                mail.logout()
                                return m3u_url

            mail.logout()
        except Exception as e:
            print(f"حدث خطأ أثناء الاتصال بالبريد: {e}")

        print(f"محاولة ({i+1}/{max_retries}) - لم تصل الرسالة بعد، الانتظار {delay} ثوانٍ...")
        time.sleep(delay)

    print("❌ لم يتم العثور على رابط M3U في الوقت المحدد.")
    return None

def run():
    first_name = generate_random_string(6).capitalize()
    last_name = generate_random_string(6).capitalize()
    
    # الاعتماد على عنوان البريد أو الجزء الأساسي منه
    base_email = os.getenv("OUTLOOK_USER", "zwri@outlook.sa")
    email_prefix = base_email.split("@")[0]
    email_domain = base_email.split("@")[1] if "@" in base_email else "outlook.sa"
    
    email_tag = generate_random_string(6)
    email = f"{email_prefix}+{email_tag}@{email_domain}"
    
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

        print("1. جاري فتح الموقع...")
        page.goto("https://stormiptv.co/tv/", timeout=60000)
        page.wait_for_selector("text=Free Trial 24h", timeout=60000)
        page.click("text=Free Trial 24h")

        print("2. جاري اختيار None لإلغاء القنوات الإباحية نهائياً...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        product_selects = page.locator(
            "form select:not([onchange*='selectChangeNavigate'])"
        )

        if product_selects.count() >= 1:
            try:
                product_selects.nth(0).select_option(label="None", force=True)
            except Exception:
                try:
                    product_selects.nth(0).select_option(value="None", force=True)
                except Exception:
                    product_selects.nth(0).select_option(index=0, force=True)

        if product_selects.count() >= 2:
            try:
                product_selects.nth(1).select_option(
                    label="M3U & Xtream Code", force=True
                )
            except Exception:
                product_selects.nth(1).select_option(index=1, force=True)

        print("3. الضغط على Continue...")
        time.sleep(1)
        continue_btn = page.locator(
            "#btnCompleteProductConfig, button[type='submit']:has-text('Continue'),"
            " button:has-text('Continue')"
        ).first
        continue_btn.click(force=True)

        print("4. الانتقال لصفحة Checkout...")
        page.wait_for_selector(
            "a:has-text('Checkout'), button:has-text('Checkout'), #checkout",
            timeout=60000,
        )
        time.sleep(1)
        page.locator(
            "a:has-text('Checkout'), button:has-text('Checkout'), #checkout"
        ).first.click(force=True)

        print("5. تعبئة بيانات الحساب...")
        page.wait_for_selector(
            "input[name='firstname'], #inputFirstName", timeout=60000
        )

        page.fill("input[name='firstname'], #inputFirstName", first_name)
        page.fill("input[name='lastname'], #inputLastName", last_name)
        page.fill("input[name='email'], #inputEmail", email)
        page.fill("input[name='phonenumber'], #inputPhone", phone_number)

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

    # الخطوة 7: سحب رابط M3U من البريد
    m3u_link = fetch_m3u_link_from_email(email)
    
    if m3u_link:
        print(f"\n🚀 الرابط الذي تم جلبه جاهز للمرحلة القادمة:\n{m3u_link}\n")
        # هنا سيتم إضافة كود المرحلة القادمة (إضافة الرابط في موقع التلفزيون)
        return m3u_link
    else:
        print("⚠️ لم يتم العثور على الرابط.")
        return None

if __name__ == "__main__":
    run()
