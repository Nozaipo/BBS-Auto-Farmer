import asyncio
import subprocess
from bot import UpdateInfo
from mitmproxy import options
from mitmproxy.tools import dump


class RequestLogger:
    def request(self, flow):
        print(flow.request)

async def start_proxy():
    opts = options.Options(listen_host="0.0.0.0", listen_port=8080)

    master = dump.DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False,
    )
    master.addons.add(UpdateInfo())
    # master.addons.add(RequestLogger())
    
    subprocess.run("setproxy localhost:8080", capture_output=True)
    print("Proxy ON")
    await master.run()
    print("ok")

    return master

if __name__ == '__main__':
    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        subprocess.run("setproxy none", capture_output=True)
        print("Proxy OFF")