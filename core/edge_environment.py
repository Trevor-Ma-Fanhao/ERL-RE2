import numpy as np
import edge_server_model

class EdgeServerEnv:
    def __init__(self, num_servers, time_steps, csv_file):
        self.num_servers = num_servers  # 边缘服务器的数量
        self.time_steps = time_steps      # 未来时间步数
        self.current_step = 0             # 当前时间步
        self.egde_servers = []  # 初始化服务器列表
        for i in range(num_servers):
            server = edge_server_model.EdgeServer(csv_file, i)
            self.egde_servers.append(server)  # 将每个服务器添加到列表中

    def reset(self):
        # 重置环境到初始状态
        self.current_step = 0
        return self.egde_servers[0].get_future_resource_capacity()[self.current_step]

    def step(self, action):
        # 执行动作并返回下一个状态、奖励和是否结束
        if self.current_step >= self.time_steps - 1:
            done = True
            next_state = None
            reward = 0  # 结束时的奖励可以根据需求定义
        else:
            done = False
            self.current_step += 1
            next_state = self.egde_servers[0].get_future_resource_capacity()[self.current_step]
            reward = self.calculate_reward(action, next_state)  # 根据动作和下一个状态计算奖励

        return next_state, reward, done, {}

    def calculate_reward(self, action, next_state):
        # 根据动作和下一个状态计算奖励
        # 这里可以根据具体需求定义奖励函数
        # 例如，假设动作是请求的资源量，奖励是可用资源的总和
        return np.sum(next_state) - np.sum(action)  # 示例奖励函数

    def action_space_sample(self):
        # 随机生成一个动作，假设动作是请求的资源量
        return np.random.rand(self.num_servers)

# 示例用法
if __name__ == "__main__":
    env = EdgeServerEnv(num_servers=43, time_steps=1000 ,csv_file="edge_server_cpu_rate.csv")
    import matplotlib.pyplot as plt

    # 可视化第一个和第43个边缘服务器的未来时刻资源
    plt.figure(figsize=(10, 5))
    plt.plot(env.egde_servers[0].get_future_resource_capacity(), label='Server 1')
    plt.plot(env.egde_servers[-1].get_future_resource_capacity(), label='Server 43')
    plt.xlabel('Time Steps')
    plt.ylabel('Resource Capacity')
    plt.title('Future Resource Capacity of Server 1 and Server 43')
    plt.legend()
    plt.show()

    state = env.reset()
    done = False

    while not done:
        action = env.action_space_sample()  # 随机选择一个动作
        next_state, reward, done, info = env.step(action)
        print(f"State: {state}, Action: {action}, Reward: {reward}, Next State: {next_state}")
        state = next_state