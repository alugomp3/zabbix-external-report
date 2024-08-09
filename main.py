import zabapi
from gpt import requestOpenAI
from report import populateAvailabilityDocx, getRelatorio

print(getRelatorio(days=1))
