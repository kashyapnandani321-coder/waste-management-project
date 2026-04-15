from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Backend is running 🚀"

# Form data receive karne ke liye
@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    location = data.get('location')
    description = data.get('description')

    print("Location:", location)
    print("Description:", description)

    return jsonify({"message": "Data received successfully"})

if __name__ == '__main__':
    app.run(debug=True)
