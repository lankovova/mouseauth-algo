from flask import Flask, jsonify, request
from Linguistic import linguistic

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
		linguisticResponse = linguistic(timelines)
	except:
		print("Error happened during linguistic algo")

	return jsonify(linguisticResponse)

if __name__ == "__main__":
	app.run(debug=True)
