"""A disposable that survived the S4 exit. `MF-S4-001` fails on its presence.

The import graph is clean here on purpose: nothing imports this file. The
defect being planted is the directory's *existence* after the exit, because
"no source imports spike/" and "spike/ is gone" are different claims, and only
the second one prevents the disposable from being promoted later.
"""
