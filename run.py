from app import boot_app
import argparse

app = boot_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask web server.')
    parser.add_argument('--debug', default=False, help='debug mode bool value', type=bool)
    args = parser.parse_args()

    app.run(debug=args.debug)