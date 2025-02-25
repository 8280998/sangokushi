from playwright.sync_api import sync_playwright
import time
from datetime import datetime

LOGIN_URL = "https://quest.kai-sangokushi-taisen.games/en/login"
TARGET_URL = "https://quest.kai-sangokushi-taisen.games/en/quest/"
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
            print("打开登录页面成功")
            time.sleep(10)  # 等待页面加载

            if page.is_visible("text=click here to login"):
                page.click("text=click here to login")
                print("点击 'click here to login' 按钮")
                time.sleep(10)  # 等待页面加载

            page.fill("input[name='email']", username)
            page.fill("input[name='password']", password)
            print("输入用户名和密码")
            page.click("button:has-text('login')")
            print("点击登录按钮")

            time.sleep(10)  # 等待页面加载
            if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                page.click("img[src*='btn-close.d84df04b.png']")
                print("关闭弹窗")

            # 登录成功后等待2秒
            time.sleep(2)

            # 重复操作4次
            for i in range(4):
                print(f"任务{i + 1}: 打开任务页面...")
                page.goto(TARGET_URL)
                time.sleep(2)  # 等待页面加载

                # 点击第一个 'Next' 按钮
                if page.is_visible("button:has-text('Next')"):
                    page.click("button:has-text('Next')")
                    print("点击第一个 'Next' 按钮")
                    time.sleep(2)  # 等待页面更新

                if page.is_visible("img[src*='btn-close.d84df04b.png']"):
                    page.click("img[src*='btn-close.d84df04b.png']")
                    print("关闭弹窗")
                    time.sleep(1)  # 等待页面更新
                    page.goto(TARGET_URL)
                    time.sleep(10)  # 等待页面加载
                # 查找目标图标
                icons = page.locator("img").all()
                print(f"找到的图标数量: {len(icons)}")
                target_icons = [
                    icon for icon in icons
                    if TARGET_ICON_KEYWORD in (icon.get_attribute("src") or "")
                ]
                print(f"找到符合条件的图标数量: {len(target_icons)}")

                if not target_icons:
                    print(f"{username} 未找到符合条件的目标图标，耗时 0 秒")
                    return

                # 遍历目标图标
                for index, target_icon in enumerate(target_icons):
                    for attempt in range(3):  # 每个图标最多尝试点击 3 次
                        try:
                            print(f"尝试点击第 {index + 1} 个目标图标 (第 {attempt + 1} 次尝试)")

                            # 检查图标是否可见
                            if not target_icon.is_visible():
                                print(f"第 {index + 1} 个目标图标不可见，跳过此图标")
                                break

                            # 获取边界框信息
                            bounding_box = target_icon.bounding_box()
                            if not bounding_box:
                                print(f"无法获取第 {index + 1} 个目标图标的边界框，跳过此图标")
                                break

                            # 调整点击位置为图标的中心点
                            x_center = bounding_box["x"] + bounding_box["width"] / 2
                            y_center = bounding_box["y"] + bounding_box["height"] / 2
                            print(f"目标图标的中心坐标: x={x_center}, y={y_center}")

                            # 强制鼠标移动到中心点并点击
                            page.mouse.move(x_center, y_center)
                            time.sleep(0.2)  # 稳定鼠标位置
                            page.mouse.click(x_center, y_center)
                            print(f"成功点击第 {index + 1} 个目标图标")


                        except Exception as e:
                            print(f"点击第 {index + 1} 个目标图标时发生错误: {e}")
                            if attempt == 2:  # 最后一次尝试失败后记录
                                print(f"{username} 点击第 {index + 1} 个目标图标失败，耗时 0 秒")
                            time.sleep(1)  # 短暂等待后重试
                    else:
                        print(f"第 {index + 1} 个图标重试 1 次后仍未成功，跳过此图标")

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                print(f"{username} 所有目标图标点击后均未触发窗口，耗时 {duration:.2f} 秒")
                print("所有目标图标点击后均未触发窗口，退出当前用户操作")
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
        print("user.txt file not found.")
        return

    for line in users:
        if "|" in line:
            username, password = line.strip().split("|", 1)
            print(f"Processing user {username}...")
            process_user(username, password)
            time.sleep(3)  # 每个用户之间的间隔时间
        else:
            print(f"Invalid line format in user.txt: {line.strip()}")

if __name__ == "__main__":
    while True:
        try:
            print(f"脚本运行开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            main()
            print(f"脚本运行完成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"脚本运行过程中发生异常：{e}")
        finally:
            print("等待 5小时后再次运行...")
            time.sleep(18000)
