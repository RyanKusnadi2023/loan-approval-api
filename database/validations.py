class Validation:
    def __init__(self, input: str):
        self.input = input.lower().replace(" ", "")
        
    def person_gender(self) -> bool:
        return self.input not in ['female', 'male']
    
    def person_education(self) -> bool:
        return self.input not in ['highschool', 'associate', 'bachelor', 'master', 'doctorate'] 
    
    def person_home_ownership(self) -> bool:
        return self.input not in ['rent', 'own', 'mortgage', 'other']
    
    def loan_intent(self) -> bool:
        return self.input not in ['personal', 'education', 'medical', 'venture', 'homeimprovement']