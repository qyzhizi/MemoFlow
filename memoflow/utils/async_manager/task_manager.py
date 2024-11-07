import logging
import asyncio
from typing import Any, Awaitable, List
# import uvloop

# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

LOG = logging.getLogger(__name__)

class TaskManager:
    """管理异步任务的事件循环"""

    def __init__(self, batch_size=100):
        # 初始化事件循环
        LOG.info("create new event loop")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.batch_size = batch_size # 每次运行的任务数量

    def run_async_task(self, coro: Awaitable[Any]) -> Any:
        """运行一个异步任务，并在完成后返回结果"""
        try:
            # 运行异步任务
            result = self.loop.run_until_complete(coro)
            return result
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    # def run_multiple_tasks(self, coros: list[Awaitable[Any]]) -> list[Any]:
    #     """并发运行多个异步任务，返回结果列表"""
    #     try:
    #         # 使用 asyncio.gather 并发运行多个异步任务
    #         results = self.loop.run_until_complete(asyncio.gather(*coros))
    #         LOG.info("all async task is over")
    #         return results
    #     except Exception as e:
    #         print(f"Error occurred: {e}")
    #         return []

    def run_multiple_tasks(self, coros: List[Awaitable[Any]]) -> List[Any]:
        """并发运行多个异步任务，返回结果列表"""
        results = []

        try:
            # 分批处理任务
            for i in range(0, len(coros), self.batch_size):
                batch = coros[i:i + self.batch_size]  # 获取当前批次的任务
                batch_results = self.loop.run_until_complete(asyncio.gather(*batch))
                results.extend(batch_results)  # 将当前批次的结果添加到总结果中

            LOG.info("All async tasks are over")
            return results
        except Exception as e:
            LOG.error(f"run_until_complete, Error occurred: {e}")
            return results

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