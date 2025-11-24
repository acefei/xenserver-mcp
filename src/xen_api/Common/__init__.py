import asyncio

import XenAPI


class XenApiAsyncTimeoutException(Exception):
    """Exception raised for timeout during processing xenapi query

    Attributes:
        session -- the session where exception has occurred
        task -- the task which caused timeout
    """

    def __init__(self, session, task, message="XenAPI Timeout occurred in xen_api"):
        self.session = session
        self.task = task
        self.message = message
        super().__init__(self.message)


class Common:
    TIMEOUT = 5000

    @classmethod
    async def xenapi_task_handler(
        cls, session, task, ignore_timeout=False, show_progress=False
    ):
        cycle_passed = 0

        while session.xenapi.task.get_status(task) == "pending" and (
            cycle_passed <= cls.TIMEOUT or ignore_timeout
        ):
            await asyncio.sleep(1)

            if show_progress:
                progress = round(session.xenapi.task.get_progress(task), 2) * 100
                print(str(progress) + "% Complete!", flush=True)

            cycle_passed += 1

        if cycle_passed > cls.TIMEOUT:
            raise XenApiAsyncTimeoutException()

        session.xenapi.task.get_record(task)
        result = session.xenapi.task.get_result(task)
        error = session.xenapi.task.get_error_info(task)

        result = result.replace("<value>", "")
        result = result.replace("</value>", "")

        if len(error) > 0:
            raise XenAPI.Failure(error)

        return result
