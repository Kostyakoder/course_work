from flask import Flask, request

app = Flask(__name__)

@app.route("/private/api/v3/register/client", methods=['POST'])
def create_client():
    print(request.get_json())
    return "", 200


app.run(host = '0.0.0.0', port = 8080)