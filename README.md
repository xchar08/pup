Hey, Miso!

A voice-controlled assistant (a Siri replica) featuring a circular widget with a Shiba Inu logo. The assistant continuously listens for the wake word "Hey Miso" and processes commands such as controlling music, translating on-screen text, and more using the Nebius AI API.
Features

    Circular Widget: Displays a Shiba Inu logo and glows when activated.
    Always Listening: Uses your microphone to listen for the wake phrase "Hey Miso."
    Command Processing: Recognizes commands like:
        "stop currently playing music"
        "start currently playing music"
        "translate text it sees on screen"
        "copy the neural network diagram on the screen"
        "create a new file and write an implementation of it in python using vscode"
    Nebius AI Integration: Unrecognized commands are forwarded to the Nebius API.

File Structure

``` hey_miso/ ├── assets/ │ └── shiba_inu.png # Shiba Inu logo image ├── main.py # Entry point ├── ui.py # UI components (PyQt5) ├── voice.py # Voice recognition and wake word detection ├── commands.py # Command processing and Nebius API integration ├── requirements.txt # Dependencies └── README.md # Project documentation ``` 
Setup & Installation

    Clone the Repository: `git clone <repository_url> cd hey_miso`

    Create and Activate a Virtual Environment: `python -m venv venv venv\Scripts\activate # On Windows`

    Install Dependencies: `bash pip install -r requirements.txt`

    Place Your Logo:
        Put your Shiba Inu logo image in the `assets/` folder and name it `shiba_inu.png`.

    API Key:
        The Nebius API key is included in `commands.py`. For production, store your API key securely.

Running the Application

Run the application with:

`python main.py`

A window with the circular widget will appear. The assistant will start listening for "Hey Miso." When it hears the wake word, the widget glows and it listens for your command.
Notes

    The voice recognition uses the Google Web Speech API, so an Internet connection is required.
    Media control commands are adapted for Windows using the `keyboard` library.
    Some features (such as OCR for on-screen text translation) are placeholders and need further integration.
    Security: Do not expose your API key in production code.

Happy coding! 

How to Set Up and Run the Project on Windows

    Create the Project Directory:
        Create a folder named hey_miso.
        Inside hey_miso, create a subfolder called assets.

    Add Your Assets:
        Place your Shiba Inu logo image in the assets folder and name it shiba_inu.png.

    Create Files:
        In the hey_miso folder, create the following files with the content provided above:
            main.py
            ui.py
            voice.py
            commands.py
            requirements.txt
            README.md

    Set Up a Virtual Environment:
        Open a Command Prompt (or PowerShell) in the hey_miso directory.
        Run the following commands: `python -m venv venv venv\Scripts\activate` (On Windows, use `venv\Scripts\activate` to activate the environment.)

    Install Dependencies:
        With the virtual environment activated, run: `pip install -r requirements.txt`

    Run the Application:
        Start the assistant by running: `python main.py`
        A window displaying the circular widget with your Shiba Inu logo should appear.
        The assistant will continuously listen for the wake word "Hey Miso." When it hears the wake word, the widget will glow and it will listen for your command.
        If a command is not recognized locally (for example, "play audio"), it will attempt to forward it to the Nebius API. If there is a DNS/network issue, check your Internet connection and verify that the domain “api.nebius.ai” is reachable.