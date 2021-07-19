import time
from typing import List

class Driver_Scheduler:
    def __init__(self,MAX_NUM_OF_DRIVERS:int,idle_drivers:List):
        self.MAX_NUM_OF_DRIVERS=MAX_NUM_OF_DRIVERS # 最多同时开启driver的个数
        self.idle_drivers=idle_drivers # 空闲driver的id列表
        self.busy_drivers=[] # 繁忙driver
    def get_idle_driver(self): # 获取空闲driver
        print("空闲的driver",self.idle_drivers)
        # print(self.busy_drivers)
        if not self.idle_drivers: # 无空闲driver
            time.sleep(0.25)  # 继续等
            return self.get_idle_driver()  # 重新检测空闲
        else:
            idle_driver=self.idle_drivers.pop()
            self.busy_drivers.append(idle_driver)
            return idle_driver