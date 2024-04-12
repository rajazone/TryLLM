import threading
import time
import secrets
import unittest
import requests
import os


class TestPerformance(unittest.TestCase):
    # URL of the Flask app
    BASE_URL = 'http://localhost:5000'
    ENDPOINT = '/generate'

    # List of random inputs to test
    inputs = ["This is a good day", "San Francisco is not a safer city", "No city is safe",
              "People are prejudiced, having bias is a natural phenomenon", "To err is human",
              "Some people hate cats, they think the cats are not loyal friends"]

    # Number of iterations for performance testing
    NUM_ITERATIONS = 100
    scenario_env = {
        'perf': {
            'RATE_LIMIT': '1000 per second'
        },
        'fail': {
            'RATE_LIMIT': '50 per minute'
        }
    }

    def setUp(self):
        self.flask_thread = threading.Thread(target=self.start_app)
        self.flask_thread.daemon = True
        self.flask_thread.start()
        time.sleep(30)

    def tearDown(self):
        os.system("pkill -f 'python app.py'")

    def start_app(self):
        os.environ.update(self.scenario_env['perf'])
        from app import app
        app.run(host='localhost', port=5000)

    # Test function to measure response time for a specific endpoint
    def test_endpoint_performance(self):
        rate_limit = os.getenv('RATE_LIMIT')
        print("Rate Limit : " + rate_limit)
        start_time = time.time()
        for _ in range(self.NUM_ITERATIONS):
            data = {'input_text': secrets.choice(self.inputs)}
            response = requests.post(self.BASE_URL + self.ENDPOINT, json=data)
            assert response.status_code == 200
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_request = total_time / self.NUM_ITERATIONS
        print(f"Total time taken for {self.NUM_ITERATIONS} requests to {self.ENDPOINT}: {total_time} seconds")
        print(f"Avg. time per request: {avg_time_per_request} seconds")


if __name__ == '__main__':
    unittest.main()
