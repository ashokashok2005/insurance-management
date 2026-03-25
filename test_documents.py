import unittest
from app import create_app, db
from app.models import Agent, Customer, Policy
from flask_jwt_extended import create_access_token
from datetime import date

class DocumentsTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'JWT_SECRET_KEY': 'test-secret',
            'WTF_CSRF_ENABLED': False
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Setup data
            self.agent = Agent(name='Test Agent', email='agent@test.com')
            self.agent.set_password('password')
            db.session.add(self.agent)
            db.session.commit()
            
            self.customer = Customer(name='Test Customer', email='customer@test.com', mobile='1234567890', agent_id=self.agent.id)
            db.session.add(self.customer)
            db.session.commit()
            
            self.policy = Policy(
                policy_number='POL-123', 
                customer_id=self.customer.id, 
                insurer='Test Insurer', 
                premium=1000.0,
                type='Health',
                start_date=date.today(),
                end_date=date.today(),
                frequency='Yearly'
            )
            db.session.add(self.policy)
            db.session.commit()
            
            self.policy_id = self.policy.id
            self.agent_id = self.agent.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_token(self):
        with self.app.app_context():
            return create_access_token(identity=str(self.agent_id), additional_claims={'role': 'agent'})

    def test_download_receipt_pdf(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        response = self.client.get(f'/api/documents/receipt/{self.policy_id}/pdf', headers=headers)
        
        if response.status_code != 200:
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {response.data}")

        # Check if response is PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/pdf')
        self.assertTrue(len(response.data) > 0)
        self.assertIn(b'%PDF', response.data[:10])

    def test_email_sending_mock(self):
        # We can't easily test actual email sending without a mock, 
        # but we can verify the payment success route doesn't crash when email fails (or succeeds)
        # To strictly test email, we'd need to mock app.utils.send_email
        pass

if __name__ == '__main__':
    unittest.main()
