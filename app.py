from flask import Flask, jsonify, request
from linguistic import linguistic

app = Flask(__name__)

@app.route("/api/linguistic", methods=["POST"])
def linguisticRoute():
	request_data = request.get_json(silent=True)

	if 'timeline' in request_data:
		timeline = request_data['timeline']
		if not timeline:
			return jsonify({ "error": "Timeline should not be empty" }), 400
	else:
		return jsonify({ "error": "Timeline is required" }), 400

	try:
		linguisticResponse = linguistic(timeline)
	except Exception as execption:
		print(execption)
		return jsonify({ "error": "Error happened during linguistic algo" }), 500

	return jsonify(linguisticResponse), 200

if __name__ == "__main__":
	app.run(debug=True)
