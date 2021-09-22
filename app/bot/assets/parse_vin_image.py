from django.conf import settings
import xmltodict, requests, asyncio


SERVICE_URL = 'http://cloud.ocrsdk.com'
TASK_REPEAT = 5


async def parse_vin_image(image):
    data = requests.post(SERVICE_URL + '/processImage?language=english,russian&exportFormat=txt',
            auth=(settings.CLOUD_APP_ID, settings.CLOUD_PASS,),
            headers={'User-Agent': 'Nissan Telegram bot'},
            files={'vin_file': image}
        )
    print(data.text)
    if data.status_code == 200:
        xml_data = xmltodict.parse(data.text)
        task = xml_data['response']['task']
        if task['@status'] == 'Queued':
            for i in range(TASK_REPEAT):
                data = requests.get(SERVICE_URL + '/getTaskStatus?taskid=' + str(task['id']),
                        auth=(settings.CLOUD_APP_ID, settings.CLOUD_PASS,),
                        headers={'User-Agent': 'PHP Cloud OCR SDK Sample'}
                    )
                if data.status_code == 200:
                    xml_data = xmltodict.parse(data.text)
                    task = xml_data['response']['task']
                    if task['@status'] == 'Completed':
                        data = requests.get(task['resultUrl'])
                        full_text = re.sub(r'[^A-z\d]+', '', data.text)
                        print(full_text)
                await asyncio.sleep(5)
    return None
