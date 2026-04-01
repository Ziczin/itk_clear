from src.utils.request_builder import ErrorCodeHandler

handler = ErrorCodeHandler("TestAPI")

try:
    raise handler(404)
except handler[404] as e:
    print("Поймали 404!", e)
    print("Type:", type(e))

try:
    raise handler(400, {"body": 123})
except handler[400] as e:
    print("Поймали 400 с телом!", e)
    print("Type:", type(e))
