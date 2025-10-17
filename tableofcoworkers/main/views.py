from django.shortcuts import render

from datetime import timedelta
from django.utils import timezone
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from managers.create_calls import CreateCalls


cc = CreateCalls()
# Create your views here.
@main_auth(on_start=True, set_cookie=True)
def index(request):
    
    return render(request, 'main/index.html', locals())


@main_auth(on_cookies=True)
def table(request):
    but = request.bitrix_user_token
    users = but.call_list_method('user.get', {
        'sort': 'ID',
        'order': 'ASC'
    })
    dep = but.call_list_method('department.get', {
        'sort': 'ID',
        'order': 'ASC'
    })
    
    # Подготавливаем данные для передачи в шаблон
    users_data = []
    
    for user in users:
        
        user_id = user.get('ID')
        user_firstname = user.get('NAME')
        user_lastname = user.get('LAST_NAME')  # Исправлено: LAST_NAME вместо LASTNAME
        
        # Получаем звонки
        calls = but.call_list_method('voximplant.statistic.get', {
            "FILTER": {
                'CALL_TYPE': '1',
                '>CALL_DURATION': 60,
                '>CALL_START_DATE': (timezone.now() - timedelta(hours=24)).isoformat(),
                '=PORTAL_USER_ID': str(user_id)
            }
        })
        call_count = len(calls) if calls else 0
        
        # Находим руководителей согласно вашему синтаксису
        supervisors = []
        departments = user.get('UF_DEPARTMENT', [])
        
        for department_id in departments:
            for department in dep:
                if int(department.get('ID')) == int(department_id):
                    supervisor_id = department.get('UF_HEAD')
                    print(supervisor_id)
                    if supervisor_id:
                        # Ваш синтаксис согласно документации
                        supervisor_data = but.call_list_method('user.get', {
                            'filter': {"=ID": supervisor_id}
                        })
                        if supervisor_data:
                            
                            supervisor = supervisor_data[0]
                            supervisor_name = f"{supervisor.get('NAME')} {supervisor.get('LAST_NAME')}".strip()
                            if supervisor_name and supervisor_name not in supervisors:
                                supervisors.append(supervisor_name)
        
        # Добавляем данные пользователя
        users_data.append({
            'id':user_id,
            'first_name': user_firstname,
            'last_name': user_lastname,
            'call_count': call_count,
            'supervisors': supervisors
        })
        
    return render(request, 'main/table.html', {'users_data': users_data})
    


@main_auth(on_cookies=True)
def create_call(request):
    token = request.bitrix_user_token
    
    # Получаем delta из GET параметров (только когда форма отправлена)
    delta = request.GET.get('delta')
    if delta:
        try:
            delta = int(delta)
        except (ValueError, TypeError):
            delta = 3600
        
        users = token.call_list_method('user.get', {
            'sort': 'ID',
            'order': 'ASC'
        })
        users_id = [user.get('ID') for user in users]
        
        user_id, call_info = cc.register_call(token, users_id)
        print(user_id, call_info)
        
        cc.stop_call(token, user_id, call_info.get('CALL_ID'), delta)
    
    # Всегда возвращаем шаблон с формой
    return render(request, 'main/create_call.html', locals())

