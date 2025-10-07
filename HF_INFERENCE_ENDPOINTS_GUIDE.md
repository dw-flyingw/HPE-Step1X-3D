# HuggingFace Inference Endpoints Setup Guide

## Step-by-Step Setup

### 1. Create HuggingFace Account (if needed)

1. Go to https://huggingface.co/join
2. Sign up with email
3. Verify your email

### 2. Get Your Access Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it: "Step1X-3D-Inference"
4. Type: "Write" (needed for inference endpoints)
5. Click "Generate"
6. **Copy and save the token** (you'll need it)

### 3. Create an Inference Endpoint

1. Go to https://ui.endpoints.huggingface.co/
2. Click "New Endpoint"
3. Configure:
   - **Model Repository**: `stepfun-ai/Step1X-3D`
   - **Endpoint name**: `step1x3d-inference`
   - **Cloud Provider**: AWS (or your preference)
   - **Region**: us-east-1 (or closest to you)
   - **Instance Type**: GPU Medium (T4 or better)
   - **Scaling**: 
     - Min replicas: 0 (saves money when not in use)
     - Max replicas: 1 (or more if you need scaling)
   - **Security Level**: Protected (requires your token)
4. Click "Create Endpoint"
5. Wait 5-10 minutes for deployment

### 4. Get Your Endpoint URL

Once deployed, you'll see:
- **Endpoint URL**: Something like `https://xxxxx.us-east-1.aws.endpoints.huggingface.cloud`
- **Status**: Should show "Running" (green)

**Copy this URL** - you'll need it!

### 5. Configure Your Local Setup

On your remote server:

```bash
cd ~/HPE-Step1X-3D

# Create .env file with your credentials
cat > .env << EOF
HF_TOKEN=hf_your_token_here
HF_ENDPOINT_URL=https://xxxxx.us-east-1.aws.endpoints.huggingface.cloud
EOF
```

### 6. Run the Client

```bash
# Install minimal dependencies
pip install requests pillow gradio python-dotenv

# Start the web UI
python3 client/gradio_client.py
```

Access at: `http://your-server:7860`

## Pricing

**GPU Medium (T4):**
- ~$0.60/hour when running
- $0.00/hour when scaled to zero
- First 1,000 requests/month may be free (check current HF pricing)

**Tips to save money:**
- Set min replicas to 0 (scales to zero when not in use)
- Auto-shutdown after 15 minutes of inactivity
- Only scales up when you make a request

## Testing Your Endpoint

### Using curl:

```bash
curl https://YOUR_ENDPOINT_URL/predict \
  -X POST \
  -H "Authorization: Bearer YOUR_HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "image_base64_here"}'
```

### Using Python:

```python
import requests
from PIL import Image
import base64
import io

# Load image
image = Image.open("test.png")
buffered = io.BytesIO()
image.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()

# Call endpoint
response = requests.post(
    "https://YOUR_ENDPOINT_URL/predict",
    headers={"Authorization": f"Bearer YOUR_HF_TOKEN"},
    json={"inputs": img_str}
)

result = response.json()
```

## Advantages

✅ **No dependency management** - HF handles everything
✅ **Auto-scaling** - scales to zero when not in use
✅ **Fully managed** - HF handles updates, security, infrastructure
✅ **Fast deployment** - 5-10 minutes setup
✅ **API access** - standard REST API
✅ **Monitoring** - built-in logs and metrics
✅ **High availability** - HF manages uptime

## Monitoring

1. Go to https://ui.endpoints.huggingface.co/
2. Click on your endpoint
3. View:
   - Request count
   - Response time
   - Error rate
   - Cost estimate

## Scaling

**During development:**
- Min: 0, Max: 1
- Saves money, cold start is OK

**For production:**
- Min: 1, Max: 3+
- Always ready, handles traffic spikes

## Troubleshooting

### Endpoint stuck in "Building"
- Wait 10-15 minutes
- Check HF status: https://status.huggingface.co/

### 401 Unauthorized
- Check your token is correct
- Make sure token has "Write" permissions

### 503 Service Unavailable
- Endpoint is scaled to zero and starting up
- Wait 30-60 seconds, try again
- Consider increasing min replicas

### High costs
- Check you set min replicas to 0
- Verify auto-shutdown is enabled
- Monitor usage in dashboard

## Next Steps

1. ✅ Create HF account
2. ✅ Get access token
3. ✅ Deploy endpoint
4. ✅ Configure .env file
5. ✅ Run client UI
6. ✅ Test generation

See `client/` directory for ready-to-use client code!

