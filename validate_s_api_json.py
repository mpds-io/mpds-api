
import sys
import ujson as json
from jsonschema import validate, Draft3Validator

try: f, t = sys.argv[1], sys.argv[2]
except IndexError: sys.exit("Usage: schema input_JSON")

schema = json.loads(open(f).read())
Draft3Validator.check_schema(schema)

target = json.loads(open(t).read())

if not target.get("npages") or not target.get("out") or target.get("error"):
    sys.exit("Not a valid API response")

for sentry in target["out"]:
    validate(sentry, schema)

sys.exit(0)
