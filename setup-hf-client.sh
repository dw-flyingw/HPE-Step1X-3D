#!/bin/bash
# Setup HuggingFace Inference Endpoints Client
# No models, no CUDA, just API calls!

echo "=========================================="
echo "HuggingFace Inference Client Setup"
echo "=========================================="
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing minimal dependencies..."
pip install --upgrade pip
pip install gradio requests pillow python-dotenv

echo ""
echo "✅ Setup complete!"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Set up HuggingFace Inference Endpoint:"
echo "   - Go to https://ui.endpoints.huggingface.co/"
echo "   - Deploy stepfun-ai/Step1X-3D"
echo "   - Get your endpoint URL"
echo ""
echo "2. Create .env file:"
echo "   cat > .env << 'EOF'"
echo "   HF_TOKEN=your_token_here"
echo "   HF_ENDPOINT_URL=your_endpoint_url_here"
echo "   EOF"
echo ""
echo "3. Start the client:"
echo "   source venv/bin/activate"
echo "   python3 client/hf_api_client.py"
echo ""
echo "See HF_INFERENCE_ENDPOINTS_GUIDE.md for detailed instructions!"
echo ""

