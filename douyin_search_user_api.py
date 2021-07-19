from flask import Flask,jsonify,request
from douyin_search_user import *
from douyin_search_user_driver_scheduler import Driver_Scheduler

app=Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def usage():
    return '抖音搜索用户接口：/douyin/search/user/?username=XXXX'

@app.route('/douyin/search/user/',methods=['GET'])
def douyin_search_user():
    if request.method!="GET":
        return jsonify(
            {
                "code": 2,
                "message": "失败",
                "data": "请求方式错误"
            }
        )
    username=request.args.get('username')
    if username is None:
        return jsonify(
            {
                "code": 2,
                "message": "失败",
                "data": "缺乏必要参数"
            }
        )
    driver_id=driver_scheduler.get_idle_driver()
    print("搜索：",username)
    print("分配到",driver_id)
    try:
        data=drivers[driver_id].user_search(username)
        # 更新driver状态
        driver_scheduler.busy_drivers.remove(driver_id)
        driver_scheduler.idle_drivers.append(driver_id)

        return jsonify(
            {
                "code": 1,
                "message": "成功",
                "data": {
                    "paging": {
                        "count": len(data)
                    },
                    "data": data
                }
            }
        )
    except Exception as e:
        print(e,'\n搜索关键字"{}"的driver: {}无法继续运行'.format(username,driver_id))
        driver_scheduler.busy_drivers.remove(driver_id) # 移除没用的driver
        print("正在创建一个新的driver...")
        driver_scheduler.idle_drivers.append(create_driver())
        return jsonify(
            {
                "code": 2,
                "message": "失败",
                "data": "服务器繁忙，请稍后再试"
            }
        )

def create_driver():
    driver = Driver()
    driver.open_driver()
    driver_id=id(driver)
    drivers[driver_id] = driver
    return driver_id

if __name__=='__main__':
    drivers={} # driver_id:driver
    MAX_NUM_OF_DRIVERS=4
    print('正在启动{}个无头浏览器...'.format(MAX_NUM_OF_DRIVERS))
    for _ in range(MAX_NUM_OF_DRIVERS):
        create_driver()
    print("启动完毕")
    # print(drivers)
    driver_scheduler=Driver_Scheduler(MAX_NUM_OF_DRIVERS,list(drivers.keys()))
    app.run()