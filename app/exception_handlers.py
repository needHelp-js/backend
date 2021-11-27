from fastapi.responses import JSONResponse


async def validation_exception_handler(request, exc):
    for error in exc.errors():
        return JSONResponse(
            {
                "Error": "Error de validacion de datos",
                "loc": error["loc"],
                "msg": error["msg"],
            },
            status_code=422,
        )
