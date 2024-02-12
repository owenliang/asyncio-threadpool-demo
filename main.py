from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI,Request,Response
import uvicorn
import asyncio
import time 

# 创建web
app=FastAPI()

#   创建线程池
threadpool=ThreadPoolExecutor(max_workers=200)

#   第一个版本
@app.get('/ver1')
async def ver1(request: Request):
    # 获取参数
    msg=request.query_params.get('msg')

    # 获取async io event loop
    loop=asyncio.get_event_loop()
    
    # 准备计算任务
    task={
        'msg': msg,
        'event': asyncio.Event(),
        'result': None,
    }
    
    # 计算函数
    def handle_task():
        print('task received:',task['msg'])
        task['result']=task['msg'].lower()
        time.sleep(2) # 模拟线程阻塞
        def async_callback():
            print('task ends notified:',task['result'],asyncio.get_event_loop())
            task['event'].set()
        loop.call_soon_threadsafe(async_callback)
    
    # 提交并等待结果
    threadpool.submit(handle_task)
    await task['event'].wait()
    
    return Response(task['result'])

#   第一个版本
@app.get('/ver2')
async def ver2(request: Request):
    # 获取参数
    msg=request.query_params.get('msg')

    # 获取async io event loop
    loop=asyncio.get_event_loop()
    
    # 准备计算任务
    task={
        'msg': msg,
    }
    
    # 计算函数
    def handle_task():
        print('task received:',task['msg'])
        result=task['msg'].lower()
        time.sleep(2) # 模拟线程阻塞
        return result
    
    # 提交并等待结果
    result=await loop.run_in_executor(threadpool,handle_task)
    return Response(result)


if __name__=='__main__':
    uvicorn.run(app,host='localhost',port=8000)