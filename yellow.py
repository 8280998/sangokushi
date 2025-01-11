from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import logging
import random
import os
from datetime import datetime

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"
logging.basicConfig(level=logging.INFO)

def timestamp_str():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def take_screenshot(page, prefix="screenshot"):
    filename = f"{prefix}_{timestamp_str()}.png"
    page.screenshot(path=filename, full_page=True)
    logging.info(f"截图已保存: {filename}")

def handle_popup_ok(page):
    # 检查是否存在 "OK" 按钮
    ok_button = page.locator("button:has-text('OK')")
    if ok_button.is_visible():
        logging.info("检测到OK按钮，滚动到可视区域并点击关闭弹窗")
        # 滚动到按钮可视区域并点击
        ok_button.scroll_into_view_if_needed()
        time.sleep(3)  # 等待页面稳定
        ok_button.click(timeout=5000)  # 点击按钮

def handle_popup_okx(page):
    # 检查是否存在 "OK" 按钮
    ok_button = page.locator("button:has-text('OK')")
    if ok_button.is_visible():
        logging.info("检测到OK按钮，滚动到可视区域并点击关闭弹窗")
        # 滚动到按钮可视区域并点击
        ok_button.scroll_into_view_if_needed()
        time.sleep(3)  # 等待页面稳定
        page.click("img[src*='d84df04b.png']")

    # 检查是否存在 "NEXT" 按钮
    next_button = page.locator("button:has-text('Next')")
    if next_button.is_visible():
        logging.info("检测到NEXT按钮，滚动到可视区域并点击")
        next_button.scroll_into_view_if_needed()
        time.sleep(3)  # 等待页面稳定
        next_button.click(timeout=5000)  # 第一次点击
        time.sleep(2)  # 等待页面更新
        next_button.click(timeout=5000)  # 第二次点击
        logging.info("NEXT按钮点击成功")
        time.sleep(random.uniform(2, 4))  # 增加随机等待以模拟真实操作


def handle_confirm_warlord(page):
    if page.is_visible("p:has-text('OK')"):
        logging.info("检测到选择warlord确认弹窗OK按钮，点击关闭")
        time.sleep(3)
        page.click("p:has-text('OK')", timeout=5000)
        time.sleep(3)

def wait_and_click_next_if_visible(page):
    sleep_time = random.uniform(2,4)
    logging.info(f"等待 {sleep_time:.1f} 秒后检查NEXT按钮")
    time.sleep(sleep_time)
    if page.is_visible("p:has-text('Next')"):
        page.click("text=NEXT", timeout=5000)
        page.click("text=NEXT", timeout=5000)
        logging.info("检测到NEXT并点击成功")
        time.sleep(random.uniform(2,4))
        return True
    else:
        logging.info("未出现NEXT按钮")
        return False

def click_4th_55bbffa3_button(page, max_retries=8):
    """
    增强对第第4张牌按钮的点击逻辑：
    1. 等待按钮出现并可见。
    2. 如果有OK弹窗在前面，先点击OK关闭。
    3. 滚动到可视区域。
    4. 强制点击。
    """

    for attempt in range(1, max_retries+1):
        card_buttons = page.locator("img[src*='55bbffa3.png']")
        cb_count = card_buttons.count()
        logging.info(f"尝试点击第4张牌（第{attempt}次），找到 {cb_count} 个按钮")

        if cb_count > 3:
            fourth_button = card_buttons.nth(3)
            try:
                # 等待按钮可见
                fourth_button.wait_for(state="visible", timeout=10000)

                # 新增逻辑：如果有OK弹窗先关闭
                handle_popup_okx(page)
                handle_popup_ok(page)

                # 滚动到可视区域
                fourth_button.scroll_into_view_if_needed()

                # 尝试点击
                fourth_button.click(force=True, timeout=5000)
                logging.info("强制点击第4张牌")
                time.sleep(2)
                # 新增逻辑：点击弹出next
                wait_and_click_next_if_visible(page)
                
            except PlaywrightTimeoutError as te:
                logging.warning(f"等待或点击第4张牌超时（第{attempt}次尝试）: {te}")
                time.sleep(2)
            except Exception as e:
                logging.warning(f"点击第4张牌失败（第{attempt}次尝试）: {e}")
                time.sleep(2)
        else:
            logging.info("没有找到第4张牌，无法点击")
            break

            logging.info("多次尝试后仍无法点击第4张牌，尝试关闭NEXT弹窗后再试一次")
            handle_popup_ok(page)  # 先关闭可能存在的NEXT弹窗

