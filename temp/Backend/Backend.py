from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from urllib.parse import quote_plus
import tldextract
from PictureSimilarity import PictureSimilarity
from CodeSimilarity import CodeSimilarity
from Models import Models
from FeatureExtraction import FeatureExtraction

app = Flask(__name__)
CORS(app)

username = quote_plus('SIH_user')
password = quote_plus('chakDeIndia@2023')
uri = "mongodb+srv://%s:%s@cluster0.3fajycc.mongodb.net/?retryWrites=true&w=majority" % (
    username, password)
client = MongoClient(uri)
db = client['HackathonDB']
collection = db['URLs']


@app.route("/Predict", methods=['POST'])
def Predict():
    try:
        data = request.get_json()
        url = data['url']
        url_parsed = tldextract.extract(url)
        domain = url_parsed.domain
        suffix = url_parsed.suffix
        subdomain = url_parsed.subdomain
        if subdomain != '':
            full_domain_name = "https://" + subdomain + "." + domain + "." + suffix
        else:
            full_domain_name = "https://" + domain + "." + suffix

        row = collection.find_one({'url': full_domain_name})
        if row:
            return jsonify({'ok': True, 'detectionResult': row['result'], 'score': row['result'], 'type': 'From Database'}), 200

        PictureSimilarityResult, websites_to_check = PictureSimilarity(
            url).getSimilarity()
        
        if len(websites_to_check) != 0:
            collection.insert_one({'url': full_domain_name, 'result': 1, 'score': 0})
            return jsonify({"ok": True, "detectionResult": 1, "score": PictureSimilarityResult, "type": "Picture Similarity"}), 200
        
        if PictureSimilarityResult == 0:
            collection.insert_one({'url': full_domain_name, 'result': 0, 'score': 0})
            return jsonify({"ok": True, "detectionResult": 0, "score": PictureSimilarityResult, "type": "Picture Similarity"}), 200
        
        if PictureSimilarityResult == 64:
            collection.insert_one({'url': full_domain_name, 'result': 0, 'score': 0})
            return jsonify({"ok": True, "detectionResult": 0, "score": PictureSimilarityResult, "type": "Picture Similarity"}), 200
        if len(websites_to_check) == 0:
            collection.insert_one({'url': full_domain_name, 'result': 1, 'score': 0})
            return jsonify({"ok": True, "detectionResult": 1, "score": PictureSimilarityResult, "type": "Picture Similarity"}), 200
        # if PictureSimilarityResult < 15:
        #     collection.insert_one(
        #         {'url': full_domain_name, 'result': 1, 'score': float(1 - PictureSimilarityResult / 64)})
        #     return jsonify({"ok": True, "detectionResult": 1, "score": PictureSimilarityResult, "type": "Picture Similarity"}), 200

        print(PictureSimilarityResult, websites_to_check)

        # CodeSimilarityResult = 0

        # for website in websites_to_check:
        #     CodeSimilarityResult = max(
        #         CodeSimilarityResult, CodeSimilarity(website, url).compare_html_dom())

        # if CodeSimilarityResult > 90:
        #     collection.insert_one(
        #         {'url': full_domain_name, 'result': 1, 'score': float(CodeSimilarityResult / 100)})
        #     return jsonify({"ok": True, "detectionResult": 1, "score": CodeSimilarityResult, "type": "Code Similarity"}), 200

        # Sample = FeatureExtraction(url).getFeatures()
        # print(Sample)
        # score, result = Models(Sample).getResults()
        # print(score, result)

        # collection.insert_one(
        #     {'url': full_domain_name, 'result': int(result), 'score': float(score)})
        # return jsonify({"ok": True, "detectionResult": result, "score": score, "type": "Model Evaluation"}), 200

    except Exception as e:
        print(e)
        return jsonify({"ok": False, "detectionResult": 0, "score": 0}), 400

@app.route("/recenturls")
def recentURLs():
    recent = collection.find().sort({'_id': -1}).limit(10)
    response = []
    for x in recent:
        url = x['url']
        if x['result'] == 0:
            response.append({'url': url, 'result': 'clean'})
        else:
            response.append({'url': url, 'result': 'suspicious'})
    return response

@app.route("/scanUrls", methods=['POST'])
def scanUrls():
    data = request.get_json()
    urls = data['urls']
    detection_result = []
    for url in urls:
        PictureSimilarityResult, websites_to_check = PictureSimilarity(url).getSimilarity()
        if len(websites_to_check) != 0:
            collection.insert_one({'url': url, 'result': 1, 'score': 0})
            detection_result.append({"url":url,"status":"Phishing"})
        
        if PictureSimilarityResult == 0:
            collection.insert_one({'url': url, 'result': 0, 'score': 0})
            detection_result.append({"url":url,"status":"Safe"})
    return jsonify({"ok":True, "Result":detection_result}), 200

@app.route("/getHash",methods=["POST"])
def getHash():
    data = request.get_json()
    urls = data["urls"]
    print(urls)
    detection_result = []
    for url in urls:
        try:
            image = PictureSimilarity(url).take_screenshot(url)
            hash = PictureSimilarity(url).calculate_image_hash(image)
            detection_result.append({"url":url,"hash":str(hash)})
        except Exception as  e:
            detection_result.append({"url":url,"hash":"None"})
    return jsonify({"ok":True, "Result":detection_result}), 200

if __name__ == "__main__":
    app.run(debug=True)