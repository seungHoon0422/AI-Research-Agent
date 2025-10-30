
GET_CURRENT_TIME = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current time in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. seoul",
                    "default": "seoul",
                },
            },
            "required": ["location"],
        },
    }
}