#!/usr/bin/env python

import sys
import json
import httplib2
from jsonschema import validate, Draft4Validator
from jsonschema.exceptions import ValidationError

try: input_json = sys.argv[1]
except IndexError: sys.exit("Usage: %s input_json" % sys.argv[0])

network = httplib2.Http()
response, content = network.request("http://developer.mpds.io/mpds.schema.json")
assert response.status == 200

schema = json.loads(content)
Draft4Validator.check_schema(schema)

target = json.loads(open(input_json).read())

if not target.get("npages") or not target.get("out") or target.get("error"):
    sys.exit("Unexpected API response")

try:
    validate(target["out"], schema)
except ValidationError, e:
    raise RuntimeError(
        "The item: \r\n\r\n %s \r\n\r\n has an issue: \r\n\r\n %s" % (
            e.instance, e.context
        )
    )