# 再给一次尝试机会
            if click_4th_55bbffa3_button(page, max_retries=1):
                return True
            else:
                return False

def handle_55bbffa3_sequence(page):
    for attempt in range(1,6):
        logging.info(f"第{attempt}次尝试点击第4张牌")
        if not click_4th_55bbffa3_button(page):
            logging.info(f"第{attempt}次点击失败，提前结束")
            return False
        if wait_and_click_next_if_visible(page):
            logging.info(f"第{attempt}次NEXT已点击")
            if attempt == 3:
                logging.info("已完成三次点击及NEXT流程")
                return True
        else:
            logging.info(f"第{attempt}次点击后未出现NEXT，提前结束")
            return False
    return True

def handle_overlay(page):
    """检测并处理阻挡点击操作的覆盖层。"""
    overlay_selector = "div.fixed.z\\[100\\]"  
    if page.is_visible(overlay_selector):
        logging.info("检测到覆盖层，尝试等待覆盖层消失")
        try:
            page.wait_for_selector(overlay_selector, state="hidden", timeout=10000)
            logging.info("覆盖层已消失")
        except PlaywrightTimeoutError:
            logging.error("覆盖层未在指定时间内消失，尝试截图调试")
            take_screenshot(page, prefix="overlay_not_disappear")
    else:
        logging.info("未检测到覆盖层")

def click_with_retries(button, retries=3, delay=2):
    """尝试多次点击按钮，直到成功或达到最大重试次数。"""
    for attempt in range(1, retries + 1):
        try:
            button.click(timeout=5000)
            logging.info(f"点击按钮成功，尝试次数: {attempt}")
            return True
        except PlaywrightTimeoutError:
            logging.warning(f"点击按钮超时，尝试次数: {attempt}")
            time.sleep(delay)
    logging.error("多次尝试后仍无法点击按钮")
    return False

def login_to_account(page, username, password):
    page.goto(LOGIN_URL)
    page.wait_for_load_state('networkidle')
    logging.info("登录页面加载完成")

    if page.is_visible("text=click here to login"):
        page.click("text=click here to login")
        logging.info("点击 'click here to login' 按钮")

    page.fill('input[name="email"]', username)
    page.fill('input[name="password"]', password)
    logging.info(f"输入用户名和密码: {username}")

    page.click("button:has-text('login')")
    logging.info("点击登录按钮")
    time.sleep(5)

    if page.is_visible("img[src*='d84df04b.png']"):
        page.click("img[src*='d84df04b.png']")
        logging.info("关闭初始弹窗")
        time.sleep(2)

    if page.is_visible("button:has-text('Next')"):
        page.click("button:has-text('Next')")
        logging.info("点击第一个 'Next' 按钮")
        time.sleep(3)

    next_buttons = page.locator("button:has-text('Next')")
    count_nb = next_buttons.count()
    logging.info(f"找到 {count_nb} 个 'Next' 按钮")
    if count_nb > 1:
        next_buttons.nth(1).scroll_into_view_if_needed()
        next_buttons.nth(1).click()
        logging.info("点击第二个 'Next' 按钮")
        time.sleep(3)

