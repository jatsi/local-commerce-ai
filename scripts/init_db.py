from apps.api_gateway.app.services.bootstrap import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created")
