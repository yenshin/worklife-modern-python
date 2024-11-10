from .routes import health, employee


def add_app_routes(app):
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(employee.router, prefix="/employee", tags=["Employee"])
