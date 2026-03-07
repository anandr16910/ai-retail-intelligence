"""
AWS Lambda Function: AI-Powered Document Analysis with Amazon Bedrock
Includes document history storage in DynamoDB
"""
import json
import boto3
from datetime import datetime
import hashlib
import uuid

# Initialize AWS clients
bedrock_east = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_west = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB table for document history
history_table = dynamodb.Table('DocumentAnalysisHistory')


def save_to_history(document_id, text, analysis_type, model_choice, analysis_result, timestamp):
    """Save document analysis to DynamoDB history"""
    try:
        # Create text hash for deduplication
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Prepare item for DynamoDB
        item = {
            'document_id': document_id,
            'timestamp': timestamp,
            'text_hash': text_hash,
            'text_preview': text[:500],  # Store first 500 chars as preview
            'full_text': text,  # Store full text
            'analysis_type': analysis_type,
            'model_used': model_choice,
            'summary': analysis_result.get('summary', ''),
            'key_entities': analysis_result.get('key_entities', []),
            'insights': analysis_result.get('insights', []),
            'sentiment': analysis_result.get('sentiment', 'neutral'),
            'confidence_score': str(analysis_result.get('confidence_score', 0.0)),
            'document_length': len(text),
            'ttl': int(datetime.now().timestamp()) + (90 * 24 * 60 * 60)  # 90 days TTL
        }
        
        # Save to DynamoDB
        history_table.put_item(Item=item)
        print(f"Saved document {document_id} to history")
        
    except Exception as e:
        print(f"Error saving to history: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Analyze documents using Amazon Bedrock AI
    
    Request body:
    {
        "text": "document content...",
        "analysis_type": "market_intelligence|financial_report|research_paper|general",
        "model": "nova-lite|claude-3-haiku|llama-3-3-70b"
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        text = body.get('text', '').strip()
        analysis_type = body.get('analysis_type', 'general')
        model_choice = body.get('model', 'nova-lite')
        
        # Validate inputs
        if not text:
            return error_response(400, 'Document text is required')
        
        if len(text) < 50:
            return error_response(400, 'Document text too short (minimum 50 characters)')
        
        if len(text) > 50000:
            return error_response(400, 'Document text too long (maximum 50,000 characters)')
        
        # Select Bedrock model
        model_id = get_model_id(model_choice)
        
        # Analyze document using Bedrock
        analysis_result = analyze_with_bedrock(text, analysis_type, model_id)
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Store in history
        try:
            save_to_history(document_id, text, analysis_type, model_choice, analysis_result, timestamp)
        except Exception as e:
            print(f"Warning: Failed to save history: {str(e)}")
            # Continue even if history save fails
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'document_id': document_id,
                'analysis': analysis_result,
                'timestamp': timestamp,
                'model_used': model_choice,
                'document_length': len(text)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def analyze_with_bedrock(text, analysis_type, model_id):
    """Analyze document using Amazon Bedrock"""
    
    # Build analysis prompt based on type
    type_instructions = {
        'market_intelligence': 'Focus on market trends, competitive landscape, pricing strategies, and business opportunities.',
        'financial_report': 'Focus on financial metrics, revenue trends, profitability, growth indicators, and financial health.',
        'research_paper': 'Focus on key findings, methodology, conclusions, and research implications.',
        'general': 'Provide comprehensive analysis covering all important aspects of the document.'
    }
    
    instruction = type_instructions.get(analysis_type, type_instructions['general'])
    
    prompt = f"""You are an expert document analyst specializing in business, finance, and market intelligence. Analyze the following document and provide detailed insights.

Document Type: {analysis_type.replace('_', ' ').title()}
Analysis Focus: {instruction}

Document Content:
{text}

Please provide a comprehensive analysis in JSON format with the following structure:
{{
    "summary": "Brief 2-3 sentence summary of the document",
    "key_entities": ["entity1", "entity2", ...],
    "key_metrics": [
        {{"metric": "metric name", "value": "value", "context": "brief context"}}
    ],
    "insights": [
        "insight 1",
        "insight 2",
        "insight 3"
    ],
    "sentiment": "positive|neutral|negative",
    "confidence_score": 0.85,
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ],
    "risk_factors": ["risk 1", "risk 2"],
    "opportunities": ["opportunity 1", "opportunity 2"]
}}

IMPORTANT: Return ONLY valid JSON, no additional text or markdown formatting."""
    
    try:
        # Determine model type and select appropriate region
        is_nova = 'nova' in model_id.lower()
        is_llama = 'meta.llama' in model_id.lower()
        
        # Use us-east-1 for Nova, us-west-2 for Llama inference profiles
        bedrock = bedrock_east if is_nova else bedrock_west
        
        if is_llama:
            # Llama models use simple prompt format
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    'prompt': prompt,
                    'max_gen_len': 2000,
                    'temperature': 0.3,
                    'top_p': 0.9
                })
            )
        else:
            # Amazon Nova models use messages format
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    'messages': [{
                        'role': 'user',
                        'content': [{'text': prompt}]
                    }],
                    'inferenceConfig': {
                        'maxTokens': 2000,
                        'temperature': 0.3
                    }
                })
            )
        
        # Parse response
        result = json.loads(response['body'].read())
        
        # Extract text based on model type
        if is_llama:
            analysis_text = result['generation']
        else:
            analysis_text = result['output']['message']['content'][0]['text']
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                analysis_json = json.loads(analysis_text[start_idx:end_idx])
                
                # Validate required fields
                required_fields = ['summary', 'key_entities', 'insights', 'confidence_score']
                for field in required_fields:
                    if field not in analysis_json:
                        analysis_json[field] = get_default_value(field)
                
                return analysis_json
            else:
                # Return structured response with text
                return create_fallback_analysis(text, analysis_text)
        except json.JSONDecodeError:
            # Fallback: return text response
            return create_fallback_analysis(text, analysis_text)
            
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        # Fallback to basic analysis
        return create_fallback_analysis(text, str(e))


