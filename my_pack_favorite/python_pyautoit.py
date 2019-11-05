# 第一步安装包： pip install PyAutoit
# 第二步安装软件： Autoit


# 打开第二步安装的软件: 拖动聚焦点到目标窗口完成定位

# 主要参数：
# Title : 参数里面第一项内容
# 第二项参数为属性值：具体需要到下面的Control里面去看
# 使用示例： 
import autoit

# 这里先打开一个本地窗口，不写了

# 聚焦到输入框
autoit.control_focus("打开", "[Class:Edit; instance:1]")  # (title, property)
# 输入内容
autoit.control_set_text("打开", "[Class:Edit; instance:1]", r"C:\Users\User\Desktop\images\FeedBack_3341.png")  # 发送路径
# 点击事件
autoit.control_click("打开", "[Class:Button; instance:1]")


# ### 更多操作慢慢拓展中，可以提前百度了解一下