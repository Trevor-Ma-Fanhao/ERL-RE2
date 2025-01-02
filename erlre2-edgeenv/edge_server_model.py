import pandas as pd
import offline_task

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
        self.offlinetask_list.append(offlinetask)

    def run_offlinetask(self, t):
        # 找出在 t 时刻资源量内能运行的尽量多的任务
        valid_tasks = []
        remaining_capacity = self.future_resource_capacity[t]
        for task in sorted(self.offlinetask_list, key=lambda x: x.require_source):
            if task.require_source <= remaining_capacity:
                valid_tasks.append(task)
                remaining_capacity -= task.require_source
        # 获取被删除任务的 id 列表
        removed_ids = [task.id for task in valid_tasks]
        # 从离线任务列表中删除这些任务
        self.offlinetask_list = [task for task in self.offlinetask_list if task not in valid_tasks]
        return removed_ids



