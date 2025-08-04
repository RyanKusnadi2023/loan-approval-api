import random
from locust import HttpUser, task, between
import json

class LoanPredictionUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts - check if API is healthy"""
        response = self.client.get("/")
        if response.status_code != 200:
            print(f"Health check failed: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test the health check endpoint - lightweight operation"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(10)  # 10x more likely to run this task (main load)
    def predict_loan_approval(self):
        """Test the prediction endpoint with realistic data"""
        
        # Generate realistic loan application data
        loan_data = self.generate_loan_application()
        
        with self.client.post("/predict", 
                              json=loan_data,
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Validate response structure
                    if all(key in result for key in ["prediction", "confidence", "status"]):
                        response.success()
                        # Log some results for monitoring
                        if random.random() < 0.1:  # Log 10% of requests
                            print(f"Prediction: {result['status']}, Confidence: {result['confidence']:.2f}")
                    else:
                        response.failure("Invalid response structure")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 400:
                # Expected validation errors - still a successful test
                response.success()
                print(f"Validation error (expected): {response.text}")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def predict_invalid_data(self):
        """Test with invalid data to check error handling"""
        invalid_data = {
            "person_age": "not_a_number",  # Invalid age
            "loan_amnt": -1000,           # Negative loan amount
            "person_income": -500,        # Negative income
            "credit_score": "invalid",    # Invalid credit score
        }
        
        with self.client.post("/predict", 
                              json=invalid_data,
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            
            if response.status_code == 400:
                response.success()  # Expected validation error
            else:
                response.failure(f"Expected 400, got {response.status_code}")
    
    @task(1)
    def predict_edge_cases(self):
        """Test edge cases with extreme values"""
        edge_case_data = self.generate_edge_case_application()
        
        with self.client.post("/predict", 
                              json=edge_case_data,
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            
            if response.status_code in [200, 400]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    def generate_loan_application(self):
        """Generate realistic loan application data matching the new schema"""
        return {
            "person_age": random.uniform(18.0, 80.0),  # Realistic age range
            "person_gender": random.choice(["male", "female"]),
            "person_education": random.choice([
                "High School", "Associate", "Bachelor", "Master", "Doctorate"
            ]),
            "person_income": random.uniform(25000.0, 150000.0),  # Annual income range
            "person_emp_exp": random.randint(0, 40),  # Years of employment experience
            "person_home_ownership": random.choice(["RENT", "OWN", "MORTGAGE", "OTHER"]),
            "loan_amnt": random.uniform(1000.0, 100000.0),  # Loan amount
            "loan_intent": random.choice([
                "PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT"
            ]),
            "loan_int_rate": random.uniform(3.0, 25.0),  # Interest rate percentage
            "loan_percent_income": random.uniform(0.05, 0.50),  # 5% to 50% of income
            "cb_person_cred_hist_length": random.uniform(0.0, 30.0),  # Credit history length in years
            "credit_score": random.randint(300, 850),  # Standard credit score range
            "previous_loan_defaults_on_file": random.choice(["Yes", "No"])
        }
    
    def generate_edge_case_application(self):
        """Generate edge case data with extreme but valid values"""
        return {
            "person_age": random.choice([18.0, 100.0]),  # Very young or very old
            "person_gender": "male",
            "person_education": random.choice(["High School", "Doctorate"]),  # Extremes
            "person_income": random.choice([1.0, 500000.0]),  # Very low or very high income
            "person_emp_exp": random.choice([0, 50]),  # No experience or lots
            "person_home_ownership": random.choice(["RENT", "OTHER"]),
            "loan_amnt": random.choice([1.0, 200000.0]),  # Very small or very large loan
            "loan_intent": "VENTURE",
            "loan_int_rate": random.choice([0.1, 29.99]),  # Very low or very high rate
            "loan_percent_income": random.choice([0.01, 0.90]),  # Very low or very high percentage
            "cb_person_cred_hist_length": random.choice([0.0, 50.0]),  # No history or very long
            "credit_score": random.choice([300, 850]),  # Worst or best credit
            "previous_loan_defaults_on_file": random.choice(["Yes", "No"])
        }

class HighVolumeUser(HttpUser):
    """Simulate high-volume users making rapid requests"""
    wait_time = between(0.1, 0.5)  # Much faster requests
    
    @task
    def rapid_predictions(self):
        """Fixed loan data for rapid testing"""
        loan_data = {
            "person_age": 35.0,
            "person_gender": "male",
            "person_education": "Bachelor",
            "person_income": 75000.0,
            "person_emp_exp": 10,
            "person_home_ownership": "MORTGAGE",
            "loan_amnt": 25000.0,
            "loan_intent": "PERSONAL",
            "loan_int_rate": 8.5,
            "loan_percent_income": 0.25,
            "cb_person_cred_hist_length": 12.0,
            "credit_score": 720,
            "previous_loan_defaults_on_file": "No"
        }
        
        self.client.post("/predict", json=loan_data)

class DatabaseStressUser(HttpUser):
    """Focus on stressing database operations if you add them later"""
    wait_time = between(0.5, 1.5)
    
    @task
    def predict_with_logging(self):
        """Simulate requests that might involve database logging"""
        loan_data = {
            "person_age": random.uniform(25.0, 65.0),
            "person_gender": random.choice(["male", "female"]),
            "person_education": "Bachelor",
            "person_income": random.uniform(40000.0, 120000.0),
            "person_emp_exp": random.randint(2, 25),
            "person_home_ownership": random.choice(["RENT", "OWN", "MORTGAGE"]),
            "loan_amnt": random.uniform(5000.0, 50000.0),
            "loan_intent": random.choice(["PERSONAL", "HOMEIMPROVEMENT", "EDUCATION"]),
            "loan_int_rate": random.uniform(5.0, 15.0),
            "loan_percent_income": random.uniform(0.10, 0.40),
            "cb_person_cred_hist_length": random.uniform(2.0, 20.0),
            "credit_score": random.randint(500, 800),
            "previous_loan_defaults_on_file": "No"
        }
        
        self.client.post("/predict", json=loan_data)

class ValidationTestUser(HttpUser):
    """Specifically test various validation scenarios"""
    wait_time = between(1, 2)
    
    @task(1)
    def test_missing_required_fields(self):
        """Test with missing required fields"""
        incomplete_data = {
            "person_age": 30.0,
            "person_gender": "male",
            # Missing other required fields
        }
        
        with self.client.post("/predict", 
                            json=incomplete_data,
                            headers={"Content-Type": "application/json"},
                            catch_response=True) as response:
            
            if response.status_code == 400:
                response.success()  # Expected validation error
            else:
                response.failure(f"Expected 400 for missing fields, got {response.status_code}")

    @task(1)
    def test_invalid_literals(self):
        """Test with invalid literal values"""
        invalid_literals_data = {
            "person_age": 30.0,
            "person_gender": "unknown",  # Invalid gender
            "person_education": "PhD",   # Invalid education level
            "person_income": 50000.0,
            "person_emp_exp": 5,
            "person_home_ownership": "RENTING",  # Invalid home ownership
            "loan_amnt": 10000.0,
            "loan_intent": "TRAVEL",  # Invalid intent
            "loan_int_rate": 7.5,
            "loan_percent_income": 0.20,
            "cb_person_cred_hist_length": 8.0,
            "credit_score": 650,
            "previous_loan_defaults_on_file": "Maybe"  # Invalid value
        }
        
        with self.client.post("/predict", 
                              json=invalid_literals_data,
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            
            if response.status_code == 400:
                response.success()  # Expected validation error
            else:
                response.failure(f"Expected 400 for invalid literals, got {response.status_code}")
    
    @task(1)
    def test_boundary_violations(self):
        """Test with values that violate field constraints"""
        boundary_violation_data = {
            "person_age": -5.0,  # Violates gt=0
            "person_gender": "female",
            "person_education": "Bachelor",
            "person_income": -1000.0,  # Violates ge=0
            "person_emp_exp": -2,  # Violates ge=0
            "person_home_ownership": "OWN",
            "loan_amnt": -5000.0,  # Violates gt=0
            "loan_intent": "PERSONAL",
            "loan_int_rate": -2.0,  # Violates ge=0
            "loan_percent_income": -0.1,  # Violates ge=0
            "cb_person_cred_hist_length": -1.0,  # Violates ge=0
            "credit_score": -100,  # Violates ge=0
            "previous_loan_defaults_on_file": "No"
        }
        
        with self.client.post("/predict", 
                              json=boundary_violation_data,
                              headers={"Content-Type": "application/json"},
                              catch_response=True) as response:
            if response.status_code == 400:
                response.success()  # Expected validation error
            else:
                response.failure(f"Expected 400 for boundary violations, got {response.status_code}")