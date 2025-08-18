import re

def get_contenttype(request_lines):
    headers = {}
    for line in request_lines[1:]:
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()

    return headers.get('content-type', '')

def type_handler(content):
        print(type(content))
        if isinstance(content, (dict,tuple)):
            return "application/json"
        else:
            return "text/html"

status_codes = {
    
    200: "OK",
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    405: "Method Not Allowed",
    429: "Too Many Requests",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    504: "Gateway Timeout"
}

def response_handler(code,content,type):
    response = (
        f"HTTP/1.1 {code} {status_codes[code]}\r\n"
        f"Content-Type: {type}\r\n"
        f"Content-Length: {len(content)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        f"{content}"
    )
    return response

