#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/rocha/Coding/Aether-D-System")
from vanguard.packages.adapters.models.env_loader import load_api_key
r = load_api_key("/home/rocha/Coding/Aether-D-System")
print("loaded" if r.ok else f"fail:{r.error.kind if r.error else 'unknown'}")
