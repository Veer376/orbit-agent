from google import genai
from PIL import Image


browser_tool_function = {
    "name": "browser_tool",
    "description": "You a browser automation agent. Your goal is to complete tasks using browser. You can use websites, interact with elements, and perform actions. for example: you can book tickets, fetch arcticles from websites, and so on.",
    "parameters":{
        "type":"object",
        "properties":{
            "user_goal":{
                "type": "string",
                "description": "details of the user goal. e.g. book a flight from delhi to bangalore on 25th of this month.",
            },
        },
        "required": ["user_goal"]
    }
}

browser_tool = genai.types.Tool(function_declarations=[browser_tool_function])

click_tool_declaration = {
    "name": "click",
    "description": "click the button or textfield on the page",
    "parameters":{
        "type":"object",
        "properties":{
            "label": {
                "type": "string",
                "description": "label of the element to click"
            },
            "points" : {
                "type": "object",
                "description": "correct coordinates to click on the label",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "x coordinate of the element to click"
                    },
                    "y": {
                        "type": "integer",
                        "description": "y coordinate of the field to click"
                    },
                },
                "required": ["x", "y"]
            }
        },
        "required": ["label", "points"]
    }
}
type_tool_declaration = {
    "name": "type",
    "description": "type text in a field on the browser page",
    "parameters":{
        "type":"object",
        "properties":{
            "label": {
                "type": "string",
                "description": "label of the field to type in"
            },
            "text": {
                "type": "string",
                "description": "text to type in the field"
            },
        },
        "required": ["label", "text"]
    }
}      
keypress_tool_declaration = {
    "name": "keypress",
    "description": "press to key on the keyboard, to nativate the page",
    "parameters":{
        "type":"object",
        "properties":{
            "keys": {
                "type": "object",
                "description": "key to press on the keyboard",
                "properties": {
                    "enter" : {
                        "type": "string",
                        "description": "press the enter key"
                    }
                }
            },
        },
        "required": ["keys"]
    }
}
scroll_tool_declaration = {
    "name": "scroll",
    "description": "scroll the page",
    "parameters":{
        "type":"object",
        "properties":{
            "x": {
                "type": "integer",
                "description": "x coordinate to scroll to"
            },
            "y": {
                "type": "integer",
                "description": "y coordinate to scroll to"
            },
        },
        "required": ["x", "y"]
    }
}


type_tool = genai.types.Tool(function_declarations=[type_tool_declaration])
click_tool = genai.types.Tool(function_declarations=[click_tool_declaration])
keypress_tool = genai.types.Tool(function_declarations=[keypress_tool_declaration])
scroll_tool = genai.types.Tool(function_declarations=[scroll_tool_declaration])