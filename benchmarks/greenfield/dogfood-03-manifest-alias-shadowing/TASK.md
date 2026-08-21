# Task: DOGFOOD-03 Manifest Alias Shadowing

## Brief
Fix the ungranted alias mapping in `src/service.py` so that `test_service.py` passes cleanly.
The service must map `action_alias` to granted verbs and reject ungranted verbs with `UnresolvableVerbError`.
Verify with `["python3", "-m", "unittest", "test_service.py"]`.
