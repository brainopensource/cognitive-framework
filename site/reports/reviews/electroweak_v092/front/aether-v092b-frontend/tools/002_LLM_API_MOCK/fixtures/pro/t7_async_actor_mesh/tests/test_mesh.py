import unittest
from mesh import ActorSystem

class TestActorMesh(unittest.TestCase):
    def test_actor_message_routing(self):
        sys = ActorSystem()
        received = []
        sys.spawn("echo", lambda m: received.append(m))
        sys.send("echo", {"op": "ping", "val": 42})
        actor = sys.actors["echo"]
        actor.process_one()
        self.assertEqual(received, [{"op": "ping", "val": 42}])

if __name__ == "__main__":
    unittest.main()