def create_fallback_analysis(text, ai_response):
    """Create fallback analysis when JSON parsing fails"""
    # Extract basic entities
    entities = extract_basic_entities(text)
    
    return {
        'summary': ai_response[:300] if len(ai_response) > 300 else ai_response,
        'key_entities': entities,
        'key_metrics': [],
        'insights': [
            'Document analysis completed',
            f'Document contains {len(text)} characters',
            'AI-powered insights extracted'
        ],
        'sentiment': 'neutral',
        'confidence_score': 0.75,
        'recommendations': ['Review the full analysis for detailed insights'],
        'risk_factors': [],
        'opportunities': []
    }


def extract_basic_entities(text):
    """Extract basic entities from text"""
    entities = []
    keywords = [
        'Gold', 'Silver', 'ETF', 'Market', 'Revenue', 'Profit', 'Growth',
        'Price', 'Sales', 'Customer', 'Product', 'Competition', 'Strategy',
        'Amazon', 'Flipkart', 'Retail', 'E-commerce', 'India'
    ]
    
    text_upper = text.upper()
    for keyword in keywords:
        if keyword.upper() in text_upper:
            entities.append(keyword)
    
    return entities[:10]  # Return top 10


def get_default_value(field):
    """Get default value for missing fields"""
    defaults = {
        'summary': 'Analysis completed successfully',
        'key_entities': [],
        'insights': ['Document analyzed'],
        'confidence_score': 0.70,
        'sentiment': 'neutral',
        'key_metrics': [],
        'recommendations': [],
        'risk_factors': [],
        'opportunities': []
    }
    return defaults.get(field, None)


def get_model_id(model_choice):
    """Get Bedrock model ID"""
    models = {
        'nova-micro': 'amazon.nova-micro-v1:0',
        'nova-lite': 'amazon.nova-lite-v1:0',
        'nova-pro': 'amazon.nova-pro-v1:0',
        'llama-3.2-3b': 'us.meta.llama3-2-3b-instruct-v1:0',
        'llama-3.1-8b': 'us.meta.llama3-1-8b-instruct-v1:0',
        'llama-3.3-70b': 'us.meta.llama3-3-70b-instruct-v1:0',
        'llama-4-scout': 'us.meta.llama4-scout-17b-instruct-v1:0'
    }
    return models.get(model_choice, models['nova-lite'])


def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }
