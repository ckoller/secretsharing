from app import create_app
import config

if __name__ == '__main__':
    app = create_app()
    host = config.CONFIG_VALUES['host']
    port = config.CONFIG_VALUES['port']
    app.run(debug=True, host=host, port=port)
