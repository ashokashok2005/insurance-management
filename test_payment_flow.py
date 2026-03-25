import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import Agent, Customer, Policy, Payment
from flask_jwt_extended import create_access_token
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class PaymentTestCase(unittest.TestCase):
    def setUp(self):
        test_config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'JWT_SECRET_KEY': 'test_secret'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test data
            self.agent = Agent(email='test@agent.com', name='Test Agent')
            self.agent.set_password('password')
            db.session.add(self.agent)
            db.session.commit()
            
            self.agent_id = self.agent.id
            
            self.customer = Customer(
                agent_id=self.agent.id,
                name='Test Customer',
                mobile='1234567890'
            )
            db.session.add(self.customer)
            db.session.commit()
            
            self.policy = Policy(
                customer_id=self.customer.id,
                policy_number='POL123',
                type='Health',
                insurer='Test Insurer',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                premium=1000.0,
                frequency='Yearly'
            )
            db.session.add(self.policy)
            db.session.commit()
            self.policy_id = self.policy.id
            
            self.token = create_access_token(identity=str(self.agent.id))
            self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('app.routes.payments.stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_create):
        # Mock Stripe response
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_stripe_create.return_value = mock_session
        
        response = self.client.post(f'/payments/create-checkout-session/{self.policy_id}', headers=self.headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['url'], 'https://checkout.stripe.com/test')
        
        # Verify valid call to stripe
        mock_stripe_create.assert_called_once()
        args, kwargs = mock_stripe_create.call_args
        self.assertEqual(kwargs['mode'], 'payment')
        self.assertEqual(kwargs['metadata']['policy_id'], self.policy_id)

    @patch('app.routes.payments.stripe.checkout.Session.retrieve')
    def test_payment_success(self, mock_retrieve):
        # Mock Stripe Session Retrieve
        mock_session = MagicMock()
        mock_session.metadata = {'policy_id': self.policy_id}
        mock_session.payment_status = 'paid'
        mock_session.amount_total = 100000 # 1000.00 * 100
        mock_session.currency = 'inr'
        mock_session.id = 'cs_test_123'
        
        mock_retrieve.return_value = mock_session
        
        # Call success endpoint
        response = self.client.get('/payments/success?session_id=cs_test_123')
        
        self.assertEqual(response.status_code, 200)
        # Check if record created
        with self.app.app_context():
            payment = Payment.query.filter_by(stripe_payment_id='cs_test_123').first()
            self.assertIsNotNone(payment)
            self.assertEqual(payment.status, 'completed')
            self.assertEqual(payment.amount, 1000.0)
            
            # Verify Policy Update
            updated_policy = Policy.query.get(self.policy_id)
            self.assertEqual(updated_policy.status, 'Active')
            # End date should be extended by 1 year (frequency=Yearly)
            # Original end_date was today + 365. 
            # Logic: max(today, end_date) + 1 year.
            # since end_date > today, it should be end_date + 1 year
            expected_end = self.policy.end_date + relativedelta(years=1)
            self.assertEqual(updated_policy.end_date, expected_end)

if __name__ == '__main__':
    unittest.main()
