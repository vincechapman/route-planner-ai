from route_finder import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, load_dotenv=True)