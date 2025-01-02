import numpy as np
import edge_server_model


# 随机生成动作空间的方法
class ActionSpace:
    def __init__(self, num_servers):
        self.num_servers = num_servers
        self.actions = self._generate_actions()

    def _generate_actions(self):
        # 生成所有可能的动作组合，每个元素随机取-1, 0, 1
        return np.random.randint(-1, 2, (self.num_servers ** 3, self.num_servers))

    def sample(self):
        # 从动作空间中随机采样一个动作
        return self.actions[np.random.randint(0, len(self.actions))]

class EdgeServerEnv:

    def __init__(self, num_servers, time_steps, csv_file):
        self.num_servers = num_servers  # 边缘服务器的数量
        self.time_steps = time_steps      # 未来时间步数
        self.current_step = 0             # 当前时间步
        self.egde_servers = []  # 初始化服务器列表
        for i in range(num_servers):
            server = edge_server_model.EdgeServer(csv_file, i)
            self.egde_servers.append(server)  # 将每个服务器添加到列表中
        # 初始化离线任务
        self.offlinetasks = [offline_task.OfflineTask(id=i, require_source=np.random.randint(1, 101)) for i in range(1, 101)]
        self.offlinetasksfin = np.zeros(len(self.offlinetasks))  # 初始化离线任务完成时间数组为全0
        self.action_space = self.ActionSpace(num_servers)  # 创建动作空间实例

    def get_state_Q(self, state):
        # state 是一个长度为 k 的数组，代表了 k 个任务在边缘服务器上的部署情况
        # 计算任务平均完成时间的倒数
        # 这里可以根据具体需求定义计算逻辑
        # 例如，假设任务完成时间与资源量成正比
        # 将离线任务加入 边缘服务器队列中
        completion_times = np.zeros(len(self.offlinetasks))  # 初始化完成任务的时间列表

        for i, task_position in enumerate(state):
            task_position = ( task_position - 1 ) % self.num_servers
            self.egde_servers[task_position].add_offlinetask(self.offlinetasks[i])

        for t in range(self.time_steps):
            for server in self.egde_servers:
                # 每个边缘服务器运行任务 获得已完成任务id
                finish_tasks = server.run_offlinetask(t)
                for task_id in finish_tasks:
                    completion_times[task_id - 1] = t  # 更新完成时间为当前时间t
                    
        avg_completion_time = np.mean(completion_times[completion_times > 0]) if np.any(completion_times > 0) else 0

        q_value = 1 / avg_completion_time if avg_completion_time != 0 else 0
        return q_value



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