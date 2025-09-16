
from django.shortcuts import render, redirect
from django.contrib import messages

from contact_export.utils.exorter_module import ExporterFactory
from contact_export.utils.importer_module import process_imported_file
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
# from integration_utils.bitrix24.functions.batch_api_call import _batch_api_call
from django.http import JsonResponse, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- функция отображения главной страницы ---
def common_index_view(request):

    # contacts = but.call_api_method('crm.contact.get', {'ID': 3})

    # если запрос GET, просто рендерим страницу
    return render(request, 'index.html')

@main_auth(on_start=True, set_cookie=True)
def start_index(request):
    return common_index_view(request)

@main_auth(on_cookies=True)
def index_after(request):
    return common_index_view(request)

# --- экспорт контактов в xcel или csv
@main_auth(on_cookies=True)
def export_contacts(request):
    if request.method == 'POST':
        but = request.bitrix_user_token
        try:
            # --- подготовка данныхк контактов для экспорта
            contact_ids = [contact['ID'] for contact in but.call_list_method('crm.contact.list', {'SELECT': ['ID']})]

            methods = []
            for contact_id in contact_ids:
                methods.append((
                    f'contact_{contact_id}',
                    'crm.contact.get',  # Этот метод ВСЕГДА возвращает все поля
                    {'ID': contact_id}  # SELECT здесь не работает!
                ))
            contacts = but.batch_api_call(methods=methods, halt=0, chunk_size=50)

            # получаем структурированный словарь с названиями компаний
            company_dict = {company['ID']: company['TITLE'] for company in but.call_list_method("crm.company.list", {
                "select": ["ID", "TITLE"]
            })}
            print(f'получили словарь с id + название компании: {contact_ids}')
            # фильтруем только нужные поля
            filtered_contacts = []
            for contact_data in contacts.values():
                if contact_data['error'] is None:
                    contact = contact_data['result']
                    filtered_contacts.append({
                        'ID': contact.get('ID'),
                        'NAME': contact.get('NAME'),
                        'LAST_NAME': contact.get('LAST_NAME'),
                        'PHONE': contact.get('PHONE')[0].get('VALUE', '') if contact.get('PHONE') else '',
                        'EMAIL': contact.get('EMAIL')[0].get('VALUE', '') if contact.get('EMAIL') else '',
                        'COMPANY': company_dict[contact.get('COMPANY_ID')] if contact.get('COMPANY_ID') else ''
                    })

            # print(f'>>> ответ от api получен. Список ОТФИЛЬТРОВАННЫХ контактов следующий!: {filtered_contacts}')

            # --- подготовка экспортера для переноса данных
            exporter_format = request.POST.get('exporter_format')

            exporter = ExporterFactory.get_exporter(exporter_format)
            return exporter.export(filtered_contacts)

        except Exception as e:
            return HttpResponse(f'Ошибка экспорта контактов: {e}', status=500)
    # GET-запроса быть не может, возвращаем ошибку
    return HttpResponse(f'Ошибка 405: недопустимый метод {request.method}', status=405)


@main_auth(on_cookies=True)
def import_contacts(request):
    if request.method == 'POST':
        but = request.bitrix_user_token
        try:
            if 'contacts_file' not in request.FILES:
                messages.error(request, 'файл не был загружен')
                print('файл  не был загружен, перевод на главную страницу')
                return redirect('index_after')
            uploaded_file = request.FILES['contacts_file']
            contacts_to_import = process_imported_file(uploaded_file)
            if not contacts_to_import:
                msg = f'Не удалось извлечь контактов из файла или файл пуст'
                print(msg+'. Переход на главную страницу...')
                messages.error(request, msg)
                return redirect('index_after')
            result_msg = f'Сформирован список контактов из импортированного файла: {contacts_to_import}'
            print('>>' + result_msg)
            return HttpResponse(result_msg, status=200)
        except Exception as e:
            return HttpResponse( f'Ошибка при обработке файла: {str(e)}', status=500)
        return HttpResponse(f'Недопустимый метод {request.method}', status=405)