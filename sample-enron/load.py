#!/usr/bin/env python
import asyncio
from jsonlines import Reader
import json
import os
import lzma
from nats.aio.client import Client as NATS

nc = NATS()

async def store_ent(entity: str, data):
    bfr = entity.encode("utf-8") + b"\n" + json.dumps(data).encode("utf-8")
    res = await nc.request("conthesis.cfs.put", bfr, timeout=5)
    return res

def get_all():
    with Reader(lzma.open("./enron.json.xz")) as reader:
        yield from reader

async def main():
    bfr = []
    await nc.connect("nats://localhost:4222", loop=asyncio.get_running_loop())
    for l in get_all():
        msg_id = l["messageId"].replace(".", "_")
        bfr.append(asyncio.create_task(store_ent(f"/entity/sample-enron/email/{msg_id}", l)))
        if len(bfr) > 1000:
            old_bfr = bfr
            await asyncio.wait(old_bfr)
            bfr = []
    await asyncio.wait(bfr)


if __name__ == "__main__":
    asyncio.run(main())
