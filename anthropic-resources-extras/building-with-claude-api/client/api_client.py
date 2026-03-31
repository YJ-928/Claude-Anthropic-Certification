from anthropic import Anthropic
from dotenv import load_dotenv

# Load env
load_dotenv()

client = Anthropic()
model = "claude-sonnet-4.0"