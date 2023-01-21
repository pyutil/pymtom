import mimetypes
import zeep


BOUNDARY = b"- - - boundary - - - 8e54401e-ff36-413f-966a-295b3128a62f - - -"

# <xop:Include href="cid:1.B1150656.EC8A.4B5A.8835.A932E318190B" 
#               xmlns:xop="http://www.w3.org/2004/08/xop/include"/>

def mtom_create(message, files, cid_placeholder=b"cid:{cid}"):
    """
        Will create a MTOM message from SOAP message and attached files.

    Parameters:

        message     the completely prepared xml request message, without mtom attachments
                    with b"cid:{cid}" placeholders which will be replaced to <xop:Include..> elements
        files       list of paths to the attachment files
        cid_placeholder    default or explicit placeholder which will be replaced with the link to the attached binary file 

        The count of files should be equal to the count of elements having inner text b"cid:{cid}" (or explicit placeholder).

    Result:

        message     finished mtom message withou outer http headers, modified to contain attachments
        update_headers  outer headers (Content-Type, ..) which you should use to update headers
                    example: headers = {'SOAPAction': '""'}.update(update_headers)

    For `zeep` soap client: We have here a wrapping Transport class,
        use it as: transport=MTOMTransport(files=[path1, path2, ..])
    """

    # https://www.w3.org/Submission/soap11mtom10/

    update_headers = {
        'MIME-Version': '1.0',
        'Content-Type': f'multipart/related; type="application/xop+xml"; boundary="{BOUNDARY.decode()}"; start="0"; start-info="text/xml"',
    }
    boundary = b"--" + BOUNDARY + b'\n'
    mime_message = boundary

    mime_message += (
        b'Content-Type: application/xop+xml; type="text/xml"; charset="UTF-8"\n'  # application/xop+xml? text/xml? 
        b'Content-Transfer-Encoding: 8bit\n'
        b'Content-Id: 0\n\n'
    )

    for idx, file in enumerate(files):
        cid = idx + 1
        message = message.replace(
            cid_placeholder,
            f'<xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="cid:{cid}" />'.encode(),
            1   # replace first N=1 placeholder occurences
        )

    mime_message += message + b'\n'
    mime_message += boundary

    for idx, file in enumerate(files):
        cid = idx + 1
        mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
        mime_message += f'Content-Type: {mime_type}\n'.encode()
        mime_message += b'Content-Transfer-Encoding: binary\n'
        mime_message += f'Content-Id: {cid}\n\n'.encode()  # <{cid}> or cid:{cid} ?

        with open(file, "rb") as f:
            mime_message += f.read()
        mime_message += boundary

    return mime_message, update_headers


class _PseudoSessionForInternalCallbackFromPost:
    transport = None
    mtom_message = None

    def __init__(self, transport, mtom_message):
        self.transport = transport
        self.mtom_message = mtom_message

    def post(self, *args, **kwargs):
        kwargs["data"] = self.mtom_message
        response = self.transport.pushed_session.post(*args, **kwargs)
        # print(response.text)
        return response


class MTOMTransport(zeep.Transport):
    """
        MTOM support for outgoing message in Zeep.

		transport = MTOMTransport()
		client = zeep.Client(URL, transport=transport)
		params = {
			"fileName_1": "dark.png",
			"imageData_1": "cid:{cid}",  # will change to <xop:Include href="cid:1">
			"fileName_2": "light.png",
			"imageData_2": "cid:{cid}",  # will change to <xop:Include href="cid:2">
        }
		transport.add_files(files=["tmp/black.png", "tmp/white.png"])
		client.service.METHOD(**params)
    """
    files = []
    pushed_session = None

    def __init__(self, **kwargs):
        """
        You can stage files here already. But preffered is stage them via .add_files() 
        """
        self.files = kwargs.pop("files", [])
        super().__init__(**kwargs)

    def add_files(self, files):
        """
        files   list of files (pathnames) you want to attach during next service call
        """
        self.files = files

    def post(self, address, message, headers):
        if self.files:
            message, update_headers = mtom_create(message, self.files)
            headers.update(update_headers)
            self.files = []

        # we want to inherit the original method (super().post(..)) because it contains some wrapping logging
        #   but we have to modify the internal call; the trick makes a _PseudoSessionForInternalCallbackFromPost class and its .post() 
        self.pushed_session = self.session  # push
        self.session = _PseudoSessionForInternalCallbackFromPost(self, message)

        # instead of call requests directly, it calls the callback, so we have chance to modify the requests parameters
        #   we need this, because .post() requires utf-8 encoded binary, but we need send a message with different, partially binary content
        response = super().post(address, str(message).encode(), headers)

        self.session = self.pushed_session  # pop

        return response
