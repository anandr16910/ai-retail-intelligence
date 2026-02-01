# AI Retail Intelligence Platform - Deployment Guide

## Quick Start Commands

### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd ai-retail-intelligence
pip install -r requirements.txt

# Run demo
python main.py --mode demo

# Start API server
python main.py --mode server
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t ai-retail-intelligence .
docker run -p 8000:8000 ai-retail-intelligence

# Or use Docker Compose
docker-compose up -d
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get forecast
curl -X POST http://localhost:8000/api/v1/forecast/gold \
  -H "Content-Type: application/json" \
  -d '{"symbol": "GOLD", "horizon": 7}'

# Get pricing recommendation
curl -X POST http://localhost:8000/api/v1/pricing/recommend \
  -H "Content-Type: application/json" \
  -d '{"symbol": "GOLD", "current_price": 1850.0}'

# Query market copilot
curl -X POST http://localhost:8000/api/v1/copilot/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current gold price?"}'
```

## AWS Deployment Options

### 1. AWS Lambda (Serverless)
- **Best for**: Low traffic, cost optimization
- **Setup**: Use AWS SAM or Serverless framework
- **Scaling**: Automatic, pay-per-request

### 2. AWS ECS (Containerized)
- **Best for**: Medium to high traffic
- **Setup**: Use provided Dockerfile
- **Scaling**: Auto-scaling groups

### 3. AWS EC2 (Virtual Machines)
- **Best for**: Full control, custom configurations
- **Setup**: Manual deployment on Ubuntu/Amazon Linux
- **Scaling**: Manual or auto-scaling groups

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Database connections secured
- [ ] Monitoring and logging enabled
- [ ] Backup strategy implemented
- [ ] Load balancing configured
- [ ] Security groups configured
- [ ] API rate limiting enabled

## Monitoring & Maintenance

### Health Checks
- API endpoint: `/health`
- System status: `python main.py --mode status`
- Docker health: `docker ps` (check health status)

### Log Monitoring
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- API access logs: Built into FastAPI

### Performance Metrics
- Response times
- Memory usage
- CPU utilization
- Request rates
- Error rates