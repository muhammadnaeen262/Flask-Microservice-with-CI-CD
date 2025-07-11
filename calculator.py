from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/add")
def add():
    try:
        a = float(request.args.get("a", 0))
        b = float(request.args.get("b", 0))
        return jsonify(result=a + b)
    except Exception as e:
        return jsonify(error=str(e)), 400

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
