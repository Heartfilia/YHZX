# 最大刷单量
max_task = 200
# 最大注册进程
max_register_process = 1
# 最大storm注册进程
max_storm_register_process = 5
# 最大rack注册进程
max_rack_register_process = 5
# 最大下单进程
max_place_order_process = 2
# 站点id
marketplace_id = 1
# 站点英文名字缩写
marketplace_name = 'us'
# 任务地址
# task_url = "https://www.suitshe.com/api/task2.php"
task_url = "http://third.gets.com/api/task.php?marketplace_id=%s&inner_debug=True" % marketplace_id

# 任务完成提交地址
# task_done_url = "http://testthird.gets.com:8383/api/task_done.php?sku=%s&name=%s&marketplace_id=%s&auto_status=%s&auto_error=%s"
task_done_url = "http://third.gets.com/api/task_done.php?sku=%s&name=%s&marketplace_id=%s&auto_status=%s&auto_error=%s&inventory_type=%s&had_send_email=%s&email_number=%s&inner_debug=True"

# 商家过滤列表,用于开发测试,生产环境保持 为空即可.
task_shop_name_filter = []

# 商品下架监控提交地址
# task_watch_url = "http://testthird.gets.com:8383/api/task_watch.php?sku=%s&name=%s&marketplace_id=%s&in_selling=%s"
task_watch_url = "http://third.gets.com/api/task_watch.php?sku=%s&name=%s&marketplace_id=%s&in_selling=%s&inner_debug=True"

# 商品下架监控明细提交地址
# task_watch_log_url = "http://testthird.gets.com:8383/api/task_watch_log.php?sku=%s&name=%s&marketplace_id=%s&in_selling=%s"
task_watch_log_url = "http://third.gets.com/api/task_watch_log.php?sku=%s&name=%s&marketplace_id=%s&in_selling=%s&inner_debug=True"

# 日志提交地址
# task_log_url = "http://testthird.gets.com:8383/api/task_operate_log.php?marketplace_id=%s&log_name=%s&sku=%s&name=%s&time=%s&log=%s"
task_log_url = "http://third.gets.com/api/task_operate_log.php?marketplace_id=%s&log_name=%s&sku=%s&name=%s&time=%s&log=%s&inner_debug=True"

# 核能量提交地址
# power_status_url = "http://testthird.gets.com:8383/api/task_power_status.php?power_status=%s"
power_status_url = "http://third.gets.com/api/task_power_status.php?power_status=%s&inner_debug=True"

# register_rtx_receivers = "陈镇泉;曾永伟;符琦梦;李汉培;"
register_rtx_receivers = "李汉培;"