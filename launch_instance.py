# install requirements
print("Installing requirements ...")
os.system('sudo apt-get install python-pyaudio python3-pyaudio; pip3 install -r requirements.txt')

import time
import speech_recognition as sr
import boto3
import os


def create_aws_instance(resource_name='ec2', img_id='ami-0520e698dd500b1d1', instance_type='t2.micro'):
    client = boto3.resource(resource_name)
    response = client.create_instances(
        ImageId=img_id,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1
    )
    for item in response:
        os.system('say "Instance launched successfully"')
        print("\nInstance Launched with ID : {item_id}".format(item_id=item.id))


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        os.system('say "Say your Command"')
        print("\nSay your Command : ")
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        os.system('say "Processing your Command"')
        print("\nProcessing ...")
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":

    # set the dict of AMIs and prompt limit
    AMIS = {
        'AMAZON' : 'ami-0998bf58313ab53da',
        'REDHAT' : 'ami-0520e698dd500b1d1',
        'WINDOWS' : 'ami-07f3715a1f6dbb6d9',
        'UBUNTU' : 'ami-0fc20dd1da406780b'
    }
    INSTANCE_TYPES = ['t1.micro', 't2.nano', 't2.micro', 't2.small', 't2.medium']
    PROMPT_LIMIT = 5

    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # format the instructions string
    instructions = (
        "\nINSTRUCTIONS =>\n\n"
        "Ask for creating AWS instance with following AMI options:\n"
        "\n{amis}\n"
        # "\nInstance Types -\n{instance_types}\n"
        "\nDon't forget to include keywords 'launch' and 'instance'."
    ).format(amis='\n'.join(AMIS.keys()))#, instance_types='\n\t'.join(INSTANCE_TYPES))

    # show instructions and wait 5 seconds before starting the game
    print(instructions)
    os.system('say "Please go through the instructions"')
    time.sleep(5)

    flag = 1
    while flag:
        for i in range(PROMPT_LIMIT):
            command = recognize_speech_from_mic(recognizer, microphone)
            if command["transcription"]:
                break
            if not command["success"]:
                break
            os.system('say "I did not catch that. What did you say"')
            print("I didn't catch that. What did you say?\n")

        # if there was an error, quit
        if command["error"]:
            print("ERROR: {}".format(command["error"]))
            exit(0)

        command_words = list(map(lambda x: x.lower(), command['transcription'].split()))

        if 'launch' in command_words and 'instance' in command_words:
            for ami in AMIS.keys():
                if ami.lower() in command_words:
                    img_id = AMIS[ami]
                    break
            try:
                create_aws_instance(img_id=img_id)
            except:
                create_aws_instance()
            flag = 0
        else:
            os.system('say "Sorry! I did not understand that. Try Again"')
            print("\nSorry! I didn't understand that. Try Again ...")