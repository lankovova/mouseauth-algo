from flask import Flask, jsonify, request
from linguistic import linguistic

app = Flask(__name__)

@app.route("/api/linguistic", methods=["POST"])
def linguisticRoute():
	request_data = request.get_json(silent=True)

	if 'timelines' in request_data:
		timelines = request_data['timelines']
		if not timelines:
			return jsonify({ "error": "Timelines should not be empty" }), 400
	else:
		return jsonify({ "error": "Timelines is required" }), 400

	try:
		isUserOK = linguistic(timelines=timelines, userID="TEST") # Change userID to dynamic
	except Exception as execption:
		print(execption)
		return jsonify({ "error": "Error happened during linguistic algo" }), 500

	if isUserOK:
		return jsonify({ "message": "User is OK!" }), 200

	return jsonify({ "message": "Wrong user"}), 200

if __name__ == "__main__":
	app.run(debug=True)
