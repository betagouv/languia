from fastapi import FastAPI, HTTPException
from typing import List, Dict
import asyncio
import time
from datetime import datetime

app = FastAPI()

# Outage is now a dictionary with time_of_outage and model_name
outages: List[Dict[str, str]] = []


@app.post("/outages/", status_code=201)
async def create_outage(model_name: str):

    outage = {
        "detection_time": datetime.now().isoformat(),
        "model_name": model_name,
    }

    # Check if the model name already exists in the outages list
    existing_outage = next((o for o in outages if o["model_name"] == model_name), None)

    if existing_outage:
        existing_outage["detection_time"] = outage["detection_time"]
    else:
        outages.append(outage)
    return outage


@app.get("/outages/")
async def get_outages():
    """
    Retrieves a list of all outages.

    Returns:
        List[Dict[str, str]]: A list of outage dictionaries.
    """
    return outages


@app.delete("/outages/{model_name}", status_code=204)
async def remove_outage(model_name: str):
    """
    Removes an outage entry by model name.

    Args:
        model_name (str): The model name to remove from outages.

    Raises:
        HTTPException: If the model is not found in outages.
    """
    for i, outage in enumerate(outages):
        if outage["model_name"] == model_name:
            del outages[i]
            return
    raise HTTPException(status_code=404, detail="Model not found in outages")


import logging
import os
import openai
from typing import Dict



async def test_model(model_name):

    # Log the outage test
    logging.info(
        f"Testing outage: {model_name} "
    )

    # Define test parameters
    test_message = "Say 'this is a test'."
    temperature = 1
    top_p = 1
    max_new_tokens = 10



    # Initialize the OpenAI client
    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(
        base_url="https://api.openai.com/v1",
        api_key=api_key,
        timeout=180,
    )

    try:
        # Send a test message to the OpenAI API
        res = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": test_message}],
            temperature=temperature,
            max_tokens=max_new_tokens,
            stream=True,
        )

        # Verify the response
        text = ""
        for chunk in res:
            if len(chunk.choices) > 0:
                text += chunk.choices[0].delta.content or ""
                break

        # Check if the response is successful
        if text:
            logging.info(f"Test successful: {model_name}")
            logging.info(f"Removing {model_name} from outage list")
            remove_outage(model_name)

            return {"success": "true", "error_message": ""}
        else:
            logging.error(f"Test failed: {model_name}")
            create_outage(model_name)
            return {"success": "false", "error_message": "No response from OpenAI API"}

    except openai.error.RateLimitError as e:
        logging.error(f"Rate limit exceeded: {model_name}")
        create_outage(model_name)
        return {"success": "false", "error_message": "Rate limit exceeded"}

    except openai.error.ServiceUnavailableError as e:
        create_outage(model_name)
        logging.error(f"Service unavailable: {model_name}")
        return {"success": "false", "error_message": "Service unavailable"}

    except Exception as e:
        logging.error(f"Unknown error: {model_name}, {str(e)}")
        return {"success": "false", "error_message": "Unknown error"}


async def scheduled_outage_tests():
    while True:
        for outage in outages:
            asyncio.create_task(test_model(outage['model_name']))
        await asyncio.sleep(600)  # Test every 10 minutes (600 seconds)
