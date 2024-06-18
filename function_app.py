import logging
import azure.functions as func
import json
from azure.cosmos import exceptions, CosmosClient
from datetime import datetime

# Configurações para conectar ao Cosmos DB
ENDPOINT = 'https://miniprojeto-edu-gui-joao-1.documents.azure.com:443/'

DATABASE_ID = 'QuizGami'
SCORES_CONTAINER_ID = 'Scores'

app = func.FunctionApp()

@app.function_name(name="FinalizeQuiz")
@app.route(route="FinalizeQuiz", auth_level=func.AuthLevel.ANONYMOUS)
def FinalizeQuiz(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('FinalizeQuiz HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        username = req_body.get('username')
        category = req_body.get('category')
        score = req_body.get('score')

        # Conectar ao Cosmos DB
        client = CosmosClient(ENDPOINT, KEY)
        database = client.get_database_client(DATABASE_ID)
        container = database.get_container_client(SCORES_CONTAINER_ID)

        # Criar um documento para armazenar os resultados do quiz
        quiz_result = {
            'id': str(datetime.utcnow().timestamp()),  # Usar o timestamp atual como ID
            'username': username,
            'category': category,
            'score': score,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Salvar o documento no container do Cosmos DB
        container.create_item(body=quiz_result)

        return func.HttpResponse(
            json.dumps({"message": "Quiz finalized successfully"}),
            status_code=200,
            mimetype="application/json"
        )
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error saving quiz result: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=e.status_code,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error finalizing quiz: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
