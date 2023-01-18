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
        files       list of paths to the attachment files
        mtom_placeholder    placeholder which will be replaced with the link to the attached binary file 

        The wsdl items having the attribute `xmime:expectedContentTypes`
            will be replaced with the link (xop:Include) to the mime attached file. 
        The count of files shoul be equal to the count of elements having `xmime:expectedContentTypes`.

    Example for `zeep` soap client:
        xmime:expectedContentTypes

    Result:

        message     finished mtom message, modified to contain attachments
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

        print(60*'+')
        print(response.text)

        return response


class MTOMTransport(zeep.Transport):
    files = []
    pushed_session = None

    def __init__(self, **kwargs):
        self.files = kwargs.pop("files", [])
        super().__init__(**kwargs)

    def post(self, address, message, headers):
        if self.files:
            message, update_headers = mtom_create(message, self.files)
            headers.update(update_headers)

        self.pushed_session = self.session  # push
        self.session = _PseudoSessionForInternalCallbackFromPost(self, message)

        # instead of call requests directly, it calls the callback, so we have chance to modify the requests parameters
        #   we need this, because .post() requires utf-8 encoded binary, but we need send a message with different, partially binary content
        response = super().post(address, str(message).encode(), headers)

        self.session = self.pushed_session  # pop

        return response
