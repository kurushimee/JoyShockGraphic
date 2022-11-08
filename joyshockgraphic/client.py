import asyncio
import subprocess
from psutil import Process, process_iter


class Client:

    async def __init(self):
        proc_jsm = await asyncio.subprocess.create_subprocess_exec(
            "JoyShockMapper_x64/JoyShockMapper.exe")

        # Go through every running process, append process if it's conhost.exe
        # and the parent process is JoyShockMapper.exe
        self.pid_conhost = sum([
            p.info["pid"] for p in process_iter(["pid", "name"])
            if p.info["name"] == "conhost.exe"
            and Process(p.info["pid"]).ppid() == proc_jsm.pid
        ])

        await proc_jsm.wait()

    def init_client(self):
        asyncio.run(self.__init())

    def send_command(self, commands):
        subprocess.run([
            "joyshockgraphic/scripts/send_command.bat",
            f"{self.pid_conhost}",
            f"{commands}",
        ])
