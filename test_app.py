import json, os, tempfile, threading, unittest
import urllib.request, urllib.error
from http.server import ThreadingHTTPServer

os.environ["DATA_FILE"] = os.path.join(tempfile.mkdtemp(), "messages.json")
import app


class APITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), app.APIHandler)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data, method=method,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_health(self):
        status, body = self.call("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")

    def test_post_valid(self):
        status, body = self.call("POST", "/messages", {"message": "halo"})
        self.assertEqual(status, 201)
        self.assertIn("created_at", body["message"])

    def test_post_empty(self):
        status, _ = self.call("POST", "/messages", {"message": "  "})
        self.assertEqual(status, 400)

    def test_post_too_long(self):
        status, _ = self.call("POST", "/messages", {"message": "x" * 501})
        self.assertEqual(status, 400)

    def test_delete_not_found(self):
        status, _ = self.call("DELETE", "/messages?index=999")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()