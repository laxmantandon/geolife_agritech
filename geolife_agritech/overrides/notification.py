import frappe
from frappe import _
from frappe.email.doctype.notification.notification import Notification, get_context, json

class SendNotification(Notification):

    
    def appe_send_push_notification(self, doc, notification, receivers):
        # try:
        frappe.log_error("send_push_notification receivers",receivers)
        #     url = frappe.db.get_single_value("CRM Mobile Push Notification Setting", "fcm_url")
        #     server_key = frappe.db.get_single_value("CRM Mobile Push Notification Setting", "server_key")
        #     headers = {
        #         'Authorization': 'key=' + server_key,
        #         'Content-Type': 'application/json'
        #     }
        #     for receiver in receivers:
        #         if receiver:
        #             payload = {
        #                 "to": receiver,
        #                 "notification": {
        #                     "title": notification.push_notification_title,
        #                     "body": notification.push_notification_message
        #                 },
        #                 "data": {
        #                     "document_type": doc.doctype,
        #                     "document_name": doc.name
        #                 }
        #             }
        #             response = make_post_request(
        #                 url, headers=headers, data=json.dumps(payload))
        #             frappe.log_error("send_push_notification",response)
        #     frappe.msgprint("Push Notification Sent")

        # except Exception as e:
        #     frappe.log_error(frappe.get_traceback(), "Error in send_push_notification")

        # try:
        #     # Create new document
        #     notification_doc = frappe.new_doc("Mobile App Notification")
        #     notification_doc.title = doc.get("title") or "New Notification"
        #     notification_doc.message = self.get("message") or ""
            
        #     # Optional JSON data
        #     notification_doc.data = json.dumps({
        #         "document_type": doc.doctype,
        #         "document_name": doc.name
        #     })

        #     # Add users in child table
        #     for user in receivers:
        #         if user:
        #             notification_doc.append("users", {
        #                 "user": frappe.db.get_value("User", {"mobile_no": user}, "name"),
        #                 "mobile_no": user
        #             })

        #     notification_doc.insert(ignore_permissions=True)
        #     notification_doc.submit()

        #     frappe.msgprint("Mobile App Notification Created Successfully")

        # except Exception as e:
        #     frappe.log_error("Error in create_mobile_app_notification",e)
    # def validate(self):
    #     self.validate_CRM_whatsapp_settings()

    # def validate_CRM_whatsapp_settings(self):
    #     if self.enabled and self.channel == "WhatsApp" \
    #         and not frappe.db.get_single_value("CRM Whatsapp Setting", "url"):
    #         frappe.throw(_("Please enable Whatsapp settings to send WhatsApp messages"))

    def send(self, doc):
        context = get_context(doc)
        context = {"doc": doc, "alert": self, "comments": None}
        if doc.get("_comments"):
            context["comments"] = json.loads(doc.get("_comments"))

        if self.is_standard:
            self.load_standard_properties(context)

        try:
            # if self.channel == 'WhatsApp':
            #     receivers = self.get_receiver_list(doc, context)
            #     frappe.log_error('Notification Doc',str(context))
            #     send_whatsapp_msg(doc, self, receivers)

            if self.channel == 'Mobile Push Notification':
                receivers = self.get_receiver_list(doc, context)
                frappe.log_error('Notification Doc',str(context))
                frappe.log_error("Push notification receiver", receivers)
                # self.appe_send_push_notification(doc, , receivers)

                try:
                    notification_doc = frappe.new_doc("Mobile App Notification")
                    notification_doc.title = doc.get("title") or "New Notification"
                    notification_doc.message = self.get("message") or ""
                    notification_doc.data = json.dumps({
                        "document_type": doc.doctype,
                        "document_name": doc.name
                    })
                    for user in receivers:
                        if user:
                            notification_doc.append("users", {
                                "user": frappe.db.get_value("User", {"mobile_no": user}, "name"),
                                "mobile_no": user
                            })
                        else:
                            frappe.log_error("Push notification receiver not found", user)



                    notification_doc.insert(ignore_permissions=True)
                    notification_doc.save()
                    frappe.msgprint("Mobile App Notification Created Successfully")

                except Exception as e:
                    frappe.log_error("Error in create_mobile_app_notification",e)
                
    

        except Exception as e:
            frappe.log_error('Failed to send notification', e)

        super(SendNotification, self).send(doc)