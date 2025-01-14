from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"

def process_user(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # 登录流程
            page.goto(LOGIN_URL)
            
            if page.is_visible("text=click here to login"):
                page.click("text=click here to login")
                print("打开登录页面")
            
            page.fill("input[name='email']", username)
            page.fill("input[name='password']", password)
            print("输入用户名和密码")
            page.click("button:has-text('login')")

            time.sleep(5)
            if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                page.click("img[src*='btn-close.d84df04b.png']")
                print("登录成功并关闭弹窗")
            
            # 点击第一个 'Next' 按钮
            if page.is_visible("button:has-text('Next')"):
                page.click("button:has-text('Next')")
                print("点击第一个 'Next'")
                time.sleep(2)  # 等待页面更新

            # 滚动并点击第二个 'Next' 按钮
            next_buttons = page.locator("button:has-text('Next')")
            if next_buttons.count() > 1:
                second_next = next_buttons.nth(1)
                second_next.scroll_into_view_if_needed()
                second_next.click()
                print("点击第二个 'Next'")
                time.sleep(2)  # 等待页面更新

            # 点击 DAILY BONUS 按钮
            daily_bonus_selector = "button:has-text('RAID REWARD')"
            if page.is_visible(daily_bonus_selector):
                page.click(daily_bonus_selector)
                print("点击 RAID REWARD")
                time.sleep(3)  # 等待弹出窗口加载完成
            else:
                print("未找到 RAID REWARD")
                return

            # 点击 CLAIM 按钮
            claim_button_selector = "button:has-text('CLAIM')"
            if page.is_visible(claim_button_selector):
                page.click(claim_button_selector)
                print("点击 CLAIM")
                time.sleep(5)  # 等待奖励窗口弹出
            else:
                print("未找到 CLAIM ")
                return

            # 点击奖励窗口中的 OK 按钮
            reward_ok_button_selector = "button:has-text('OK')"
            if page.is_visible(reward_ok_button_selector):
                page.click(reward_ok_button_selector)
                print("领取奖励")
                time.sleep(3)  # 等待奖励确认完成
            else:
                print("未找到奖励窗口的 OK 按钮")

        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            browser.close()
            print("浏览器已关闭")

def main():
    try:
        with open("user.txt", "r") as file:
            users = file.readlines()
    except FileNotFoundError:
        print("错误: 找不到 user.txt 文件")
        return

    for line in users:
        if "|" in line:
            username, password = line.strip().split("|", 1)
            print(f"正在处理用户 {username}")
            process_user(username, password)
            time.sleep(10)
        else:
            print(f"无效的行格式: {line.strip()}")

if __name__ == "__main__":
    main()
