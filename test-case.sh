#!/usr/bin/env bash

function mk_ent {
    echo "$2" | http --json POST "dcollect.tspnhq.com/entity/$1";
}

mk_ent foo '{"foo": 1}'
mk_ent bar '{"bar": 1}'
mk_ent template \
       '{"name":"foo","entries":[{"name":"step1","inputs":["a"],"command":{"kind":"identity"}}]}'


http --json POST "entwatcher.tspnhq.com/subscribe/my_dag" \
     trigger_url="http://compgraph:8000/triggerProcess" \
     entities:='{ "$Template": "template", "foo": "foo", "bar": "bar"}'

mk_ent foo '{"foo": 2}'
mk_ent bar '{"bar": 2}'
