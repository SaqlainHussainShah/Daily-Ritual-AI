# Daily Ritual AI

AI-powered food and drink recommendations based on mood, location, and weather.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export AWS_DEFAULT_REGION=us-east-1
export OPENWEATHER_API_KEY=your_key
```

3. Run:
```bash
streamlit run streamlit_app.py
```

## Deploy

### Local
```bash
streamlit run streamlit_app.py
```

### AWS Elastic Beanstalk
1. **Create EB application** using `flask_app.py` as main file
2. **Set environment variables** in EB Configuration:
   - `AWS_DEFAULT_REGION=us-east-1`
   - `OPENWEATHER_API_KEY=your_key`
3. **Configure IAM role** with these permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [{
           "Effect": "Allow",
           "Action": [
               "bedrock:InvokeModel",
               "bedrock:InvokeModelWithResponseStream"
           ],
           "Resource": "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
       }]
   }
   ```
4. **Deploy** using EB CLI or console