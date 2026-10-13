import pickle
import os


with open(os.path.join('model', 'user_mapping.pkl'), 'rb') as f:
    user_to_index = pickle.load(f)

real_users = list(user_to_index.keys())[:10]
print("可以用来测试的真实玩家名字：")
for user in real_users:
    print(user)