def process_select_warlords(page):
    while True:
        warlords_buttons = page.locator("text='Select Warlords'")
        wb_count = warlords_buttons.count()
        logging.info(f"找到 {wb_count} 个 Select Warlords 按钮")

        if wb_count == 0:
            logging.info("没有找到 Select Warlords 按钮，进入GOOD模块")
            return

        clickable_found = False

        for button_index in range(wb_count):
            try:
                if button_index >= warlords_buttons.count():
                    logging.info(f"button_index {button_index} 超出范围，结束当前循环")
                    break

                button = warlords_buttons.nth(button_index)
                button.wait_for(state="visible", timeout=5000)

                if not button.is_enabled():
                    logging.info(f"第 {button_index + 1} 个 Warlords 按钮不可用，跳过")
                    continue

                # 在尝试点击之前先尝试关闭可能存在的NEXT弹窗
                handle_popup_ok(page)

                cursor = button.evaluate("el => window.getComputedStyle(el).cursor")
                logging.info(f"第 {button_index + 1} 个 Warlords 按钮光标样式: {cursor}")
                if cursor == 'pointer':
                    handle_overlay(page)

                    if button.is_visible() and button.is_enabled():
                        success = click_with_retries(button)
                        if success:
                            logging.info(f"点击第 {button_index + 1} 个 Select Warlords 按钮")
                            time.sleep(3)

                            # 点击Bonus Rate Table
                            bonus_rate_tables = page.locator("text=Bonus Rate Table")
                            brt_count = bonus_rate_tables.count()
                            logging.info(f"找到 {brt_count} 个 Bonus Rate Table 元素")

                            if brt_count == 0:
                                logging.info("没有 Bonus Rate Table，尝试关闭弹窗并直接进入GOOD模块")
                                if page.is_visible("img[src*='d84df04b.png']"):
                                    page.click("img[src*='d84df04b.png']")
                                    time.sleep(2)
                                return

                            rand_idx = random.randint(0, brt_count - 1)
                            chosen_element = bonus_rate_tables.nth(rand_idx)
                            chosen_element.wait_for(state="visible", timeout=10000)
                            chosen_element.scroll_into_view_if_needed()
                            chosen_element.click()
                            logging.info(f"点击随机的第 {rand_idx + 1} 个 Bonus Rate Table")
                            time.sleep(2)  # 等待 2 秒

                            # 点击完 Bonus Rate Table 后，再次查找并点击可以点击的 Select Warlords 按钮
                            logging.info("点击完 Bonus Rate Table后，继续查找 Select Warlords 按钮")
                            process_select_warlords(page)  # 递归调用

                            handle_confirm_warlord(page)

                            result = handle_55bbffa3_sequence(page)

                            if not result:
                                logging.info("翻牌序列提前结束，尝试继续下一个Warlords按钮")
                                time.sleep(3)
                                process_select_warlords(page)
                                break
                            else:
                                clickable_found = True
            except PlaywrightTimeoutError as e:
                logging.warning(f"等待或操作Warlords按钮时超时: {e}")
                continue
            except Exception as e:
                logging.warning(f"处理第 {button_index + 1} 个Warlords按钮时出错: {e}")
                continue

        if not clickable_found:
            logging.info("本轮没有找到可点击的Warlords，进入GOOD模块")
            return
def daily_bonus_task(page):
    logging.info("打开活动页面,更新到张角界面")
    page.goto("https://quest.kai-sangokushi-taisen.games/en/raid?id=7")
    time.sleep(5)
    handle_popup_ok(page)
    click_4th_55bbffa3_button(page, max_retries=8)

    if page.is_visible("img[src*='d84df04b.png']"):
        page.click("img[src*='d84df04b.png']")
        logging.info("关闭弹窗(d84df04b.png)")
        time.sleep(5)

    handle_overlay(page)
    process_select_warlords(page)

    good_button = page.locator("text='GOOD'")
    if good_button.is_visible() and good_button.is_enabled():
        good_button.scroll_into_view_if_needed()
        good_button.click()
        logging.info("点击 GOOD 按钮")
        time.sleep(random.uniform(1,5))

        attack_button = page.locator("p:has-text('Attack with this warlord')")
        if attack_button.is_visible():
            attack_button.click()
            logging.info("点击 Attack with this warlord 按钮")
            time.sleep(2)

def process_user(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            login_to_account(page, username, password)
            daily_bonus_task(page)
        except Exception as e:
            logging.error(f"处理用户 {username} 时发生错误: {e}")
            take_screenshot(page, f"screenshot_{username}_error")
        finally:
            browser.close()

def read_users_from_file(file_path):
    users = []
    with open(file_path, 'r') as f:
        for line in f:
            username, password = line.strip().split('|')
            users.append((username, password))
    return users

if __name__ == "__main__":
    users = read_users_from_file("user.txt")
    if not users:
        logging.error("没有找到有效的用户信息，脚本终止。")
    else:
        for username, password in users:
            logging.info(f"开始处理用户: {username}")
            try:
                process_user(username, password)
                logging.info(f"完成处理用户: {username}")
            except Exception as e:
                logging.error(f"处理用户 {username} 时发生未捕获的错误: {e}")
                # 如果需要，可以在这里添加截图或其他错误处理逻辑
                continue  # 跳过当前用户，继续下一个用户
            # 根据需要，添加等待时间以防止过于频繁的请求
            time.sleep(random.uniform(5, 10))
