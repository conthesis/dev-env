#!/usr/bin/env python3
import asyncio
import json

import httpx

http = httpx.AsyncClient()


async def cas_store(data):
    if isinstance(data, dict):
        data = json.dumps(data)
    resp = await http.post("http://cas.tspnhq.com/v1/store", data=data)
    resp.raise_for_status()
    return await resp.aread()


async def insert_vsn(entity: str, pointer: bytes):
    resp = await http.post(
        f"http://dcollect.tspnhq.com/entity-ptr/{entity}", data=pointer
    )
    resp.raise_for_status()
    return resp.json()


async def store_ent(entity: str, data):
    ptr = await cas_store(data)
    return await insert_vsn(entity, ptr)


async def store_ents(ents):
    await asyncio.gather(*[store_ent(ent, val) for (ent, val) in ents])


async def subscribe(name):
    resp = await http.post(f"http://entwatcher.tspnhq.com/v1/subscribe/{name}")
    resp.raise_for_status()
    return resp


async def main():
    await store_ents(
        [
            ("foo", {"foo": 1}),
            ("bar", {"bar": 1}),
            (
                "template",
                {
                    "name": "foo",
                    "entries": [
                        {"name": "step1", "inputs": ["a"], "action": "identity"}
                    ],
                },
            ),
            (
                "_conthesis.watcher.my_dag_watcher",
                {
                    "kind": "TriggerDAG",
                    "properties": [
                        {"name": "$Template", "kind": "ENTITY", "value": "template",},
                        {"name": "foo", "kind": "ENTITY", "value": "foo",},
                        {"name": "bar", "kind": "ENTITY", "value": "bar",},
                    ],
                },
            ),
        ]
    )
    await store_ents(
        [("foo", {"foo": 2}), ("bar", {"bar": 2}),]
    )


asyncio.run(main())
