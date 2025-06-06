import datetime
import frappe
from frappe.utils import now, add_to_date, get_datetime
from frappe.integrations.utils import make_get_request
from datetime import datetime ,time



@frappe.whitelist()
def get_biometric_data():
    try:
        from_date = frappe.utils.today()
        to_date = frappe.utils.today()
        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = to_date_obj.strftime('%d%m%Y')
        from_date = from_date_obj.strftime('%d%m%Y')
        mindex = frappe.db.get_value("Biometric Attendance Log", filters={'device_location':'HO Mumbai'}, fieldname="max(indexno)") or 0
        response = make_get_request(f"http://27.107.150.174/COSEC/api.svc/v2/template-data?action=get;id=3;date-range={from_date}-{to_date};format=json;index={int(mindex)+1}", auth=("sa", "omhs2012"))
        # frappe.log_error("get_biometric_data backend", response)
        if response['template-data']:
            for b in response['template-data']:
                try:
                    date_str = b.get('eventdatetime')
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
                    eventdatetime = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    mdoc = frappe.get_doc({
                        'doctype':'Biometric Attendance Log',
                        'employee': b.get('userid'),
                        'geo_mitra': (frappe.db.exists('Geo Mitra', {'dgo_code':b.get('userid')}) or '') if b.get('userid') else '',
                        'employee_name': b.get('username'),
                        'indexno': b.get('indexno'),
                        'eventdatetime': eventdatetime,
                        'device_location':'HO Mumbai'
                        }).insert()
                    if frappe.db.exists('Geo Mitra', {'dgo_code':b.get('userid')}):
                        geo_mitra = frappe.get_doc("Geo Mitra", {'dgo_code':b.get('userid')})

                        now = datetime.now()
                        three_thirty = time(3, 30)
                        if now.time() > three_thirty:
                            d_list = frappe.db.get_list('Daily Activity',filters=[["Daily Activity","geo_mitra","=",geo_mitra.get('name')],["Daily Activity","creation",">",frappe.utils.today()],["Activity Type Multiselect","activity_type","=","Start Day"]], fields=["name"])
                            if not d_list:
                                activity =frappe.get_doc({
                                    'doctype':'Daily Activity',
                                    'geo_mitra':geo_mitra.get('name'),
                                    'session_started':eventdatetime,
                                    "posting_date": frappe.utils.nowdate(),
                                    "activity_type":"Start Day",
                                    "custom_biometric_log":mdoc.get('name'),
                                    "multi_activity_types":[{
                                        "posting_date": frappe.utils.nowdate(),
                                        "activity_type":"Start Day"
                                    }]
                                }).insert()
                except Exception as err:
                    frappe.log_error("get_biometric_data error for log", err)
                    
                frappe.db.commit()


        frappe.response.message={
                'status':True,
                'message':f"Data Inserted"
        }
    except Exception as e:
        frappe.log_error("get_biometric_data error", e)
        frappe.response.message={
            'status':False,
            'message':f"{e}"
        }