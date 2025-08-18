import json
import re

def parse_body(body, content_type_header):
    content_type_header_lower = content_type_header.lower().strip()
    #content type will be octet stream/multi
    if "application/octet-stream" in content_type_header_lower:
        return {"raw_body": body}  
    
    if isinstance(body, bytes):
        try:
            decoded_body = body.decode()
        except UnicodeDecodeError:
            return {"raw_body": body}
    else:
        decoded_body = body

    if "application/json" in content_type_header_lower and decoded_body:
        try:
            return json.loads(decoded_body)
        except json.JSONDecodeError:
            return {}

    if "application/x-www-form-urlencoded" in content_type_header_lower and decoded_body:
        form_data = {}
        pairs = re.findall(r'([^=&]+)=([^&]*)', decoded_body)
        for key, value in pairs:
            key = bytes(re.sub(r'\+', ' ', key), 'utf-8').decode('unicode_escape')
            value = bytes(re.sub(r'\+', ' ', value), 'utf-8').decode('unicode_escape')
            form_data[key] = value
        return form_data

    if "multipart/form-data" in content_type_header_lower and decoded_body:
        """ ------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n
            Content-Disposition: form-data; name="username"\r\n
            \r\n
            john_doe\r\n
            ------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n
            Content-Disposition: form-data; name="email"\r\n
            \r\n
            john@example.com\r\n
            ------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n"""
        match = re.search(r'boundary=(.*)', content_type_header_lower)
        boundary = match.group(1) if match else ''
        form_data = {}
        parts = re.split(rf'--{re.escape(boundary)}(?:--)?\r\n', decoded_body)
        for part in parts:
            if 'Content-Disposition' in part:
                name_match = re.search(r'name="([^"]+)"', part)
                if not name_match:
                    continue
                key = name_match.group(1)
                value_match = re.search(r'\r\n\r\n(.*)', part, re.DOTALL)
                if value_match:
                    value = value_match.group(1).strip()
                    form_data[key] = value
        return form_data

    if "text/plain" in content_type_header_lower and decoded_body:
        return {"raw_body": decoded_body.strip()}
    return {}

def handler(body, content_type_header, func, url_params, param_names, annotations=None, default_map=None):
    body_params = parse_body(body, content_type_header)
    combined_params = {**url_params, **body_params}

    print("Body Params",body_params)
    print("combined params",combined_params)

    final_params = {}
    errors = {}
    if "raw_body" in body_params:
        combined_params["raw_body"] = body_params["raw_body"]

    for param in param_names:
        value = combined_params.get(param)

        if value is None:
            if default_map and param in default_map:
                value = default_map[param]
            else:
                errors[param] = "Missing required parameter"
                continue

        if annotations and param in annotations:
            try:
                value = annotations[param](value)
            except Exception as e:
                errors[param] = f"Invalid type for '{param}': {str(e)}"
                continue

        final_params[param] = value

    if errors:
        return {
            "error": "Wrong Arguements ",
            "details": errors
        }
    return func(**final_params)
    
