import uuid
import sys


def getId(prefix: str = "") -> str:
    return f'{prefix}{str(uuid.uuid4())}'


def Syserror(e):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("ERROR --> Mesaage: ", e)
    print("ERROR --> Exception type: ", exception_type)
    print("ERROR --> File name: ", filename)
    print("ERROR --> Line number: ", line_number)
    return None
