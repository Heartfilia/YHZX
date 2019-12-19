# from fake_useragent import UserAgent
#
# ua = UserAgent()
# print(ua.random)

from user_agent import generate_user_agent
for i in range(10):
    UserAgent = generate_user_agent(device_type="desktop")
    print(UserAgent)
    # break