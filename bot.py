import flask
from flask import request
from flask import jsonify
from flask_cors import CORS
import json
import os
from alexa import AlexaRequest
import requests
import time
from neo4j.v1 import GraphDatabase

app = flask.Flask(__name__)
CORS(app,resources={r"/*": {"origins": "*"}})

password = os.environ['NEO4J_PASS'] if 'NEO4J_PASS' in os.environ else ""
driver = GraphDatabase.driver(os.environ['NEO4J_URL'], auth=("neo4j", password))
session = driver.session()

@app.route("/")
def home():
    return jsonify({message:"hello"})

@app.route("/alexa", methods=['GET','POST'])
def alexa():
    data = request.get_json(force=True)
    alexaRequest = AlexaRequest(data)

    if alexaRequest.LAUNCH_REQUEST == alexaRequest.getRequestType():
        return jsonify(alexaRequest.buildResponse('Welcome to Linkathon', False))
    elif alexaRequest.getIntent() == 'subjectCount':
        return jsonify(handleSubjectCount(alexaRequest))
    elif alexaRequest.getIntent() == 'subjectQuery':
        return jsonify(handleSubjectQuery(alexaRequest))
    

    return jsonify(alexaRequest.buildResponse())

def handleSubjectCount(alexaRequest):
    q = "MATCH (n:studySubject) RETURN count(n) AS c"
    result = list(session.run(q))

    return alexaRequest.buildResponse('There are ' + str(result[0]['c']) + ' subjects', True)

def handleSubjectQuery(alexaRequest):
    q = "MATCH (n:studySubject) WHERE n.%s %s toInteger(%s) RETURN count(n) AS c"
    slots = alexaRequest.getSlots()
    operator = slots['operator']['value']
    operatorF = ''
    if operator == 'greater than':
        operatorF = '>'
    else:
        operatorF = '<'
    
    query = q % (slots['column']['value'], operatorF, slots['val']['value'])
    print(query)
    result = list(session.run(query))
    c = result[0]['c']

    response = 'There are %d subjects having %s %s %s' % (c, slots['column']['value'], operator, slots['val']['value'])
    
    return alexaRequest.buildResponse(response, True) 



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)