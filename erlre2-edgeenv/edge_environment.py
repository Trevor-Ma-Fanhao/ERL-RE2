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
        # 初始化服务器列表
        self.egde_servers = []  
        for i in range(num_servers):
            server = edge_server_model.EdgeServer(csv_file, i)
            self.egde_servers.append(server)  # 将每个服务器添加到列表中
        # 初始化离线任务
        self.offlinetasks = [offline_task.OfflineTask(id=i, require_source=np.random.randint(1, 101)) for i in range(1, 101)]
        self.offlinetasksfin = np.zeros(len(self.offlinetasks))  # 初始化离线任务完成时间数组为全0
        self.action_space = self.ActionSpace(num_servers)  # 创建动作空间实例
        # 初始化当前状态
        self.current_state = np.random.randint(1, self.num_servers + 1, size=len(self.offlinetasks))

    def get_state_Q(self, state):
        
        # 计算状态的Q值
        # 这块代码先放着 
        return q_value


    def reset(self):
        # 重置环境到初始状态
        self.current_step = 0
        # 随机初始化当前状态
        self.current_state = np.random.randint(1, self.num_servers + 1, size=len(self.offlinetasks))
        # 返回reset之后的当前状态
        return self.current_state

    def step(self, action):
        # 执行动作并返回下一个状态、奖励和是否结束
        if self.current_step >= self.time_steps - 1:
            done = True
            next_state = current_state
            reward = 0  # 结束时的奖励可以根据需求定义
        else:
            done = False
            self.current_step += 1
            next_state = (self.current_state + action - 1) % self.num_servers + 1
            reward = self.calculate_reward(self.current_state, next_state)  # 根据下一个状态计算奖励

        return next_state, reward, done, {}

    def calculate_reward(self, current_state, next_state):
        
        return self.calculate_state_value(next_state) - self.calculate_state_value(current_state)
    
    def calculate_state_value(self, state):
        completion_times = np.zeros(len(self.offlinetasks))  # 初始化完成任务的时间列表

        for i, task_position in enumerate(state):
            task_position = (task_position - 1) % self.num_servers
            self.egde_servers[task_position].add_offlinetask(self.offlinetasks[i])

        for t in range(self.time_steps):
            if np.all(completion_times > 0):  # 检查所有任务是否已完成
                break  # 如果所有任务都已完成，退出循环
            for server in self.egde_servers:
                # 每个边缘服务器运行任务 获得已完成任务id
                finish_tasks = server.run_offlinetask(t)
                for task_id in finish_tasks:
                    completion_times[task_id - 1] = t  # 更新完成时间为当前时间t

        avg_completion_time = np.mean(completion_times[completion_times > 0]) if np.any(completion_times > 0) else 0
        state_value = 1 / avg_completion_time if avg_completion_time != 0 else 0
        return state_value

        

    

    def action_space_sample(self):
        # 随机生成一个动作，假设动作是请求的资源量，离散值范围 -1, 0, 1
        return np.random.choice([-1, 0, 1], size=self.num_servers)

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