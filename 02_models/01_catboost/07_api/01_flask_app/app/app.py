
from flask import Flask, request, jsonify, Response
import pickle
import traceback
import logging
from waitress import serve
import pandas as pd 
pd.options.mode.chained_assignment = None # suppress warning

# set up logging
logging.basicConfig(
    filename='flask_app.log', 
    level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s',
)

# instantiate app
app = Flask(__name__)

# route the model to http://127.0.0.1:5000/
@app.route('/', methods=['GET','POST']) # GET for status code, POST for predictions
# logic for GET and POST requests
def predict():
    if request.method == 'GET':
        # log it
        logging.info('GET request received')
        # get status code
        int_status_code = Response(status=200).status_code
        # return
        return f'Status code: {int_status_code}'
    elif request.method == 'POST':
        try:
            # import parser
            str_message = 'Loading parser...'
            logging.info(str_message)
            print(str_message)
            print('')
            cls_parse_payload = pickle.load(open('cls_parser.pkl', 'rb'))
            
            # get payload
            str_message = 'Getting request...'
            logging.info(str_message)
            print(str_message)
            print('')
            dict_json_request = request.get_json()
            
            # parse payload
            str_message = 'Parsing payload...'
            logging.info(str_message)
            print(str_message)
            cls_parse_payload.get_data(dict_json_request)
            cls_parse_payload.engineer_pmt_hx()
            cls_parse_payload.shared_preprocessing()
            cls_parse_payload.generate_predictions()
            cls_parse_payload.apply_policies()
            cls_parse_payload.adverse_action()
            cls_parse_payload.counter_offers()
            cls_parse_payload.generate_output()
            
            # extract output
            str_message = 'Extracting output...'
            logging.info(str_message)
            print(str_message)
            print('')
            dict_output = cls_parse_payload.dict_output
            # return output_final
            return dict_output['output_final']
        except Exception as e:
            str_message = 'Exception occurred'
            logging.error(
                str_message, 
                exc_info=True,
            )
            #return traceback in json
            return jsonify({'error': str(e)})

# run app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
