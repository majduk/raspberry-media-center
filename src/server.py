from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import projector
import traceback
import logging
import sys

hostName = "raspberrypi"
serverPort = 8080

HANDLERS = {
    'projector': projector.ProjectorDriver(projector.GPIODriver())
}

formatter = logging.Formatter('%(name)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
HANDLERS['projector']._logger.setLevel(logging.DEBUG)
HANDLERS['projector']._logger.addHandler(handler)


class HttpHandler(BaseHTTPRequestHandler):

    def __send_ok(self, msg = "OK"):
        self.send_response(200, "OK")
        self.end_headers()
        self.wfile.write(bytes(str(msg), "utf-8"))

    def __send_404(self):
        self.send_response(404, "NOT FOUND")
        self.end_headers()
        self.wfile.write(bytes("NOT_FOUND", "utf-8"))

    def __send_500(self, exception):
        self.send_response(500, "INTERNAL ERROR")
        self.end_headers()
        self.wfile.write(bytes(str(exception), "utf-8"))

    def do_GET(self):
        if self.path == '/':
            self.__send_ok()
            return
        try:
            path_map = self.path.split("/")
            handler = HANDLERS[path_map[1]]
            if len(path_map) > 2:
                method = path_map[2]
            else:
                method = "status"
            self.log_message("Start Handler: %s, Method: %s", str(handler), method)
            ret = getattr(handler, method)()
            self.log_message("Completed Handler: %s, Method: %s, Respone: %s", str(handler), method, ret)
            if ret:
                self.__send_ok(ret)
                return
            else:
                self.__send_ok()
                return
        except KeyError:
            self.__send_404()
            return
        except AttributeError:
            self.__send_404()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.log_error("%s", lines)
            self.__send_500(e)
            return
        

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), HttpHandler)
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
