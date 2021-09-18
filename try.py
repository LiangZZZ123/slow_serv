t
from http.server import HTTPServer, SimpleHTTPRequestHandler

from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080


class TestHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_PUT(self):
        self.send_response(200)
        self.end_headers()

        path = self.translate_path(self.path)

        if "Content-Length" in self.headers:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            with open(path, "wb") as out_file:
                out_file.write(body)
        elif "chunked" in self.headers.get("Transfer-Encoding", ""):
            with open(path, "wb") as out_file:
                while True:
                    line = self.rfile.readline().strip()
                    chunk_length = int(line, 16)

                    if chunk_length != 0:
                        chunk = self.rfile.read(chunk_length)
                        out_file.write(chunk)

                    # Each chunk is followed by an additional empty newline
                    # that we have to consume.
                    self.rfile.readline()

                    # Finally, a chunk size of 0 is an end indication
                    if chunk_length == 0:
                        break


httpd = HTTPServer(("", PORT), TestHTTPRequestHandler)

print("Serving at port:", httpd.server_port)
httpd.serve_forever()
