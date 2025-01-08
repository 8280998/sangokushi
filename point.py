from playwright.sync_api import sync_playwright
import time
import csv
import os

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"
OUTPUT_CSV = "point.csv"
USER_FILE = "user.txt"

def process_user(username, password):
    with sync_playwright() as p:
        print(f"启动浏览器以处理用户: {username}")
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # 登录流程
            print("导航到登录页面...")
            page.goto(LOGIN_URL)
            time.sleep(10)  # 等待页面加载

            if page.is_visible("text=click here to login"):
                print("点击 'click here to login' 按钮")
                page.click("text=click here to login")
                time.sleep(5)  # 等待登录表单出现

            print("填写用户名和密码")
            page.fill("input[name='email']", username)
            page.fill("input[name='password']", password)
            print("点击登录按钮")
            page.click("button:has-text('login')")

            time.sleep(10)  # 等待登录过程完成

            if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                print("检测到弹窗，尝试关闭")
                page.click("img[src*='btn-close.d84df04b.png']")
                time.sleep(1)

            # 点击第一个 'Next' 按钮
            if page.is_visible("button:has-text('Next')"):
                print("点击第一个 'Next' 按钮")
                page.click("button:has-text('Next')")
                time.sleep(10)  # 等待页面更新

            # 滚动并点击第二个 'Next' 按钮
            next_buttons = page.locator("button:has-text('Next')")
            if next_buttons.count() > 1:
                second_next = next_buttons.nth(1)
                second_next.scroll_into_view_if_needed()
                print("滚动并点击第二个 'Next' 按钮")
                second_next.click()
                time.sleep(10)  # 等待页面更新

            # **已移除 DAILY BONUS 模块**

            # 提取指定 <p> 元素中的数字
            # 使用简化后的选择器
            selector = "p.font-bold.leading-none.whitespace-pre-wrap.break-words"
            print("尝试查找包含积分的元素...")
            if page.is_visible(selector):
                raw_text = page.text_content(selector)
                print(f"提取到的原始文本: {raw_text}")
                if raw_text:
                    number_str = raw_text.replace(",", "").strip()
                    if number_str.isdigit():
                        number = int(number_str)
                        print(f"成功提取数字: {number}")
                        return number
                    else:
                        print(f"提取的文本不是有效的数字: {raw_text}")
                        return None
                else:
                    print("指定元素中没有找到文本内容。")
                    return None
            else:
                print("未找到指定的积分元素。")
                return None

        except Exception as e:
            print(f"处理用户 {username} 时发生错误: {e}")
            return None
        finally:
            browser.close()
            print(f"已关闭浏览器，完成用户: {username}\n")

def main():
    users = []
    failed_users = []  # 用于记录处理失败的用户

    # 打印当前工作目录，确保CSV文件写入位置正确
    print(f"当前工作目录: {os.getcwd()}")

    # 读取 user.txt 文件中的用户信息
    print(f"尝试读取 '{USER_FILE}' 文件中的用户信息...")
    try:
        with open(USER_FILE, "r", encoding='utf-8') as file:
            for line in file:
                if "|" in line:
                    username, password = line.strip().split("|", 1)
                    users.append((username, password))
                else:
                    print(f"无效的行格式（缺少 '|')，跳过: {line.strip()}")
    except FileNotFoundError:
        print(f"错误: 找不到 '{USER_FILE}' 文件。请确保文件存在于脚本目录中。")
        return

    if not users:
        print("没有找到有效的用户信息，脚本终止。")
        return

    # 准备并写入 CSV 文件
    print(f"准备将结果写入 '{OUTPUT_CSV}' 文件...")
    try:
        with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["user", "points"])
            print("写入 CSV 文件头: user, points")

            # 逐个处理用户
            for username, password in users:
                print(f"正在处理用户: {username}...")
                points = process_user(username, password)
                print(f"接收到的积分: {points}")  # 调试输出
                if points is not None:
                    csv_writer.writerow([username, points])
                    print(f"用户: {username}, 积分: {points} 已写入 CSV 文件。")
                else:
                    print(f"用户: {username} 的积分提取失败。")
                    failed_users.append(username)  # 记录失败用户
                print("--------------------------------------------------")
                time.sleep(2)  # 用户之间的短暂暂停

        print(f"\n所有用户已处理完毕。结果已保存到 '{OUTPUT_CSV}' 文件中。")

        # 记录失败用户
        if failed_users:
            with open("failed_users.log", "w", encoding='utf-8') as f:
                for user in failed_users:
                    f.write(f"{user}\n")
            print(f"以下用户的积分提取失败，已记录到 'failed_users.log' 文件中。")

    except Exception as e:
        print(f"写入 '{OUTPUT_CSV}' 文件时发生错误: {e}")

if __name__ == "__main__":
    main()
