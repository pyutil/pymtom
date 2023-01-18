"""
Tip:
This uses internally the functionality from zeep.
You can use zeep directly for this purpose.

If you want use this part, please install zeep (`pip install zeep` or so).
Then make a service call to obtain a required parameter service_result
    client = zeep.Client("<wsdl>")
    service_result = client.service.method()

mtom_parse(service_result) will return a tuple of (root part, {attachments})

In both cases you will receive an attachment objects as results, not the file contents yet.
To get file content: attachment.content
To get file name   :
"""

def mtom_parse(service_result):
    """
    Will parse an incomming MTOM result into SOAP message and attached files.
    This just ensures that returned types are fixed,
        while the result from service is XmlResponse or MultiPack.

    https://www.w3.org/TR/SOAP-attachments
    https://docs.python-zeep.org/en/master/attachments.html

    Parameters:

        service_result   the result of zeep.Client("<wsdl>").service.method() call

    Result:

        tuple of (root part, {attachments})
            Each attachment (item in attachments) is: {<content-id>: <attachment object>}.
            To get the file content: <attachment object>.content

    Tip: To find attachment by <content-id> you can access the directory: attachments[<content-id>].
        But you can also use the zeep's function: service_result.get_by_content_id(<content-id>).
    """

    if hasattr(pack, "root"):
        if hasattr(pack, "attachments"):
            return pack.root, pack.attachments
        else:
            return pack.root, {}
    else:
        return pack, {}
