import socket
import threading
import json

from packages.helper import type_handler, response_handler, get_contenttype
from packages.Methods import handler
from packages.Base_Handler import dec_handler,url

class Server():
    version = '1.0.0.5'  #recorrect client_methods

    def __init__(self):
        print("Server Started")
        self.host = "127.0.0.1"
        self.port = 8080
        self.routes = {"GET": [], "POST": [], "PATCH": [], "PUT": [], "DELETE": [],"MIDDLEWARE":[]}
        self.middleware_track={}

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.host, self.port))
        except socket.error as e:
            print(f"{e} Failed to Initialise the server")
        else:
            self.s.listen()
            print("Server is listening")
    
    def get(self, path:str):
        def decorator(func):
            dec_handler(path,func,"GET",self.routes)
        return decorator
            
    def post(self, path:str):
        def decorator(func):
            dec_handler(path,func,"POST",self.routes)
        return decorator

    def put(self, path:str):
        def decorator(func):
            dec_handler(path,func,"PUT",self.routes)
        return decorator

    def patch(self, path:str):
        def decorator(func):
            dec_handler(path,func,"PATCH",self.routes)
        return decorator

    def delete(self, path:str):
        def decorator(func):
            dec_handler(path,func,"DELETE",self.routes)
        return decorator

    
    def handle_client(self, client:str):
        try:
            message = client.recv(4096)
            if not message:
                client.close()
                return
            #post-man input_feed section

            #headers_section ---> request_lines(contains method,path,HTTP_Version)
            headers_section, _, body = message.partition(b'\r\n\r\n')
            request_lines = headers_section.decode().splitlines()

            method, path, Http_version = request_lines[0].split(' ')
            if method in ['OPTIONS', "HEAD"]:
                response = response_handler(405, "Method Not defined", "application/text")  # AVOID trigger
                client.sendall(response.encode())
                return

            """Reference for method,path,HTTp_Version
            method--> GET/PUT/PATCH/DELETE/POST
            path ---->/items/
            Http_version ---> HTTP/1.1
            """

            content_type_header = get_contenttype(request_lines)

            for pattern, param_names, annotations, default_map, func in self.routes[method]:
                match = pattern.match(path)
                if not match:
                    continue
                raw_params = match.groupdict()
                print("param_names", param_names)

                response_body = handler(body, content_type_header, func, raw_params, param_names, annotations, default_map)
                print(response_body)

                content_type = type_handler(response_body)
                print("content ype",content_type)

                if isinstance(response_body, dict):
                    response_body = json.dumps(response_body)

                response = response_handler(200, response_body, content_type)
                client.sendall(response.encode())
                break
            else:
                response = response_handler(404, "Route not found", "text/plain")
                client.sendall(response.encode())
        finally:
            client.close()

    def run(self):
        print("Server is running")
        while True:
            client, add = self.s.accept()
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()
