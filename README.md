# gpt-cli

A commandline interface for using openai's models. 

## authentication
You have to use your own api key, uses environment variable $OPENAI_API_KEY automatically. Otherwise you have to set it separately

```python
client = OpenAI(api_key="your-api-key")
```

