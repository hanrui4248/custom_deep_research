from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings
from pydantic import BaseModel

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and"
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300"
    "words. Capture the main points. Write succintly, no need to have complete sentences or good"
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the"
    "essence and ignore any fluff. Do not include any additional commentary other than the summary"
    "itself."
)

# class WebSearchItem(BaseModel):
#     # reason: str
#     # "Your reasoning for why this search is important to the query."
#     search_result_summary: str
#     "The summary of the search result."

#     url: str
#     "The url of the search result."


search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
    #output_type=WebSearchItem,
)
