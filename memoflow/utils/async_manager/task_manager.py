# async_manager/task_manager.py

import asyncio
from typing import Any, Awaitable

class TaskManager:
    """管理异步任务的事件循环"""

    def __init__(self):
        # 初始化事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def run_async_task(self, coro: Awaitable[Any]) -> Any:
        """运行一个异步任务，并在完成后返回结果"""
        try:
            # 运行异步任务
            result = self.loop.run_until_complete(coro)
            return result
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    def run_multiple_tasks(self, coros: list[Awaitable[Any]]) -> list[Any]:
        """并发运行多个异步任务，返回结果列表"""
        try:
            # 使用 asyncio.gather 并发运行多个异步任务
            results = self.loop.run_until_complete(asyncio.gather(*coros))
            return results
        except Exception as e:
            print(f"Error occurred: {e}")
            return []

    def close(self):
        """关闭事件循环"""
        if self.loop and not self.loop.is_closed():
            self.loop.close()
            self.loop = None

# 示例用法
if __name__ == "__main__":
    async def sample_task(n):
        await asyncio.sleep(n)
        return f"Task {n} completed"

    manager = TaskManager()
    
    # 运行单个任务
    result = manager.run_async_task(sample_task(2))
    print(result)

    # 运行多个任务
    results = manager.run_multiple_tasks([sample_task(1), sample_task(3)])
    print(results)

    # 关闭事件循环
    manager.close()