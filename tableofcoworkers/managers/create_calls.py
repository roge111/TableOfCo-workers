from random import random, randint
from datetime import datetime, timedelta, timezone
import django.utils as du
import random

class CreateCalls:
    def __init__(self):
        pass

    def _generate_number(self):
        return '+79' + ''.join([str(randint(0, 9)) for _ in range(9)])
    
    

    def generate_random_iso_with_timezone(self):
    # Создаем временную зону +03:00

        tz = timezone(timedelta(hours=3))
        now = datetime.now(tz)

        # Генерируем случайное количество секунд в пределах 24 часов
        random_seconds = random.randint(0, 24 * 60 * 60)
        random_time = now - timedelta(seconds=random_seconds)

        return random_time.isoformat()

    
    
    

    def register_call(self, token, users):
        user_id = users[int(random.random() * len(users))]
        random_date = self.generate_random_iso_with_timezone()
        number = self._generate_number()
        print(number, user_id)
        
        create = token.call_list_method('telephony.externalcall.register', {
            
            'USER_ID': user_id,
            'PHONE_NUMBER': number,
            'CALL_START_DATE': random_date,
            'TYPE': 1
        })
        print(create)

        return user_id, create
    

    def stop_call(self, token, user_id, call_id, delta):
        print('delta =', delta)
        stop = token.call_list_method('telephony.externalcall.finish', {
            'CALL_ID': call_id,
            'USER_ID': user_id,
            'DURATION': delta,
            'STATUS_CODE': '200'
        })

        print(stop)
        