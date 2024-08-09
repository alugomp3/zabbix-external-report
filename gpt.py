from openai import OpenAI
import os


def requestOpenAI(papel=None,solicita=None):
  os.environ['OPENAI_API_KEY'] = ''
  client = OpenAI()
  
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": papel },
      {"role": "user", "content": solicita }
  ]
  )
  return completion.choices[0].message
