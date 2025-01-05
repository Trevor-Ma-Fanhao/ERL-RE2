import pandas as pd
import offline_task
import heapq  # 导入heapq优先级队列

class EdgeServer:
    def __init__(self, csv_file, id):
        self.id = id
        self.resource_capa = None
        self.latitude = None
        self.longitude = None
        self.coverage = None
        self.bandwidth = None
        self.task_trans_queue = None
        self.deployed_function_instance = None
        self.params = dict()
        self.offlinetask_list = []  # 增加离线任务列表

        df = pd.read_csv(csv_file)
        data = df.iloc[1:1001, id + 1].astype(int)
        max_value = data.max()
        self.future_resource_capacity = (max_value - data).tolist()

    def add_offlinetask(self, offlinetask):
        heapq.heappush(self.offlinetask_list, (offlinetask.require_source, offlinetask))  # 使用require_source作为优先级
        
    def get_next_offlinetask(self):
        return heapq.heappop(self.offlinetask_list)[1]  # 获取优先级最高的任务

    def run_offlinetask(self, t):
        # 找出在 t 时刻资源量内能运行的尽量多的任务
        valid_tasks = []
        remaining_capacity = self.future_resource_capacity[t]
        while self.offlinetask_list and self.offlinetask_list[0][0] <= remaining_capacity:  # 直接检查队列头部
            task = heapq.heappop(self.offlinetask_list)[1]  # 获取优先级最高的任务
            valid_tasks.append(task)
            remaining_capacity -= task.require_source
        
        # 获取被删除任务的 id 列表
        removed_ids = [task.id for task in valid_tasks]
        return removed_ids

# 测试代码
if __name__ == "__main__":
    server = EdgeServer("edge_server_cpu_rate.csv", 0)
    
    # 创建几个离线任务并添加到服务器
    task1 = offline_task.OfflineTask(id=1, require_source=10)
    task2 = offline_task.OfflineTask(id=2, require_source=20)
    task3 = offline_task.OfflineTask(id=3, require_source=15)

    server.add_offlinetask(task1)
    server.add_offlinetask(task2)
    server.add_offlinetask(task3)

    print("当前离线任务列表:", server.offlinetask_list)

    # 获取下一个离线任务
    next_task = server.get_next_offlinetask()
    print("下一个离线任务:", next_task)

    # 运行离线任务
    removed_tasks = server.run_offlinetask(0)
    print("已运行的任务ID:", removed_tasks)
    print("运行后离线任务列表:", server.offlinetask_list)



