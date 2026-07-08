

def FieldFromJsonResponse(field:str,response):
    try:
        respJson:dict = response.json()
        field = respJson[field]
        return (field, None)
    except Exception as e:
        return ("",f"Failed to parse token from body: {e}")
