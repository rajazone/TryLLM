import os

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
metrics = PrometheusMetrics(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10 per minute", "30 per hour"]
)

model_path = os.environ.get('MODEL_PATH', 'KoalaAI/Text-Moderation')

# Load the model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)


@app.route('/generate', methods=['POST'])
@limiter.limit(os.environ.get('RATE_LIMIT', '10 per minute'))
def generate_text():
    # Get input text from the request
    input_text = request.json.get('input_text', '')

    # Run the model on your input
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model(**inputs)

    # Get the predicted logits
    logits = outputs.logits

    # Apply softmax to get probabilities (scores)
    probabilities = logits.softmax(dim=-1).squeeze()

    # Retrieve the labels
    id2label = model.config.id2label
    labels = [id2label[idx] for idx in range(len(probabilities))]

    # Combine labels and probabilities, then sort
    label_prob_pairs = list(zip(labels, probabilities))
    label_prob_pairs.sort(key=lambda item: item[1], reverse=True)

    labels_probs = []
    # Print the sorted results
    for label, probability in label_prob_pairs:
        label_prob = f"Label: {label} - Probability: {probability:.4f}"
        labels_probs.append(label_prob)

        # Prepare JSON response
    response = {
        'input_text': input_text,
        'generated_text': labels_probs
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('APP_PORT', 5000))
