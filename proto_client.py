from proto import Server

print("Server version:", Server.version)

s = Server()
sample_list=[1,2,3]
@s.get("/")
def root():
    return f"{sample_list}"

@s.get("/json")
def json_route():
    return {"aj": 1}

@s.get("/try/{a}")
def try_route(a,b):
    return {"Item id": a,"new":b}

@s.get("/try2/{a}/{b}")
def a(a, b):
    return f"{a} is {b}"

@s.post("/submit/")
def handle_submit(a):
    return { "a": a}

@s.post("/post/{a}/{b}")
def a(c,a,b):
    return f"{c} is {a} is {b}"

@s.post("/b/{a}")
def vc(a):
    return a

@s.post('/upload')
def g(raw_body:bytes):
    with open('resume.pdf','wb') as f:
        f.write(raw_body)
    return "File Received"

s.run()