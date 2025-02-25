from playwright.sync_api import sync_playwright
import time
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename="run.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

# 成功日志
yes_logger = logging.getLogger("yes_logger")
yes_handler = logging.FileHandler("yes.log")
yes_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
yes_logger.addHandler(yes_handler)
yes_logger.setLevel(logging.INFO)

# 失败日志
no_logger = logging.getLogger("no_logger")
no_handler = logging.FileHandler("no.log")
no_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
no_logger.addHandler(no_handler)
no_logger.setLevel(logging.INFO)

# 错误日志
error_logger = logging.getLogger("error_logger")
error_handler = logging.FileHandler("error.log")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
error_logger.addHandler(error_handler)

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"
TARGET_ICON_KEYWORD = "quest-target-kokinzoku.cb1e0015.png&w=3840&q=75"

def process_user(username, password):
    start_time = datetime.now()  # 开始计时
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # 登录流程
            page.goto(LOGIN_URL)
            logging.info("打开登录页面成功")
            time.sleep(10)  # 等待页面加载
            

            if page.is_visible("text=click here to login"):
                page.click("text=click here to login")
                logging.info("点击 'click here to login' 按钮")
                time.sleep(10)  # 等待页面加载
            
            page.fill("input[name='email']", username)
            page.fill("input[name='password']", password)
            logging.info("输入用户名和密码")
            page.click("button:has-text('login')")
            logging.info("点击登录按钮")

            time.sleep(10)  # 等待页面加载
            if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                page.click("img[src*='btn-close.d84df04b.png']")
                logging.info("关闭弹窗")

            # 点击第一个 'Next' 按钮
            if page.is_visible("button:has-text('Next')"):
                page.click("button:has-text('Next')")
                logging.info("点击第一个 'Next' 按钮")
                time.sleep(10)  # 等待页面更新

            # 滚动并点击第二个 'Next' 按钮
            next_buttons = page.locator("button:has-text('Next')")
            if next_buttons.count() > 1:
                second_next = next_buttons.nth(1)
                second_next.scroll_into_view_if_needed()
                second_next.click()
                logging.info("滚动并点击第二个 'Next' 按钮")
                time.sleep(10)  # 等待页面更新

            # 点击 QUEST 按钮
            if page.wait_for_selector("button:has-text('QUEST')", timeout=15000):
                page.click("button:has-text('QUEST')")
                logging.info("点击 QUEST 按钮")
                time.sleep(10)  # 等待动画完成
            else:
                logging.error(f"用户 {username} 登录后未找到 QUEST 按钮")
                return

            # 查找目标图标
            icons = page.locator("img").all()
            logging.info(f"找到的图标数量: {len(icons)}")

            target_icons = [
                icon for icon in icons
                if TARGET_ICON_KEYWORD in (icon.get_attribute("src") or "")
            ]
            logging.info(f"找到符合条件的图标数量: {len(target_icons)}")

            if not target_icons:
                no_logger.info(f"{username} 未找到符合条件的目标图标，耗时 0 秒")
                return

            # 遍历目标图标
            for index, target_icon in enumerate(target_icons):
                for attempt in range(3):  # 每个图标最多尝试点击 3 次
                    try:
                        logging.info(f"尝试点击第 {index + 1} 个目标图标 (第 {attempt + 1} 次尝试)")

                        # 检查图标是否可见
                        if not target_icon.is_visible():
                            logging.warning(f"第 {index + 1} 个目标图标不可见，跳过此图标")
                            break

                        # 获取边界框信息
                        bounding_box = target_icon.bounding_box()
                        if not bounding_box:
                            logging.warning(f"无法获取第 {index + 1} 个目标图标的边界框，跳过此图标")
                            break

                        # 调整点击位置为图标的中心点
                        x_center = bounding_box["x"] + bounding_box["width"] / 2
                        y_center = bounding_box["y"] + bounding_box["height"] / 2
                        logging.info(f"目标图标的中心坐标: x={x_center}, y={y_center}")

                        # 强制鼠标移动到中心点并点击
                        page.mouse.move(x_center, y_center)
                        time.sleep(0.2)  # 稳定鼠标位置
                        page.mouse.click(x_center, y_center)
                        logging.info(f"成功点击第 {index + 1} 个目标图标")

                        # 检查是否弹出 OK 按钮
                        if page.wait_for_selector("button:has-text('OK')", timeout=5000):
                            page.click("button:has-text('OK')")
                            logging.info("点击 OK 按钮成功")
                            end_time = datetime.now()
                            duration = (end_time - start_time).total_seconds()
                            yes_logger.info(f"{username} 点击任务图标成功，耗时 {duration:.2f} 秒")
                            return  # 成功后退出

                    except Exception as e:
                        logging.error(f"点击第 {index + 1} 个目标图标时发生错误: {e}")
                        if attempt == 2:  # 最后一次尝试失败后记录
                            no_logger.info(f"{username} 点击第 {index + 1} 个目标图标失败，耗时 0 秒")
                        time.sleep(1)  # 短暂等待后重试
                else:
                    logging.warning(f"第 {index + 1} 个图标重试 1 次后仍未成功，跳过此图标")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            no_logger.info(f"{username} 所有目标图标点击后均未触发窗口，耗时 {duration:.2f} 秒")
            logging.info("所有目标图标点击后均未触发窗口，退出当前用户操作")
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
            time.sleep(3)  # 每个用户之间的间隔时间
        else:
            error_logger.error(f"Invalid line format in user.txt: {line.strip()}")

if __name__ == "__main__":
    while True:
        try:
            logging.info(f"脚本运行开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            main()
            logging.info(f"脚本运行完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            logging.error(f"脚本运行过程中发生异常：{e}")
        finally:
            logging.info("等待 1 小时后再次运行...")
            time.sleep(3600)
