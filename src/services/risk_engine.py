import random

class ChaosEngine:
    @staticmethod
    def generate_batch(scenario, batch_id):
        new_emails = [f"user_{batch_id}_{i}_{random.randint(100,999)}@corp.com" for i in range(25)]
        
        # Lists of tuples (Raw Data)
        data_bank = []
        data_ins = []
        
        for email in new_emails:
            if "Recession" in scenario:
                inc, status, costs = random.randint(25000, 45000), 'Default', random.randint(2000, 8000)
                region = random.choice(['northeast', 'west', 'southwest'])
            elif "Health" in scenario:
                inc, status, costs = random.randint(55000, 85000), 'Fully Paid', random.randint(45000, 120000)
                region = 'southeast'
            else:
                inc, status, costs = random.randint(90000, 150000), 'Fully Paid', random.randint(500, 4000)
                region = random.choice(['west', 'northwest'])

            # Tuple: (email, loan_amnt, term, int_rate, grade, annual_inc, loan_status)
            data_bank.append((email, 50000, '60 months', 25.5, 'G', inc, status))
            
            # Tuple: (email, age, bmi, charges, smoker, region)
            data_ins.append((email, random.randint(25, 65), round(random.uniform(22, 38), 1), costs, 'yes', region))
            
        return data_bank, data_ins

class StressTester:
    @staticmethod
    def run_simulation(db_manager, user_data):
        stresses = [0.8, 1.0, 1.2, 1.4, 1.6] 
        probs = []
        for s in stresses:
            # FIX: Convert all inputs to standard Python types before sending to DB
            new_charge = float(user_data['CHARGES'] * s)
            income = int(user_data['ANNUAL_INC'])
            age = int(user_data['AGE'])
            bmi = float(user_data['BMI'])
            
            p = db_manager.predict_risk(income, age, bmi, new_charge)
            probs.append(p * 100)
        return probs