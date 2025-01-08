from playwright.sync_api import sync_playwright
import time
import logging

# 配置日志
logging.basicConfig(
    filename="bonus.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

error_logger = logging.getLogger("error_logger")
error_handler = logging.FileHandler("error.log")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
error_logger.addHandler(error_handler)

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"

def process_user(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # 登录流程
            page.goto(LOGIN_URL)
            logging.info("打开登录页面成功")
            time.sleep(10)  # 等待页面更新
            
            if page.is_visible("text=click here to login"):
                page.click("text=click here to login")
                logging.info("点击 'click here to login' ")
                time.sleep(5)  # 等待页面更新

            page.fill("input[name='email']", username)
            page.fill("input[name='password']", password)
            logging.info("输入用户名和密码")
            page.click("button:has-text('login')")
            logging.info("点击登录")

            time.sleep(10)
            if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                page.click("img[src*='btn-close.d84df04b.png']")
                logging.info("关闭弹窗")
            # 点击第一个 'Next' 按钮
            if page.is_visible("button:has-text('Next')"):
                page.click("button:has-text('Next')")
                logging.info("点击第一个 'Next'")
                time.sleep(10)  # 等待页面更新

            # 滚动并点击第二个 'Next' 按钮
            next_buttons = page.locator("button:has-text('Next')")
            if next_buttons.count() > 1:
                second_next = next_buttons.nth(1)
                second_next.scroll_into_view_if_needed()
                second_next.click()
                logging.info("滚动并点击第二个 'Next'")
                time.sleep(10)  # 等待页面更新

            # 点击 DAILY BONUS 按钮
            daily_bonus_selector = "button:has-text('DAILY BONUS')"
            if page.is_visible(daily_bonus_selector):
                page.click(daily_bonus_selector)
                logging.info("点击 DAILY BONUS")
                time.sleep(3)  # 等待弹出窗口加载完成
            else:
                logging.warning("未找到 DAILY BONUS")
                return

            # 点击 CLAIM 按钮
            claim_button_selector = "button:has-text('CLAIM')"
            if page.is_visible(claim_button_selector):
                page.click(claim_button_selector)
                logging.info("点击 CLAIM")
                time.sleep(5)  # 等待奖励窗口弹出
            else:
                logging.warning("未找到 CLAIM 按钮")
                return

            # 点击奖励窗口中的 OK 按钮
            reward_ok_button_selector = "button:has-text('OK')"
            if page.is_visible(reward_ok_button_selector):
                page.click(reward_ok_button_selector)
                logging.info("点击奖励按钮")
                time.sleep(3)  # 等待奖励确认完成
            else:
                logging.warning("未找到奖励窗口的 OK 按钮")

        except Exception as e:
            logging.error(f"发生错误: {e}")
        finally:
            browser.close()
            logging.info("浏览器已关闭")

def main():
    try:
        with open("user.txt", "r") as file:
            users = file.readlines()
    except FileNotFoundError:
        error_logger.error("user.txt file not found.")
        return

    for line in users:
        if "|" in line:
            username, password = line.strip().split("|", 1)
            logging.info(f"Processing user {username}...")
            process_user(username, password)
            time.sleep(10)
        else:
            error_logger.error(f"Invalid line format in user.txt: {line.strip()}")

if __name__ == "__main__":
    main()