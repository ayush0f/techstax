from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection

client = MongoClient(
    "mongodb+srv://mickey919051:2moB3FXdAfixj4dj@ayush.uheu9rs.mongodb.net/?retryWrites=true&w=majority&appName=Ayush")
db = client.webhooks
collection = db.events
print(client.list_database_names())


@app.route('/webhook', methods=['POST'])
def webhook():
    print("tmkccccccccccccc")
    data = request.json
    event = request.headers.get('X-GitHub-Event')

    # defining all the vars
    author = action = from_branch = to_branch = request_id = timestamp = None

    if event == "push":
        author = data['pusher']['name']
        action = "PUSH"
        from_branch = data['ref'].split('/')[-1]
        request_id = data['after']
        timestamp = data['head_commit']['timestamp']

    elif event == "pull_request":
        pr = data['pull_request']
        author = pr['user']['login']
        from_branch = pr['head']['ref']
        to_branch = pr['base']['ref']
        request_id = str(pr['id'])
        timestamp = pr['created_at']
        action = data['action'].upper()
        if action == "CLOSED" and pr.get('merged'):
            action = "MERGE"

    else:
        print("Unhandled event:", event)
        return "Ignored", 200

    doc = {
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "request_id": request_id,
        "timestamp": timestamp
    }

    # Insert into MongoDB
    result = collection.insert_one(doc)
    print(f"Saved to MongoDB: {result.inserted_id}")

    return "Stored in MongoDB", 200


@app.route('/')
def index():
    return render_template('index.html')


def get_events():
    data = list(collection.find({}, {'_id': 0}).sort('timestamp', -1))
    return jsonify(data)


@app.route('/events')
def events():
    return get_events()


if __name__ == '__main__':
    app.run(port=5010)
