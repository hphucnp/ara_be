import email
import smtplib
from datetime import datetime

from fastapi import FastAPI, UploadFile
import time
import hashlib
import requests
import json
import yagmail

app = FastAPI()


@app.post("/api/v1/audio")
def get_audio(audio: UploadFile, question_prompt: str):
    resp = {}
    try:
        contents = audio.file.read()
        audio_file = open(audio.filename, 'wb')
        audio_file.write(contents)
        audio_file.close()


        appKey = "168411953800015d"
        secretKey = "bb187f84e5ff8681d9e572e9147f36cf"

        baseURL = "https://api.speechsuper.com/"

        timestamp = str(int(time.time()))

        coreType = "speak.eval.pro"  # Change the coreType according to your needs.
        test_type = "ielts"  # Change the test_type according to your needs.
        task_type = "ielts_part1"  # Change the task_type according to your needs.
        audioType = "mp3"  # Change the audio type corresponding to the audio file.
        # question_prompt="What did ben do yesterday?" # Change the question_prompt according to your needs.
        audioSampleRate = 16000
        userId = "guest"

        url = baseURL + coreType
        connectStr = (appKey + timestamp + secretKey).encode("utf-8")
        connectSig = hashlib.sha1(connectStr).hexdigest()
        startStr = (appKey + timestamp + userId + secretKey).encode("utf-8")
        startSig = hashlib.sha1(startStr).hexdigest()

        params = {
            "connect": {
                "cmd": "connect",
                "param": {
                    "sdk": {
                        "version": 16777472,
                        "source": 9,
                        "protocol": 2
                    },
                    "app": {
                        "applicationId": appKey,
                        "sig": connectSig,
                        "timestamp": timestamp
                    }
                }
            },
            "start": {
                "cmd": "start",
                "param": {
                    "app": {
                        "userId": userId,
                        "applicationId": appKey,
                        "timestamp": timestamp,
                        "sig": startSig
                    },
                    "audio": {
                        "audioType": audioType,
                        "channel": 1,
                        "sampleBytes": 2,
                        "sampleRate": audioSampleRate
                    },
                    "request": {
                        "coreType": coreType,
                        "tokenId": "tokenId",
                        "test_type": test_type,
                        "task_type": task_type,
                        "question_prompt":question_prompt

                    }

                }
            }
        }

        datas = json.dumps(params)
        data = {'text': datas}
        headers = {"Request-Index": "0"}
        files = {"audio": open(audio.filename, 'rb')}
        resp_json = requests.post(url, data=data, headers=headers, files=files).json()
        print("Fuck")
        resp["overall"] = resp_json["result"]["overall"]
        resp["fluency_coherence"] = resp_json["result"]["fluency_coherence"]
        resp["lexical_resource"] = resp_json["result"]["lexical_resource"]
        resp["grammar"] = resp_json["result"]["grammar"]
        resp["pronunciation"] = resp_json["result"]["pronunciation"]
        overall = resp["overall"]
        print("yeahyeah")
        level = 'FAILED'
        if overall > 7:
            level = 'ADVANCED'
        elif overall > 5:
            level = 'INTERMEDIATE'
        elif overall > 4:
            level = 'BASIC'

        resp["level"] = level

        try:
            # yag = yagmail.SMTP('ara.awaydigital@gmail.com', oauth2_file="./client_secret.json")
            contents = (
                "Dear Recruiters,\n"
                "I hope this email finds you well.\n"
                f"At {datetime.now().strftime('%M:%H %d/%m/%Y')}, your candidate has done the English Competency "
                f"Test. Hence, I am writing to inform you that the English proficiency score has been received. Their "
                f"score is {resp['overall']}, which is considered to be {resp['level']}.\n"
                "Thank you for your time and consideration.\n"
                "Sincerely, \n"
                "ARA"
            ).encode('utf-8').strip()
            # yag.send('thong.dinh@awaydigitalteams.com', 'subject', contents)
            receivers = ['ara.awaydigital@gmail.com']
            sender = 'ara.away@hotmail.com'

            # message = email.(contents)

            try:
                smtp_obj = smtplib.SMTP('localhost:25')
                smtp_obj.sendmail(sender, receivers, contents)
                print("Successfully sent email")
            except smtplib.SMTPException:
                print("Error: unable to send email")
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        return {"message": "There was an error uploading the file"}
    finally:
        audio.file.close()
    return resp
